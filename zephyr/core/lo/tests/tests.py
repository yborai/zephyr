import os

from ...tests import TestZephyrParams

class TestZephyrDataParams(TestZephyrParams):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.assets = os.path.join(os.path.dirname(__file__), "assets")

    def test_service_requests(self):
        self.assert_equal_out("service_requests")
