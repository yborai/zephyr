import json
import csv


class CoreProcessor(object):
    def __init__(self, json_string):
        self.parsed_details = json.loads(json_string)

    def write_csv(self, csv_filename):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            writer.writeheader()
            for details_row in self.parsed_details[self._data_key()]:
                writer.writerow(self._filter_row(details_row))

        return csv_filename

    def _fieldnames(self):
        raise NotImplementedError

    def _data_key(self):
        raise NotImplementedError

    def _filter_row(self, details_row):
        raise NotImplementedError
