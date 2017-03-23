import json

import pandas as pd
import requests

from urllib.parse import urlencode
from re import search, sub

from ..client import Client
from ..utils import get_config_values, timed, ZephyrException

class CloudCheckr(Client):
    name = "CloudCheckr"

    @classmethod
    def get_params(cls, cc_api_key, name, date):
        return dict(
            access_key=cc_api_key,
            date=date,
            use_account=name,
        )

    def __init__(self, config=None, log=None, **kwargs):
        if(config):
            super().__init__(config, log=log)
        self._CC_API_KEY = None

    @property
    def CC_API_KEY(self):
        if self._CC_API_KEY:
            return self._CC_API_KEY
        cc_config_keys = ("CC_API_KEY", "CC_API_BASE")
        CC_API_KEY, CC_API_BASE = get_config_values("lw-cc", cc_config_keys, self.config)
        self._CC_API_KEY = CC_API_KEY
        self.CC_API_BASE = CC_API_BASE
        return self._CC_API_KEY

    def get_account_by_slug(self, acc_short_name):
        matches = pd.read_sql("""
            SELECT a.name AS slug, c.name AS cc_name
            FROM
                sf_aws AS a LEFT OUTER JOIN
                cc_accounts AS c ON (c.aws_account = a."Acct_Number__c")
            WHERE a.name = '{slug}'
            """.format(slug=acc_short_name),
            self.database
        )["cc_name"]

        if not len(matches):
            raise ZephyrException(
                "No matching account for {}. "
                "Please see zephyr meta for a list of accounts."
                .format(acc_short_name)
            )

        return matches[0]

    def get_instance_id(self, instance_string):
        return instance_string.strip().split(" ")[0]

    def get_instance_name(self, instance_string):
        regex = search("\((.*?)\)", instance_string)
        if regex is not None:
            return search("\((.*?)\)", instance_string).group(0)[1:-1]
        return ""

    def load_pages(self, url, timing=False, log=print):
        """
        Pagination
        """
        tmpl = "&next_token={token}"
        token = ""
        page_next = True
        out = list()
        def time(func):
            if(timing):
                return timed(func, log=log)
            return func

        while(page_next):
            url_cur = url
            if(token):
                url_cur = url + tmpl.format(token=token)
            resp = time(lambda:requests.get(url_cur))()
            if(resp.status_code != 200):
                raise ZephyrException(
                    "Response not OK, got code: {}".format(resp.status_code)
                )
            obj = resp.json()
            page_next = obj.get("HasNext", False)
            token = ""
            if(page_next):
                token = obj["NextToken"]
            out.append(obj)
        return out

    def merge(self, pages):
        return sum([
            self._items_from_pages(page)
            for page in pages
        ], [])

    def parse(self, json_string):
        results = json.loads(json_string)
        items = self.merge(results)
        self.data = [[row[col] for col in self.header] for row in items]

    def request(self, account, date):
        cc_name = self.get_account_by_slug(account)
        params = self.get_params(self.CC_API_KEY, cc_name, date)
        url = "".join([
            self.CC_API_BASE,
            self.uri,
            "?",
            urlencode(params),
        ])
        self.log.debug(url)
        response = self.load_pages(url, timing=True, log=self.log.info)
        return json.dumps(response)

class CloudCheckrBPC(CloudCheckr):
    uri = "best_practice.json/get_best_practices"

    @classmethod
    def get_params(cls, cc_api_key, name, date):
        return dict(
            access_key=cc_api_key,
            bpc_id=cls.bpc_id,
            date=date,
            use_account=name,
        )

    def __init__(self, bpc_id=None, config=None, log=None, **kwargs):
        if(config):
            super().__init__(config, log=log)
        self.bpc_id = bpc_id

    def parse(self, json_string):
        results = json.loads(json_string)
        items = self.merge(results)
        self.data = [
            self.row(item)
            for item in items
        ]

    def row(self, item):
        row = dict([pair.split(": ") for pair in item.split(" | ")])
        if "Instance" in row.keys():
            row["Instance ID"] = self.get_instance_id(row["Instance"])
            row["Instance Name"] = self.get_instance_name(row["Instance"])
        return [row[key] for key in self.header]

    def _items_from_pages(self, page):
        result = page["BestPracticeChecks"]
        if result:
            return result[0]['Results']
        return []
