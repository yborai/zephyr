import json
from .recommendations_core import RecommendationsCoreProcessor


def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = EC2RIRecommendationsProcessor(json_string)
    return processor.write_csv(csv_filename)


class EC2RIRecommendationsProcessor(RecommendationsCoreProcessor):
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
