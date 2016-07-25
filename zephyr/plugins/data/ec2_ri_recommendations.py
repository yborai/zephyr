import json

from cement.core import controller

from .recommendations_core import RecommendationsSheet

import decimal

from .common import DecimalEncoder

from .common import ToolkitDataController

class ToolkitEC2RIRecommendations(ToolkitDataController):
    class Meta:
        label = "ri-recommendations"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the ri recommendations meta information."

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
        sheet = EC2RIRecommendationsSheet(response)
        sheet_data = sheet.get_data()
        self.app.render(sheet_data, cls=DecimalEncoder)




def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = EC2RIRecommendationsSheet(json_string)
    return processor.write_csv(csv_filename)


class EC2RIRecommendationsSheet(RecommendationsSheet):
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
