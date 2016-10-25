from datetime import datetime

from .core import Warp

def create_sheet(json_string, csv_filename="compute-details.csv"):
    processor = ComputeDetailsWarp(json_string)
    return processor.write_csv(csv_filename)

class ComputeDetailsWarp(Warp):
    slug = "compute-details"
    uri = "inventory.json/get_resources_ec2_details"

    def _key(self):
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
            "InstanceId",
            "InstanceName",
            "PrivateIpAddress",
            "Status",
            "Region",
            "PricingPlatform",
            "InstanceType",
            "LaunchTime"
        )

    def _datetime_fields(self):
        return ("LaunchTime",)
