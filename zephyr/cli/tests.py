from cement.utils import test

from ..__main__ import Zephyr

class TestZephyr(Zephyr):
    class Meta:
        argv = []

    @classmethod
    def assert_zephyr_success(cls, obj, args):
        with cls(argv=args) as app:
            with obj.assertRaises(SystemExit) as cm:
                app.run()
            obj.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

class TestZephyrBase(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr(self):
        with self.app as app:
            app.run()

class TestZephyrData(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr_data(self):
        with TestZephyr(argv=["data"]) as app:
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
