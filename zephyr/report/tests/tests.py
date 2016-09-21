import unittest

from cement.utils import test

from ...__main__ import Zephyr
from ...tests.tests import TestZephyr

class TestZephyrReport(test.CementTestCase):
    app_class = TestZephyr

    def test_zephyr_report(self):
        with TestZephyr(argv=["report"]) as app:
            app.run()

    def test_dbr_ri(self):
        TestZephyr.assert_zephyr_success(self, [
            "report",
            "account-review",
            "--help",
        ])
