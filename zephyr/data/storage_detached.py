from cement.core import controller

from ..cli.controllers import ZephyrData
from .core import RecommendationsWarp

class ZephyrStorageDetached(ZephyrData):
    class Meta:
        label = "storage-detached"
        stacked_on = "data"
        stacked_type = "nested"
        description = "List detached storage volumes."

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
        warp = StorageDetachedWarp(response)
        self.app.render(warp.to_ddh())


def create_sheet(json_string, csv_filename='storage-detached.csv'):
    processor = StorageDetachedWarp(json_string)
    return processor.write_csv(csv_filename)


class StorageDetachedWarp(RecommendationsWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=1)

    def _fieldnames(self):
        return (
            "Volume ID",
            "Size",
            "Predicted Monthly Cost",
            "EC2 Instance",
            "Region",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
