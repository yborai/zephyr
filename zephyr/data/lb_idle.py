from .core import RecommendationsWarp

def create_sheet(json_string, csv_filename='lb-idle.csv'):
    processor = LBIdleWarp(json_string)
    return processor.write_csv(csv_filename)

class LBIdleWarp(RecommendationsWarp):
    def __init__(self, json_string):
        super().__init__(json_string, bpc_id=126)

    def _fieldnames(self):
        return (
            "Load Balancer",
            "Average Hourly Request Count",
            "Predicted Monthly Cost",
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
