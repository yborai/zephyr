import json
import os
import sqlite3

import requests

from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode

from ..core import aws, lo
from ..core.ddh import DDH
from ..core.utils import get_config_values, ZephyrException

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

    def request(self, slug):
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
        r = requests.get(url, cookies=self.cookies, verify=False)
        return r.content.decode("utf-8")

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

    def to_ddh(self):
        header = self.header
        data = self.data

        return DDH(header=header, data=data)

