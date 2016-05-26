import json
from .core import CoreProcessor


def create_sheet(json_string, csv_filename='ec2_ri_recommendations.csv'):
    processor = EC2RIRecommendationsProcessor(json_string)
    return processor.write_csv(csv_filename)


class EC2RIRecommendationsProcessor(CoreProcessor):
    def __init__(self, json_string):
        raw_details = json.loads(self._escape_json_string(json_string))

        parsed_data = []
        for raw_detail_row in raw_details['BestPracticeChecks']:
            for raw_data in raw_detail_row[self._data_key()]:
                parsed_data.append(
                    {
                        self._left_side(pair): self._right_side(pair)
                        for pair in raw_data.split('|')
                    }
                )

        self.parsed_details = {self._data_key(): parsed_data}

    def _left_side(self, pair):
        return pair.split(':')[0].strip()

    def _right_side(self, pair):
        return pair.split(':')[1].strip()

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key].strip()
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

    def _escape_json_string(self, json_string):
        return json_string.replace('<a href=\"', '').replace('\" target=\"_blank\"', '')
