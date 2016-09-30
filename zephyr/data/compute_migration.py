from .core import SplitInstanceWarp

def create_sheet(json_string, csv_filename="compute-migration.csv"):
    processor = ComputeMigrationWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeMigrationWarp(SplitInstanceWarp):
    bpc_id = 240
    slug = "compute-migration"

    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=self.bpc_id)

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
