import os

from ....cli.tests import TestZephyr, TestZephyrFixtures
from ...tests import TestZephyrParse

class TestZephyrDataParse(TestZephyrParse):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.assets = os.path.join(os.path.dirname(__file__), "assets")

    def test_service_requests(self):
        self.assert_equal_out("service_requests")

class TestZephyrDataParams(TestZephyrFixtures):

    def test_service_requests_params(self):
        module = "service-requests"
        TestZephyr.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)
