import unittest

from cement.utils import test

from ...__main__ import Zephyr
from ...tests.tests import TestZephyr

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
