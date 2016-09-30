from cement.core import controller

from .core import BestPracticesWarp

def create_sheet(json_string, csv_filename="compute-ri.csv"):
    processor = ComputeRIWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeRIWarp(BestPracticesWarp):
    bpc_id = 190
    slug = "compute-ri"

    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=self.bpc_id)

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
