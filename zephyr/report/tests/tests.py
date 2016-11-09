import unittest

from cement.utils import test

from ...__main__ import Zephyr
from ...tests.tests import TestZephyr

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
