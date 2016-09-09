from cement.core import controller

from ..cli.controllers import ZephyrData
from .core import Warp

class ZephyrDBDetails(ZephyrData):
    class Meta:
        label = "db-details"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed rds meta information"

        arguments = ZephyrData.Meta.arguments #+ [(
            #["--cc_api_key"], dict(
            #    type=str,
            #    help="The CloudCheckr API key to use."
            #)
        #)]

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
        warp = DBDetailsWarp(response)
        self.app.render(warp.to_ddh())

def create_sheet(json_string, csv_filename='db-details.csv'):
    processor = DBDetailsWarp(json_string)
    return processor.write_csv(csv_filename)


class DBDetailsWarp(Warp):
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
