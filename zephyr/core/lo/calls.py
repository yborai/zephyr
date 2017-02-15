import json

import pandas as pd
import requests

from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlencode

from ..utils import first_of_previous_month
from . import client as lo

class ServiceRequests(lo.Logicops):
    uri = "sr-filter"

    header_hash = OrderedDict([
        ("name", "Name"),
        ("summary", "Summary"),
        ("status", "Status"),
        ("severity", "Severity"),
        ("area", "Area"),
        ("created_date", "Created Date"),
        ("closed_date", "Closed Date"),
    ])

    def __init__(self, config=None, log=None, **kwargs):
        if(config):
            super().__init__(config, log=log)

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

    def request(self, slug, date):
        lo_acct = self.get_account_by_slug(slug)
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        start_date = first_of_previous_month(date_obj).strftime("%Y-%m-%d")
        params = {
            "account_options[]" : lo_acct,
            "start_date" : start_date,
            "end_date" : date,
            "sort_option" : "-created_date",
            "status_option" : "_all_",
            "list_srs" : "1",
            "limit" : "200",
        }
        url = "".join([
            self.LO_API_BASE,
            self.uri,
            "?",
            urlencode(params),
        ])
        self.log.debug(url)
        r = requests.get(url, cookies=self.cookies, verify=False)
        return r.content.decode("utf-8")

class LogicopsAccounts(lo.Logicops):
    def request(self):
        url_accts = "https://logicops.logicworks.net/api/v1/accounts/"
        r = requests.get(url_accts, cookies=self.cookies, verify=False)
        accts = r.json()
        accounts = accts["accounts"]
        header = ["id", "name"]
        data = [[account[col] for col in header] for account in accounts]
        df = pd.DataFrame(data, columns=header)
        df.to_sql("lo_accounts", self.database, if_exists="replace")
        return r.content.decode("utf-8")

__ALL__ = [
    LogicopsAccounts,
    ServiceRequests,
]
