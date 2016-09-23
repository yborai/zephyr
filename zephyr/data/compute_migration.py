from .core import SplitInstanceWarp

def create_sheet(json_string, csv_filename='compute-migration.csv'):
    processor = ComputeMigrationWarp(json_string)
    return processor.write_csv(csv_filename)


class ComputeMigrationWarp(SplitInstanceWarp):
    def __init__(self, json_string):
        self.bpc_id = self.get_bpc_id()
        self.slug = self.get_bpc_id()
        self.uri = self.get_uri()
        super().__init__(json_string, bpc_id=self.bpc_id)

    @staticmethod
    def get_bpc_id():
        return 240

    @classmethod
    def get_params(cls, api_key, name, date):
        return dict(
            access_key=api_key,
            bpc_id=cls.get_bpc_id(),
            date=date,
            use_account=name,
        )

    @staticmethod
    def get_slug():
        return "compute-migration"

    @staticmethod
    def get_uri():
        return "best_practice.json/get_best_practices"

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
