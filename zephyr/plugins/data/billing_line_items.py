import csv
import json

from cement.core import controller

from .common import ToolkitDataController

def data(cache="billing-line-items.csv"):
    with open(cache, "r") as f:
        reader = csv.DictReader(f)
        #import pdb;pdb.set_trace()
        out = [reader.fieldnames] + [list(row.values()) for row in reader]
    return out

class ToolkitBillingLineItems(controller.CementBaseController):
    class Meta:
        label = "billing-line-items"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the line items billing meta information."

        arguments = controller.CementBaseController.Meta.arguments + [(
            ["--cache"], dict(
                 type=str,
                 help="The path to the cached response to use."
            )
        )]
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
        sheet = BillingLineItemsSheet(response)
        self.app.render(sheet.get_data())

def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = BillingLineItemsSheet(json_string)
    return processor.write_csv(csv_filename)
