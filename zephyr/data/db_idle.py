from .core import RecommendationsWarp

def create_sheet(json_string, csv_filename='db-idle.csv'):
    processor = DBIdleWarp(json_string)
    return processor.write_csv(csv_filename)

class DBIdleWarp(RecommendationsWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=134)

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
