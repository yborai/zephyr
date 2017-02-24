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
    RIPricingWarp,
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
            ri_pricings=RIPricingWarp,
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
