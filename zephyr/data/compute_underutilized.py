from cement.core import controller

from ..cli.controllers import ZephyrData
from .common import DecimalEncoder
from .core import SplitInstanceWarp

class ZephyrComputeUnderutilized(ZephyrData):
    class Meta:
        label = "compute-underutilized"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the underutilized instance meta information"

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
            raise NotImplementedError # We'll add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeUnderutilizedWarp(response)
        self.app.render(warp.to_ddh())

def create_sheet(json_string, csv_filename='compute-underutilized.csv'):
    processor = ComputeUnderutilizedWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeUnderutilizedWarp(SplitInstanceWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=68)

    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
