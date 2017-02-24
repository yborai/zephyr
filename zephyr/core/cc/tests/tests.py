import os

from ....cli.tests import TestZephyr, TestZephyrFixtures
from ...tests import TestZephyrParse

class TestZephyrDataParse(TestZephyrParse):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.assets = os.path.join(os.path.dirname(__file__), "assets")

    def test_compute_details(self):
        self.assert_equal_out("compute_details")

    def test_compute_migration(self):
        self.assert_equal_out("compute_migration")

    def test_compute_ri(self):
        self.assert_equal_out("compute_ri")

    def test_compute_underutilized(self):
        self.assert_equal_out("compute_underutilized")

    def test_db_details(self):
        self.assert_equal_out("db_details")

    def test_db_idle(self):
        self.assert_equal_out("db_idle")

    def test_iam_users(self):
        self.assert_equal_out("iam_users")

    def test_lb_idle(self):
        self.assert_equal_out("lb_idle")

    def test_storage_detached(self):
        self.assert_equal_out("storage_detached")

class TestZephyrDataParams(TestZephyrFixtures):

    def test_compute_details_params(self):
        module = "compute-details"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_compute_migration_params(self):
        module = "compute-migration"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_compute_ri_params(self):
        module = "compute-ri"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_db_details_params(self):
        module = "db-details"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_db_idle_params(self):
        module = "db-idle"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_iam_users_params(self):
        module = "iam-users"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_lb_idle_params(self):
        module = "lb-idle"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)

    def test_storage_detached_params(self):
        module = "storage-detached"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)
