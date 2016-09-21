import unittest
from cement.utils import test
from zephyr.__main__ import Zephyr

class TestingController(Zephyr):
    class Meta:
        argv = []
        config_files = []

class TestDataCommands(test.CementTestCase):
    app_class = TestingController

    def test_zephyr_data(self):
        with TestingController(argv=["data"]) as app:
            app.run()

    def test_billing_monthly(self):
        with TestingController(argv=[
            "data",
            "billing-monthly",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_billing_line_items(self):
        with TestingController(argv=[
            "data",
            "billing-line-items",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_billing_line_item_aggregates(self):
        with TestingController(argv=[
            "data",
            "billing-line-item-aggregates",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_av(self):
        with TestingController(argv=[
            "data",
            "compute-av",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_details(self):
        with TestingController(argv=[
            "data",
            "compute-details",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_migration(self):
        with TestingController(argv=[
            "data",
            "compute-migration",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_ri(self):
        with TestingController(argv=[
            "data",
            "compute-ri",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_underutilized(self):
        with TestingController(argv=[
            "data",
            "compute-underutilized",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_compute_underutilized_breakdown(self):
        with TestingController(argv=[
            "data",
            "compute_underutilized_breakdown",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_db_details(self):
        with TestingController(argv=[
            "data",
            "db-details",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_db_idle(self):
        with TestingController(argv=[
            "data",
            "db-idle",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_domains(self):
        with TestingController(argv=[
            "data",
            "domains",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_iam_users(self):
        with TestingController(argv=[
            "data",
            "iam-users",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_lb_idle(self):
        with TestingController(argv=[
            "data",
            "lb-idle",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_ri_pricings(self):
        with TestingController(argv=[
            "data",
            "ri-pricings",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_service_requests(self):
        with TestingController(argv=[
            "data",
            "service-requests",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    def test_storage_detached(self):
        with TestingController(argv=[
            "data",
            "storage-detached",
            "--help",
        ]) as app:
            with self.assertRaises(SystemExit) as cm:
                app.run()
            self.eq(cm.exception.code, 0, msg="Expected to return SystemExit: 0")

    