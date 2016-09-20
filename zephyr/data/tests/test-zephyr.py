import unittest
from cement.utils import test
from zephyr.__main__ import Zephyr

class TestingController(Zephyr):
    class Meta:
        argv = []
        config_files = []

class TestZephyr(test.CementTestCase):
    app_class = TestingController

    def test_myapp_default(self):
        with self.app as app:
            app.run()

    def test_second_default(self):
        with TestingController(argv=["data"]) as app:
            app.run()