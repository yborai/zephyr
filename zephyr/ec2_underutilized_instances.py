from .ec2_migration_recommendations import EC2MigrationRecommencationsProcessor


def create_sheet(json_string, csv_filename='ec2_underutilized_instances.csv'):
    processor = EC2UnderutilizedInstances(json_string)
    return processor.write_csv(csv_filename)


class EC2UnderutilizedInstances(EC2MigrationRecommencationsProcessor):
    def _fieldnames(self):
        return (
            "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
