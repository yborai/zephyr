from .core import BestPracticesWarp

def create_sheet(json_string, csv_filename="db-idle.csv"):
    processor = DBIdleWarp(json_string)
    return processor.write_csv(csv_filename)

class DBIdleWarp(BestPracticesWarp):
    bpc_id = 134
    slug = "db-idle"

    def _fieldnames(self):
        return (
            "DB Instance",
            "Average Read IOPS",
            "Average Write IOPS",
            "Predicted Monthly Cost",
            "Region",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
