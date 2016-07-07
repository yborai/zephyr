from .ec2_migration_recommendations import EC2MigrationRecommendationsSheet

from cement.core import controller

from .common import DecimalEncoder

class ToolkitEC2UnderutilizedInstances(controller.CementBaseController):
    class Meta:
        label = "underutilized-instances"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the underutilized instance meta information"

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
            raise NotImplementedError # We'll add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
#        import pdb; pdb.set_trace()
        with open(cache, "r") as f:
            response = f.read()
        sheet = EC2UnderutilizedInstancesSheet(response)
        sheet_data = sheet.get_data()
        self.app.render(sheet_data, cls=DecimalEncoder)

def create_sheet(json_string, csv_filename='ec2_underutilized_instances.csv'):
    processor = EC2UnderutilizedInstancesSheet(json_string)
    return processor.write_csv(csv_filename)


class EC2UnderutilizedInstancesSheet(EC2MigrationRecommendationsSheet):
    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
