from datetime import datetime

from cement.core import controller

from .core import Sheet
from .common import ToolkitDataController

class ToolkitInstanceDetails(ToolkitDataController):
    class Meta:
        label = "instance_details"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the detailed instance meta information."
        
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
        sheet = EC2DetailsSheet(response)
        self.app.render(sheet.to_ddh())

def create_sheet(json_string, csv_filename="ec2_details.csv"):
    processor = EC2DetailsSheet(json_string)
    return processor.write_csv(csv_filename)


class EC2DetailsSheet(Sheet):
    def _data_key(self):
        return "Ec2Instances"

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

        return self._format_datefields(filtered_row)

    def _format_datefields(self, row):
        for field in self._datetime_fields():
            if(row[field] is None):
                continue
            row[field] = datetime.strptime(
                row[field], "%Y-%m-%dT%H:%M:%S"
            ).strftime("%m/%d/%y %H:%M")

        return row

    def _fieldnames(self):
        return (
            "InstanceId", "InstanceName", "Status", "Region", "PricingPlatform",
            "InstanceType", "LaunchTime", "AvgCpuforLast7Days", "AvgCpuforLast30Days",
            "AvgCpuforLast90Days", "AvgNetworkInLast30Days", "AvgNetworkOutLast30Days",
            "HighCpuPercent", "LowCpuPercent", "HoursCpuUtilAbove80", "HoursCpuUtilBelow80",
            "HoursCpuUtilBelow60", "HoursCpuUtilBelow40", "HoursCpuUtilBelow20",
            "HoursHighCpuLast7Days", "HoursHighCpuLast30Days", "HoursHighCpuLast90Days",
            "HoursLowCpuLast7Days", "HoursLowCpuLast30Days", "HoursRunningLast7Days",
            "HoursRunningLast30Days", "HoursRunningLast90Days", "MinimumCpuUtilization",
            "MinimumCpuUtilizationDateTime", "PeakCpuUtilization", "PeakCpuUtilizationDateTime"
        )

    def _datetime_fields(self):
        return (
            "MinimumCpuUtilizationDateTime", "PeakCpuUtilizationDateTime", "LaunchTime"
        )
