import csv
import json

from decimal import Decimal
from re import search, sub

from ..core.ddh import DDH

class Warp(object):
    def __init__(self, json_string):
        self.raw_json = json.loads(json_string)
        self.data = {}
        key = self._key()
        self.data = self.raw_json[0]
        if(len(self.raw_json) > 1):
            self.merge_results(self.raw_json)

    def merge_results(self, pages):
        out = []
        key = self._key()
        for page in pages:
            out += page[key]
        self.data[key] = out
        return self.data

    def write_csv(self, csv_filename):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            writer.writeheader()
            for details_row in self.data[self._key()]:
                writer.writerow(self._filter_row(details_row))

        return csv_filename

    def to_ddh(self):
        header = self._fieldnames()
        parsed = self.data[self._key()]
        data = [
            [self._filter_row(row)[col] for col in header]
            for row in parsed
        ]
        return DDH(header=header, data=data)

    def _fieldnames(self):
        raise NotImplementedError

    def _key(self):
        raise NotImplementedError

    def _filter_row(self, details_row):
        raise NotImplementedError


class RecommendationsWarp(Warp):
    def __init__(self, json_string, bpc_id=None):
        super().__init__(self._remove_links(json_string))
        self.bpc_id = bpc_id

        self.data = self.raw_json[0]
        if(len(self.raw_json) > 1):
            self.merge_results(self.raw_json)

        parsed_data = []
        bpcs = self.data['BestPracticeChecks']
        bpcs_n = len(bpcs)
        for raw_detail_row in bpcs:
            if(bpcs_n > 1 and raw_detail_row['CheckId'] != self.bpc_id):
                continue
            for raw_data in raw_detail_row[self._key()]:
                parsed_data.append(
                    {
                        self._left_side(pair): self._right_side(pair)
                        for pair in raw_data.split('|')
                    }
                )

        self.data = {self._key(): parsed_data}

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

    def _remove_links(self, string):
        return string.replace('<a href=\"', '').replace('\" target=\"_blank\"', '')

    def _key(self):
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
