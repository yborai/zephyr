import csv
import itertools
from decimal import Decimal

from .recommendations_core import RecommendationsCoreProcessor


def create_sheet(json_string, csv_filepath, csv_filename='ri_pricing.csv'):
    processor = RIPricingProcessor(json_string, csv_filepath)
    return processor.write_csv(csv_filename)


class RIPricingProcessor(RecommendationsCoreProcessor):
    def __init__(self, json_string, csv_filepath):
        super().__init__(json_string)

        self._read_from_csv(csv_filepath)
        self._merge_data()

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key]
            for key in self._fieldnames() if key in details_row.keys()
        }

        return filtered_row

    def _read_from_csv(self, csv_filepath):
        with open(csv_filepath) as csvfile:
            self.csv_data = list(csv.DictReader(list(csvfile)[5:]))

    def _merge_data(self):
        grouped_json_data = self._prepare_json_total_data()
        grouped_csv_data = self._prepare_csv_total_data(grouped_json_data)

        self.parsed_details = {self._data_key(): grouped_csv_data}

    def _prepare_csv_total_data(self, grouped_json_data):
        csv_data = sorted(self.csv_data, key=self._csv_group_keys)
        csv_data = itertools.groupby(csv_data, self._csv_group_keys)

        grouped_csv_data = []
        for group, data in csv_data:
            total_data = {}
            for row in data:
                total_data['Region'] = row['Location']
                total_data['Instance Type'] = row['Instance Type']
                total_data['Tenancy'] = row['Tenancy']
                total_data['Platform'] = row['Operating System']
                total_data['Payment Type'] = row['PurchaseOption']
                total_data['Term'] = 12 if row['LeaseContractLength'] == '1yr' else 36

                if row['Unit'] == 'Quantity':
                    total_data['Upfront'] = row['PricePerUnit']

                    for json_data_row in grouped_json_data:
                        if self._same_instance(total_data, json_data_row):
                            total_data['Effective Hourly'] = (
                                json_data_row['Reserved Monthly Cost'] /
                                Decimal(total_data['Upfront'])
                            )
                            total_data['On-Demand Hourly'] = (
                                json_data_row['On-Demand Monthly Cost'] /
                                Decimal(total_data['Upfront'])
                            )
                else:
                    total_data['Monthly'] = row['PricePerUnit']

            if total_data['Payment Type'] == 'All Upfront':
                total_data['Monthly'] = 0
            if total_data['Payment Type'] == 'No Upfront':
                total_data['Upfront'] = 0

            if total_data['Payment Type'] and total_data['Region']:
                grouped_csv_data.append(total_data)

        return grouped_csv_data

    def _prepare_json_total_data(self):
        json_data = list(map(self._fix_az_naming, self.parsed_details[self._data_key()]))
        json_data = list(map(self._format_money_fields, json_data))

        json_data = sorted(json_data, key=self._json_group_keys)
        json_data = itertools.groupby(json_data, self._json_group_keys)

        grouped_json_data = []
        for group, data in json_data:
            total_data = {}
            for row in data:
                total_data['Region'] = row['AZ']
                total_data['Instance Type'] = row['Instance Type']
                total_data['Tenancy'] = row['Tenancy']

                if 'Linux' in row['Platform']:
                    total_data['Platform'] = 'Linux'
                else:
                    total_data['Platform'] = row['Platform']

                if 'Partial' in row['Commitment Type']:
                    total_data['Payment Type'] = 'Partial Upfront'

                if '1 Year Partial' in row['Commitment Type']:
                    total_data['Term'] = 12
                else:
                    total_data['Term'] = 36

                total_data['Reserved Monthly Cost'] = row['Reserved Monthly Cost']
                total_data['On-Demand Monthly Cost'] = row['On-Demand Monthly Cost']

                total_data = self._aggregate_data(total_data, row)
            grouped_json_data.append(total_data)

        return grouped_json_data

    def _same_instance(self, json_data_row, total_data):
        return (json_data_row['Region'] == total_data['Region'] and
                json_data_row['Instance Type'] == total_data['Instance Type'] and
                json_data_row['Platform'] == total_data['Platform'] and
                json_data_row['Payment Type'] == total_data['Payment Type'] and
                json_data_row['Term'] == total_data['Term'])

    def _aggregate_data(self, total_data, row):
        for field in self._money_fields() + ('Number',):
            if field in total_data:
                total_data[field] += row[field]
            else:
                total_data[field] = row[field]

        return total_data

    def _money_fields(self):
        return (
            "Upfront RI Cost", "Reserved Monthly Cost",
            "On-Demand Monthly Cost", "Total Savings"
        )

    def _fix_az_naming(self, elem):
        for code in self._region_code_name_map().keys():
            if code in elem['AZ']:
                elem['AZ'] = self._region_code_name_map()[code]

        return elem

    def _csv_group_keys(self, row):
        return (
            row['Location'], row['Tenancy'], row['Operating System'],
            row['Instance Type'], row['LeaseContractLength']
        )

    def _json_group_keys(self, row):
        return (
            row['AZ'], row['Tenancy'], row['Platform'],
            row['Instance Type'], row['Commitment Type']
        )

    def _fieldnames(self):
        return (
            'Region', 'Tenancy', 'Platform', 'Instance Type', 'Term',
            'Payment Type', 'Upfront', 'Monthly', 'Effective Hourly',
            'On-Demand Hourly'
        )

    def _region_code_name_map(self):
        return {
            'us-east-1': 'US East (N. Virginia)', 'us-west-2': 'US West (Oregon)',
            'us-west-1': 'US West (N. California)', 'eu-west-1': 'EU (Ireland)',
            'eu-central-1': 'EU (Frankfurt)', 'ap-southeast-1': 'Asia Pacific (Singapore)',
            'ap-northeast-1': 'Asia Pacific (Tokyo)', 'ap-southeast-2': 'Asia Pacific (Sydney)',
            'ap-northeast-2': 'Asia Pacific (Seoul)', 'sa-east-1': 'South America (São Paulo)'
        }
