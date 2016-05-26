import csv
import json

from core import CoreProcessor


def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = EC2RIRecommendations(json_string)
    return processor.write_csv(csv_filename)


class EC2RIRecommendations(CoreProcessor):
    def __init__(self, json_string):
        details = json.loads(json_string)
        self.parsed_details = {self._data_key(): []}

        for detail in details['BestPracticeChecks']:
            details_reader = csv.DictReader(
                detail[self._data_key()], self._fieldnames(), delimiter='|'
            )

            for row in details_reader:
                self.parsed_details[self._data_key()].append(row)

    def _filter_row(self, details_row):
        filtered_row = {
            key: (details_row[key]).replace("%s:" % key, '').strip()
            for key in self._fieldnames() if key in details_row.keys()
        }

        return self._format_money_fields(filtered_row)

    def _data_key(self):
        return 'Results'

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
