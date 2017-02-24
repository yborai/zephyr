import os
import sqlite3
import shutil

import pandas as pd

from cement.utils import test

from ..__main__ import Zephyr
from ..core.book import Book
from ..core.cc.sheets import SheetEC2, SheetRDS
from ..core.dy.sheets import SheetBilling
from ..core.lo.sheets import SheetSRs
from ..core.fixtures import fixtures
from ..core.utils import (
    first_of_previous_month,
    get_config_values,
    ZephyrException
)


def get_db_path():
    with Zephyr() as app:
        app.configure()
        config = app.config
    zephyr_config_keys = ("ZEPHYR_CACHE_ROOT", "ZEPHYR_DATABASE")
    cache_root, db = [
        os.path.expanduser(path)
        for path in get_config_values("zephyr", zephyr_config_keys, config)
    ]
    return os.path.join(cache_root, db)


class TestZephyr(Zephyr):
    class Meta:
        argv = []

    @classmethod
    def assert_zephyr_success(cls, obj, args):
        with cls(argv=args) as app:
            app.configure()
            with obj.assertRaises(SystemExit) as cm:
                app.run()
            obj.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    @classmethod
    def assert_zephyr_expected_failure(cls, obj, args):
        with cls(argv=args) as app:
            app.configure()
            with obj.assertRaises(ZephyrException) as exc:
                app.run()
            obj.eq(
                True
                and len(exc.exception.args) > 0
                and bool(exc.exception.args[0]),
                True,
                msg="Expected an appropriate error message."
            )

    @classmethod
    def assert_successful_run(cls, obj, args, module):
        with cls(argv=args) as app:
            app.configure()
            app.run()
            data, output = app.last_rendered
        trans_out = output.replace("\r\n", "")

        cache_root = os.path.dirname(get_db_path())
        date = first_of_previous_month().strftime("%Y-%m")
        gold_csv = os.path.join(cache_root, date, "{}.csv".format(module))
        with open(gold_csv, "r") as f:
            gold_result = f.read()
        trans_gold = gold_result.replace("\n", "")
        obj.eq(trans_out, trans_gold)

class TestZephyrSheet(test.CementTestCase):
    app_class = TestZephyr
    sheet = None

    def setUp(self):
        with self.app_class() as app:
            app.configure()
            config = app.config
            log = app.log
        self.sheet = SheetEC2(config, ".meta", "2001-01-01", None, log=log)

    def tearDown(self):
        # See comment in TestZephyrBook
        pass

    def test_sheet_clients(self):
        assert len(self.sheet.clients) == len(self.sheet.calls)

    def test_sheet_header_format(self):
        assert (
            self.sheet.header_format_xlsx(["col1", "col2"], "fmt", []) ==
            [
                {'header_format': 'fmt', 'header': 'col1'},
                {'header_format': 'fmt', 'header': 'col2'}
            ]
        )

class TestZephyrBook(test.CementTestCase):
    app_class = TestZephyr
    book = None

    def setUp(self):
        with self.app_class() as app:
            app.configure()
            config = app.config
            log = app.log
        self.book = Book(
            config,
            "Test",
            (SheetEC2, SheetRDS, SheetBilling, SheetSRs),
            ".meta",
            None,
            None,
            log=log
        )

    def tearDown(self):
        """
        Cement uses temp files in its default tests, and the references
        will not exist if setUp is overridden and will break when
        tearDown is called. A short-term fix is to override tearDown as
        well. The long-term fix will be to use CementTestCase more like
        the authors of Cement intended.
        """
        pass

    def test_book_validators(self):
        assert len(self.book.slug_validators()) == 3

    def test_book_validators_fail(self):
        assert (
            self.book.cache_key("slug", "account", "2001-01-01") ==
            "account/2001-01/slug.xlsx"
        )


