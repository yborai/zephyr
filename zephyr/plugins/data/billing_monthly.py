import json

from cement.core import controller

class ToolkitBillingMonthly(controller.CementBaseController):
    class Meta:
        label = "billing-monthly"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the monthly billing meta information."

        arguments = controller.CementBaseController.Meta.arguments + [(
            ["--cc_api_key"], dict(
                type=str,
                help="The CloudCheckr API key to use."
            )
        ), (
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
        sheet = BillingMonthlySheet(response)
        self.app.render(sheet.get_data())



def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = BillingMonthlySheet(json_string)
    return processor.write_csv(csv_filename)


'''class BillingMonthlySheet(Sheet):
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
'''