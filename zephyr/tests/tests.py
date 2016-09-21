import unittest
from cement.utils import test
from zephyr.__main__ import Zephyr

class TestingController(Zephyr):
    class Meta:
        argv = []
        config_files = []

class TestZephyr(test.CementTestCase):
    app_class = TestingController

    def test_zephyr(self):
        with self.app as app:
            app.run()
