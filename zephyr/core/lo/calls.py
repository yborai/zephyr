import csv
import json

import requests

from collections import OrderedDict
from urllib.parse import urlencode

from . import client as lo
from ..ddh import DDH

class ServiceRequests(lo.Logicops):
    uri = "sr-filter"

    header_hash = OrderedDict([
        ("summary", "Summary"),
        ("status", "Status"),
        ("severity", "Severity"),
        ("area", "Area"),
        ("created_date", "Created Date"),
        ("created_by", "Created By"),
    ])

    @classmethod
    def create_sheet(cls, json_string, csv_filename="out.csv"):
        processor = cls(json_string)
        return processor.write_csv(csv_filename)

    def __init__(self, json_string=None, config=None):
        if(config):
            super().__init__(config)
        if(json_string):
            self.parse(json_string)

    def parse(self, json_string):
        self.response = json.loads(json_string)
        header_raw = self.response["header"]
        data_raw = self.response["data"]

        self.header = list(self.header_hash.values())
        self.column_indexes = [
            header_raw.index(key)
            for key in list(self.header_hash.keys())
        ]
        self.data = [[row[index] for index in self.column_indexes] for row in data_raw]
        return self.response

    def request(self, slug, log=None):
        lo_acct = self.get_account_by_slug(slug)
        params = {
            "team_options[0]" : "_all_",
            "assigned_to_options[0]" : "_all_",
            "group_options[0]" : "_all_",
            "area_options[0]" : "_all_",
            "status_options[0]" : "_all_",
            "severity_options[0]" : "_all_",
            "account_options[0]" : lo_acct,
        }
        url = "".join([
            self.base,
            self.uri,
            "?",
            urlencode(params),
        ])
        log.debug(url)
        r = requests.get(url, cookies=self.cookies, verify=False)
        return r.content.decode("utf-8")

    def write_csv(self, csv_filename):
        with open(csv_filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.header)

            writer.writeheader()
            for row in self.data:
                row_dict = dict(zip(self.header, row))
                writer.writerow(row_dict)

        return csv_filename

__ALL__ = [
    ServiceRequests
]
