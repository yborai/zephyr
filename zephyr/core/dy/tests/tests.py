import os

from ....cli.tests import get_db_path, TestZephyr, TestZephyrFixtures
from ...utils import first_of_previous_month
from ...tests import TestZephyrParse

class TestZephyrDataParse(TestZephyrParse):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.assets = os.path.join(os.path.dirname(__file__), "assets")

    def test_billing_line_items(self):
        self.assert_equal_out("billing")

class TestZephyrDataParams(TestZephyrFixtures):

    def assert_successful_run(self, obj, args, module):
        with TestZephyr(argv=args) as app:
            app.configure()
            app.run()
            data, output = app.last_rendered
        trans_out = output.replace("\r\n", "")

        cache_root = os.path.dirname(get_db_path())
        date = first_of_previous_month().strftime("%Y-%m")
        gold_csv = os.path.join(cache_root, date, "billing.csv")
        with open(gold_csv, "r") as f:
            gold_result = f.read()
        trans_gold = gold_result.replace("\n", "")
        obj.eq(trans_out, trans_gold)

    def test_billing_line_items_params(self):
        module = "billing-line-items"
        self.assert_successful_run(self, [
            "data",
            module,
            "--account=.meta",
            "-o",
            "csv",
        ], module)
