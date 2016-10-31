import json

import requests

from collections import OrderedDict
from urllib.parse import urlencode

from ..core.ddh import DDH

class ServiceRequests(object):
    base = "https://logicops.logicworks.net/api/v1/"
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
    def read_srs(cls, account, cookies=None):
        params = {
            "team_options[0]" : "_all_",
            "assigned_to_options[0]" : "_all_",
            "group_options[0]" : "_all_",
            "area_options[0]" : "_all_",
            "status_options[0]" : "_all_",
            "severity_options[0]" : "_all_",
            "account_options[0]" : account,
        }
        url = "".join([
            cls.base,
            cls.uri,
            "?",
            urlencode(params),
        ])
        r = requests.get(url, cookies=cookies, verify=False)
        return r.content.decode("utf-8")

    def __init__(self, json_string=None):
        self.response = json.loads(json_string)
        header_raw = self.response["header"]
        data_raw = self.response["data"]

        self.header = list(self.header_hash.values())
        self.column_indexes = [header_raw.index(key) for key in list(self.header_hash.keys())]
        self.data = [[row[index] for index in self.column_indexes] for row in data_raw]

    def to_ddh(self):
        header = self.header
        data = self.data

        return DDH(header=header, data=data)


