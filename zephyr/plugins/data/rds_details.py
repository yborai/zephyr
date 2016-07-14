from .common import ToolkitDataController
from .core import Sheet

from cement.core import controller

class ToolkitRdsDetails(ToolkitDataController):
    class Meta:
        label = "rds-details"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed rds meta information"

        arguments = ToolkitDataController.Meta.arguments + [(
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
            raise NotImplementedError #We will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        sheet = RDSDetailsSheet(response)
        self.app.render(sheet.get_data())

def create_sheet(json_string, csv_filename='rds_details.csv'):
    processor = RDSDetailsSheet(json_string)
    return processor.write_csv(csv_filename)


class RDSDetailsSheet(Sheet):
    def _data_key(self):
        return 'RdsDbInstances'

    def _filter_row(self, details_row):
        return {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

    def _fieldnames(self):
        return (
            'DbInstanceId', 'DbInstanceName', 'MonthlyCost', 'RegionName',
            'DbInstanceClass', 'Engine', 'EngineVersion', 'LicenseModel',
            'AllocatedStorageGB', 'FreeStorageSpaceBytes', 'Endpoint',
            'BackupRetentionPeriod'
        )
