from .recommendations_core import RecommendationsCoreProcessor
import re


def create_sheet(json_string, csv_filename='ec2_migration_recommendations.csv'):
    processor = EC2MigrationRecommencationsProcessor(json_string)
    return processor.write_csv(csv_filename)


class EC2MigrationRecommencationsProcessor(RecommendationsCoreProcessor):
    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])

        return super()._filter_row(details_row)

    def _get_instance_id(self, instance_string):
        return instance_string.strip().split(' ')[0]

    def _get_instance_name(self, instance_string):
        return re.search('\((.*?)\)', instance_string).group(0)[1:-1]

    def _instance_field(self):
        return "Instance"

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
