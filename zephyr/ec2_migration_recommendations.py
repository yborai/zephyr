from .ec2_ri_recommendations import EC2RIRecommendationsProcessor


def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = EC2MigrationRecommencationsProcessor(json_string)
    return processor.write_csv(csv_filename)


class EC2MigrationRecommencationsProcessor(EC2RIRecommendationsProcessor):
    def _fieldnames(self):
        return (
            "Instance", "Region", "Recommendation", "On-Demand Current Monthly Cost",
            "Cost for Recommended", "Yearly Savings", "Platform", "vCPU for current",
            "vCPU for next gen", "Memory for current", "Memory for next gen"
        )

    def _money_fields(self):
        return (
            "On-Demand Current Monthly Cost", "Cost for Recommended", "Yearly Savings"
        )
