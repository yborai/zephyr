import csv
import json

from .common import DDH

class Sheet(object):
    def __init__(self, json_string):
        self.parsed_details = json.loads(json_string)

    def get_data(self):
        out = list(self._fieldnames())
        rows = self.parsed_details[self._data_key()]
        data = [self._filter_row(row) for row in rows]
        out.extend(data)
        return out

    def write_csv(self, csv_filename):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            writer.writeheader()
            for details_row in self.parsed_details[self._data_key()]:
                writer.writerow(self._filter_row(details_row))

        return csv_filename

    def to_ddh(self):
        header = self._fieldnames()
        parsed = self.parsed_details[self._data_key()]
        data = [[obj[col] for col in header] for obj in parsed]
        return DDH(headers=header, data=data)

    def _fieldnames(self):
        raise NotImplementedError

    def _data_key(self):
        raise NotImplementedError

    def _filter_row(self, details_row):
        raise NotImplementedError
