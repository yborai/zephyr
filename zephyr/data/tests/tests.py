import os
import unittest

from cement.utils import test

from ...__main__ import Zephyr

from ...core.boto.calls import domains
from ...core.cc.calls import (
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    ComputeUnderutilizedBreakdownWarp,
    DBDetailsWarp,
    DBIdleWarp,
    IAMUsersData,
    LBIdleWarp,
    RIPricingWarp,
    StorageDetachedWarp,
)
from ...core.ddh import DDH
from ...core.lo.calls import ServiceRequests
from ...tests.tests import TestZephyr

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
    
class TestZephyrDataParams(test.CementTestCase):
    app_class = TestZephyr

    def assert_equal_out(self, module):
        modules = dict(
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

        files = os.path.join(os.path.dirname(__file__), "assets")

        infile = os.path.join(files, "{}_single.json".format(module))
        outfile = os.path.join(files, "{}_gold.csv".format(module))


        with open(infile, "r") as f:
            response = f.read()
        warp = modules[module](json_string=response)
        csv_out = warp.to_ddh().to_csv()
        trans_csv = csv_out.replace("\r\n", "")

        with open(outfile, "r") as f:
            gold_result = f.read()
        trans_gold = gold_result.replace("\n", "")
        self.eq(trans_csv, trans_gold)

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

    def test_service_requests(self):
        self.assert_equal_out("service_requests")

    def test_storage_detached(self):
        self.assert_equal_out("storage_detached")

