import csv
import json

from decimal import Decimal
from re import search, sub

from .common import DDH

class Warp(object):
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
        data = [
            [self._filter_row(row)[col] for col in header]
            for row in parsed
        ]
        return DDH(headers=header, data=data)

    def _fieldnames(self):
        raise NotImplementedError

    def _data_key(self):
        raise NotImplementedError

    def _filter_row(self, details_row):
        raise NotImplementedError


class RecommendationsWarp(Warp):
    def __init__(self, json_string, bpc_id=None):
        self.bpc_id = bpc_id
        raw_details = json.loads(self._escape_json_string(json_string))

        parsed_data = []
        bpcs = raw_details['BestPracticeChecks']
        bpcs_n = len(bpcs)
        for raw_detail_row in raw_details['BestPracticeChecks']:
            if(bpcs_n > 1 and raw_detail_row['CheckId'] != self.bpc_id):
                continue
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

    def _format_money_fields(self, row):
        for money_field in self._money_fields():
            row[money_field] = self._parse_money(row[money_field])

        return row

    def _money_fields(self):
        raise NotImplementedError

    def _parse_money(self, money_string):
        return Decimal(sub(r'[^\d\-.]', '', money_string))

    def _escape_json_string(self, json_string):
        return json_string.replace('<a href=\"', '').replace('\" target=\"_blank\"', '')

    def _data_key(self):
        return 'Results'


class SplitInstanceWarp(RecommendationsWarp):
    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])

        return super()._filter_row(details_row)

    def _get_instance_id(self, instance_string):
        return instance_string.strip().split(' ')[0]

    def _get_instance_name(self, instance_string):
        regex = search('\((.*?)\)', instance_string)
        if regex is not None:
            return search('\((.*?)\)', instance_string).group(0)[1:-1]
        return ''

    def _instance_field(self):
        return "Instance"
