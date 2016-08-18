from cement.core import controller

from .core import RecommendationsWarp
from .common import ToolkitDataController

class ToolkitLBIdle(ToolkitDataController):
    class Meta:
        label = "lb-idle"
        stacked_on = "data"
        stacked_type = "nested"
        description = "List idle load balancers."

        arguments = ToolkitDataController.Meta.arguments #+ [(
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
        warp = LBIdleWarp(response)
        self.app.render(warp.to_ddh())


def create_sheet(json_string, csv_filename='lb-idle.csv'):
    processor = LBIdleWarp(json_string)
    return processor.write_csv(csv_filename)


class LBIdleWarp(RecommendationsWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=126)

    def _fieldnames(self):
        return (
            "Load Balancer",
            "Average Hourly Request Count",
            "Predicted Monthly Cost",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
