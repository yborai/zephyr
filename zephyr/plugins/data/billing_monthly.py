import csv
import json

from cement.core import controller

from .common import DDH, ToolkitDataController

class ToolkitBillingMonthly(ToolkitDataController):
    class Meta:
        label = "billing-monthly"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the monthly billing meta information."

        arguments = ToolkitDataController.Meta.arguments #+ [(
            #["--cache"], dict(
            #     type=str,
            #     help="The path to the cached response to use."
            #)
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
            header = reader.fieldnames
            data = [[row[col] for col in header] for row in reader]
        out = DDH(headers=header, data=data)
        self.app.render(out)
        return out

def create_sheet(table):
    processor = BillingMonthlySheet(json_string)
    return processor.write_csv(csv_filename)
