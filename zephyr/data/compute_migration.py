from cement.core import controller

from ..cli.controllers import ZephyrData
from .core import SplitInstanceWarp
from .common import DecimalEncoder

class ZephyrComputeMigration(ZephyrData):
    class Meta:
        label = "compute-migration"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the migration recommendations meta information"

        arguments = ZephyrData.Meta.arguments #+ [(
        #    ["--cc_api_key"], dict(
        #        type=str,
        #        help="The CloudCheckr API key to use."
        #    )
        #)]

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))
     
    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We will add fetching later.
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeMigrationWarp(response)
        self.app.render(warp.to_ddh())


def create_sheet(json_string, csv_filename='compute-migration.csv'):
    processor = ComputeMigrationWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeMigrationWarp(SplitInstanceWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=240)

    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Region", "Recommendation",
            "On-Demand Current Monthly Cost", "Cost for Recommended",
            "Yearly Savings", "Platform", "vCPU for current",
            "vCPU for next gen", "Memory for current", "Memory for next gen"
        )

    def _money_fields(self):
        return (
            "On-Demand Current Monthly Cost", "Cost for Recommended", "Yearly Savings"
        )
