import json
import csv


class CoreProcessor(object):
    def __init__(self, json_string):
        self.parsed_details = json.loads(json_string)

    def write_csv(self, csv_filename):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.__fieldnames__())

            writer.writeheader()
            for details_row in self.parsed_details[self.__data_key__()]:
                writer.writerow(self.__filter_row__(details_row))

        return csv_filename

    def __fieldnames__(self):
        raise NotImplementedError

    def __data_key__(self):
        raise NotImplementedError

    def __filter_row__(self, details_row):
        raise NotImplementedError
