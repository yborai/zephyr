import os
import sqlite3

import pandas as pd

from cement.utils import test

from ..__main__ import Zephyr
from ..core.book import Book
from ..core.cc.sheets import SheetEC2, SheetRDS
from ..core.dy.sheets import SheetBilling
from ..core.lo.sheets import SheetSRs
from ..core.configure import CRED_ITEMS, DEFAULTS
from ..core.fixtures import fixtures
from ..core.utils import get_config_values, ZephyrException

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
            obj.eq(True
                and len(exc.exception.args)>0
                and bool(exc.exception.args[0]),
                True,
                msg="Expected an appropriate error message."
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

    @classmethod
    def tearDownClass(cls):
        with sqlite3.connect(get_db_path()) as con:
            cls._delete_fixtures(con.cursor())

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