class TestZephyrFixtures(test.CementTestCase):
    app_class = TestZephyr

    @classmethod
    def _delete_fixtures(cls, cur):
        for table in fixtures.keys():
            cur.execute("""
                DELETE FROM {} WHERE "index" IN (-1, -2)
            """.format(table))

    @classmethod
    def _load_fixtures(cls, cur):
        for table in fixtures:
            fixture = fixtures[table]
            pd.DataFrame(
                list(fixture["data"]),
                columns=fixture["header"]
            ).to_sql(
                table,
                cur.connection,
                if_exists="append",
                index=False,
            )

    @classmethod
    def copy_assets(cls):
        core_path = os.path.join(os.path.dirname(__file__), "..", "core")
        cc_assets = os.path.join(core_path, "cc", "tests", "assets")
        dy_assets = os.path.join(core_path, "dy", "tests", "assets")
        lo_assets = os.path.join(core_path, "lo", "tests", "assets")
        all_assets = [cc_assets, dy_assets, lo_assets]
        cache_root = os.path.dirname(get_db_path())
        date = first_of_previous_month().strftime("%Y-%m")
        asset_cache = os.path.join(cache_root, date)
        os.makedirs(asset_cache, exist_ok=True)
        for assets in all_assets:
            for asset in os.listdir(assets):
                shutil.copy2(os.path.join(assets, asset), asset_cache)

    @classmethod
    def setUpClass(cls):
        with sqlite3.connect(get_db_path()) as con:
            try:
                cls._delete_fixtures(con.cursor())
            except sqlite3.OperationalError as e:
                """
                This error can be thrown if the database exists but has
                no data. In this case there is nothing to delete.
                """
                pass
            cls._load_fixtures(con.cursor())
        cls.copy_assets()

    @classmethod
    def tearDownClass(cls):
        with sqlite3.connect(get_db_path()) as con:
            cls._delete_fixtures(con.cursor())

class TestZephyrFixturesCalls(TestZephyrFixtures):

    def test_account_unrecognized(self):
        TestZephyr.assert_zephyr_expected_failure(self, [
            "report",
            "account-review",
            "--account=..",
        ])

    def test_account_account_review_no_dynamics(self):
        TestZephyr.assert_zephyr_expected_failure(self, [
            "report",
            "account-review",
            "--account=.no_dynamics",
        ])

    def test_account_billing_no_dynamics(self):
        TestZephyr.assert_zephyr_expected_failure(self, [
            "report",
            "billing",
            "--account=.no_dynamics",
        ])

class TestZephyrBase(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr(self):
        with self.app as app:
            app.configure()
            app.run()


class TestZephyrData(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr_data(self):
        with TestZephyr(argv=["data"]) as app:
            app.configure()
            app.run()

    def test_billing_monthly(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "billing-monthly",
            "--help",
        ])

    def test_billing_line_items(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "billing-line-items",
            "--help",
        ])

    def test_billing_line_item_aggregates(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "billing-line-item-aggregates",
            "--help",
        ])

    def test_compute_av(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute-av",
            "--help",
        ])

    def test_compute_details(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute-details",
            "--help",
        ])

    def test_compute_migration(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute-migration",
            "--help",
        ])

    def test_compute_ri(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute-ri",
            "--help",
        ])

    def test_compute_underutilized(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute-underutilized",
            "--help",
        ])

    def test_compute_underutilized_breakdown(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "compute_underutilized_breakdown",
            "--help",
        ])

    def test_db_details(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "db-details",
            "--help",
        ])

    def test_db_idle(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "db-idle",
            "--help",
        ])

    def test_domains(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "domains",
            "--help",
        ])

    def test_iam_users(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "iam-users",
            "--help",
        ])

    def test_lb_idle(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "lb-idle",
            "--help",
        ])

    def test_ri_pricings(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "ri-pricings",
            "--help",
        ])

    def test_service_requests(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "service-requests",
            "--help",
        ])

    def test_storage_detached(self):
        TestZephyr.assert_zephyr_success(self, [
            "data",
            "storage-detached",
            "--help",
        ])


class TestZephyrETL(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr_etl(self):
        with TestZephyr(argv=["etl"]) as app:
            app.configure()
            app.run()

    def test_dbr_ri(self):
        TestZephyr.assert_zephyr_success(self, [
            "etl",
            "dbr-ri",
            "--help",
        ])


class TestZephyrReport(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr_report(self):
        with TestZephyr(argv=["report"]) as app:
            app.configure()
            app.run()

    def test_account_review(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "account-review",
            "--help",
        ])

    def test_ec2(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "ec2",
            "--help",
        ])

    def test_rds(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "rds",
            "--help",
        ])

    def test_ri_recs(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "ri-recs",
            "--help",
        ])

    def test_sr(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "sr",
            "--help",
        ])
