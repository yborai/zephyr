from collections import defaultdict
from .ec2_migration_recommendations import EC2MigrationRecommencationsProcessor
import csv


def create_sheet(json_string, csv_filename='ec2_migration_recommendations.csv'):
    processor = EC2UnderutilizedInstancesBreakdowb(json_string)
    return processor.write_csv(csv_filename)


class EC2UnderutilizedInstancesBreakdowb(EC2MigrationRecommencationsProcessor):
    def write_csv(self, csv_filename):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            filtered_rows = (
                self._filter_row(details_row)
                for details_row in self.parsed_details[self._data_key()]
            )

            grouped_rows = self._group_rows(filtered_rows)

            writer.writeheader()
            for category in grouped_rows.keys():
                for row in grouped_rows[category]:
                    row.update({"Category": category})
                    writer.writerow(row)

                writer.writerow({})

        return csv_filename

    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])

        details_row["Category"] = details_row["Instance Name"].split("-")[0]

        return super()._filter_row(details_row)

    def _group_rows(self, filtered_rows):
        grouped_rows = defaultdict(list)
        for filtered_row in filtered_rows:
            grouped_rows[self._define_category(filtered_row["Category"])].append(filtered_row)

        return grouped_rows

    def _define_category(self, raw_category):
        if "prod" in raw_category:
            return "prod"
        if "mgmt" in raw_category:
            return "mgmt"
        if "stage" in raw_category or "staging" in raw_category:
            return "stage"

        return "other"

    def _fieldnames(self):
        return (
            "Category", "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )
