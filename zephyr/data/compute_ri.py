from cement.core import controller

from ..cli.controllers import ZephyrData
from .core import RecommendationsWarp
from .common import DecimalEncoder

class ZephyrComputeRI(ZephyrData):
    class Meta:
        label = "compute-ri"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the ri recommendations meta information."

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
        warp = ComputeRIWarp(response)
        self.app.render(warp.to_ddh(), cls=DecimalEncoder)


def create_sheet(json_string, csv_filename='compute-ri.csv'):
    processor = ComputeRIWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeRIWarp(RecommendationsWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=190)

    def _fieldnames(self):
        return (
            "Number", "Instance Type", "AZ", "Platform", "Commitment Type",
            "Tenancy", "Upfront RI Cost", "Reserved Monthly Cost",
            "On-Demand Monthly Cost", "Total Savings"
        )

    def _money_fields(self):
        return (
            "Upfront RI Cost", "Reserved Monthly Cost",
            "On-Demand Monthly Cost", "Total Savings"
        )
