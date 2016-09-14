from .common import DecimalEncoder
from .core import SplitInstanceWarp

def create_sheet(json_string, csv_filename='compute-underutilized.csv'):
    processor = ComputeUnderutilizedWarp(json_string)
    return processor.write_csv(csv_filename)

class ComputeUnderutilizedWarp(SplitInstanceWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=68)

    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
