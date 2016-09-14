import csv
import itertools

from .core import RecommendationsWarp

def create_sheet(csv_filepath, csv_filename='ri_pricing.csv'):
    processor = RIPricingWarp(csv_filepath)
    return processor.write_csv(csv_filename)

class RIPricingWarp(RecommendationsWarp):
    def __init__(self, csv_filepath):
        self._read_from_csv(csv_filepath)

        grouped_csv_data = self._prepare_csv_total_data()
        self.data = {self._key(): grouped_csv_data}

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key]
            for key in self._fieldnames() if key in details_row.keys()
        }

        return filtered_row

    def _read_from_csv(self, csv_filepath):
        with open(csv_filepath) as csvfile:
            self.csv_data = list(csv.DictReader(list(csvfile)[5:]))

    def _prepare_csv_total_data(self):
        csv_data = sorted(self.csv_data, key=self._csv_group_keys, reverse=True)
        csv_data = itertools.groupby(csv_data, self._csv_group_keys)

        grouped_csv_data = []
        for group, data in csv_data:
            total_data = {}
            for row in data:
                if self._is_second_date(total_data, row):
                    break

                total_data['Region'] = row['Location']
                total_data['EffectiveDate'] = row['EffectiveDate']
                total_data['Instance Type'] = row['Instance Type']
                total_data['Tenancy'] = row['Tenancy']
                total_data['Platform'] = row['Operating System']
                total_data['Payment Type'] = row['PurchaseOption']
                total_data['Term'] = 12 if row['LeaseContractLength'] == '1yr' else 36

                if row['Unit'] == 'Quantity':
                    total_data['Upfront'] = row['PricePerUnit']
                else:
                    total_data['Monthly'] = row['PricePerUnit']

            if total_data['Payment Type'] == 'All Upfront':
                total_data['Monthly'] = 0
            if total_data['Payment Type'] == 'No Upfront':
                total_data['Upfront'] = 0

            if total_data['Payment Type'] and total_data['Region']:
                grouped_csv_data.append(total_data)

        return grouped_csv_data

    def _is_second_date(self, total_data, row):
        return ('EffectiveDate' in total_data and total_data['EffectiveDate'] and
                total_data['EffectiveDate'] != row['EffectiveDate'])

    def _csv_group_keys(self, row):
        return (
            row['EffectiveDate'], row['Location'], row['Tenancy'],
            row['Operating System'], row['Instance Type'], row['LeaseContractLength']
        )

    def _fieldnames(self):
        return (
            'Region', 'Tenancy', 'Platform', 'Instance Type', 'Term',
            'Payment Type', 'Upfront', 'Monthly'
        )
