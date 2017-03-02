import os

from cement.utils import test

from ..cli.tests import TestZephyr
from .ddh import DDH

from .dy.calls import Billing
from .lo.calls import ServiceRequests
from .cc.calls import (
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    StorageDetachedWarp,
)

class TestZephyrParse(test.CementTestCase):
    app_class = TestZephyr
    assets = "."

    def assert_equal_out(self, module):
        modules = dict(
            billing=Billing,
            compute_details=ComputeDetailsWarp,
            compute_migration=ComputeMigrationWarp,
            compute_ri=ComputeRIWarp,
            compute_underutilized=ComputeUnderutilizedWarp,
            db_details=DBDetailsWarp,
            db_idle=DBIdleWarp,
            iam_users=IAMUsersData,
            lb_idle=LBIdleWarp,
            service_requests=ServiceRequests,
            storage_detached=StorageDetachedWarp,
        )

        module_name = module.replace("_", "-")
        infile = os.path.join(self.assets, "{}.json".format(module_name))
        outfile = os.path.join(self.assets, "{}.csv".format(module_name))

        with open(infile, "r") as f:
            response = f.read()
        warp = modules[module]()
        warp.parse(response)
        csv_out = warp.to_ddh().to_csv()
        trans_csv = csv_out.replace("\r\n", "")

        with open(outfile, "r") as f:
            gold_result = f.read()
        trans_gold = gold_result.replace("\n", "")
        self.eq(trans_csv, trans_gold)

class TestZephyrParseCache(TestZephyrParse):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.assets = os.path.join(os.path.dirname(__file__), "assets")

    def test_billing(self):
        self.assert_equal_out("billing")

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

    def test_service_requests(self):
        self.assert_equal_out("service_requests")
