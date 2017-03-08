import os

from cement.utils import test

from ..cli.tests import TestZephyr, TestZephyrFixtures
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
from .cc.sheets import SheetEC2, SheetUnderutilized
from .utils import first_of_previous_month


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


class TestZephyrReportParse(TestZephyrParse):

    def test_get_launch_times(self):
        with self.app_class() as app:
            app.configure()
            config = app.config
        header = ["Status", "LaunchTime"]
        data = [
            ["running", "02/06/17 02:50"],
            ["stopped", "02/06/17 02:50"],
            ["running", "10/06/16 02:50"],
            ["stopped", "10/06/16 02:50"],
            ["running", "07/06/16 02:50"],
            ["stopped", "07/06/16 02:50"],
            ["running", "01/06/16 02:50"],
            ["stopped", "01/06/16 02:50"]
        ]
        launch_times_ = [
            "02/06/17 02:50",
            "10/06/16 02:50",
            "07/06/16 02:50",
            "01/06/16 02:50"
        ]
        days_90_ = 1
        days_180_ = 1
        days_270_ = 1
        test_result = launch_times_, days_90_, days_180_, days_270_
        ec2 = SheetEC2(config, date="2017-03-01")
        ec2._ddh = DDH(header=header, data=data)
        sheet_result = ec2.get_launch_times()
        self.eq(sheet_result, test_result)


class TestZephyrParseFixtures(TestZephyrFixtures):

    def test_underutilized_join(self):
        with self.app_class() as app:
            app.configure()
            config = app.config
            log = app.log
        date = first_of_previous_month().strftime("%Y-%m-%d")
        header = [
            'InstanceId',
            'InstanceName',
            'Environment',
            'Average CPU Util',
            'Predicted Monthly Cost'
        ]
        data = [
            ['i-0272f78b', 'AVID-TESTING-SSO-HAP01', '', '0.15%', '84.48']
        ]
        uu = SheetUnderutilized(config, account=".meta", date=date, log=log)
        sheet_ddh = uu.ddh
        self.eq(sheet_ddh.data, data)
        self.eq(sheet_ddh.header, header)
