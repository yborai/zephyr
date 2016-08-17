import csv

from cement.core import controller

from .common import ToolkitDataController

def data(cache="billing-line-items.csv"):
    with open(cache, "r") as f:
        reader = csv.DictReader(f)
        out = [reader.fieldnames] + [[row[col] for col in reader.fieldnames] for row in reader]
    return out

class ToolkitBillingLineItems(ToolkitDataController):
    class Meta:
        label = "billing-line-items"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the line items billing meta information."

        arguments = ToolkitDataController.Meta.arguments #+ [(
        #    ["--cache"], dict(
        #         type=str,
        #         help="The path to the cached response to use."
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
            reader = csv.DictReader(f)
            ddh = DDH(
                headers=reader.fieldnames,
                data=[list(row.values()) for row in reader]
            )
        self.app.render(ddh)
