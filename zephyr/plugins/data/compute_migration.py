import re

from cement.core import controller

from .core import RecommendationsWarp
from .common import DecimalEncoder
from .common import ToolkitDataController

class ToolkitComputeMigration(ToolkitDataController):
    class Meta:
        label = "compute-migration"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the migration recommendations meta information"

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
        warp = ComputeMigrationWarp(response)
        self.app.render(warp.to_ddh())


def create_sheet(json_string, csv_filename='compute-migration.csv'):
    processor = ComputeMigrationWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeMigrationWarp(RecommendationsWarp):
    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])

        return super()._filter_row(details_row)

    def _get_instance_id(self, instance_string):
        return instance_string.strip().split(' ')[0]

    def _get_instance_name(self, instance_string):
        regex = re.search('\((.*?)\)', instance_string)
        if regex is not None:
            return re.search('\((.*?)\)', instance_string).group(0)[1:-1]
        return ''

    def _instance_field(self):
        return "Instance"

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
