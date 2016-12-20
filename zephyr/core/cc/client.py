import json
import os

import pandas as pd
import requests

from datetime import datetime
from urllib.parse import urlencode

from ..client import Client
from ..utils import get_config_values, timed, ZephyrException

class CloudCheckr(Client):
    def __init__(self, config):
        super().__init__(config)
        cc_config_keys = ("CC_API_KEY", "CC_API_BASE")
        CC_API_KEY, CC_API_BASE = get_config_values("lw-cc", cc_config_keys, config)
        self.CC_API_KEY = CC_API_KEY
        self.CC_API_BASE = CC_API_BASE
        self.name = "CloudCheckr"

    def get_account_by_slug(self, acc_short_name):
        return pd.read_sql("""
            SELECT a.name AS slug, c.name AS cc_name
            FROM
                aws AS a LEFT OUTER JOIN
                cloudcheckr_accounts AS c ON (c.aws_account = a."Acct_Number__c")
            WHERE a.name = '{slug}'
            """.format(slug=acc_short_name),
            self.database
        )["cc_name"][0]

    @classmethod
    def get_params(cls, cc_api_key, name, date):
        return dict(
            access_key=cc_api_key,
            date=date,
            use_account=name,
        )

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

    def request(self, account, date, log=None):
        cc_name = self.get_account_by_slug(account)
        params = self.get_params(self.CC_API_KEY, cc_name, date)
        url = "".join([
            self.CC_API_BASE,
            self.uri,
            "?",
            urlencode(params),
        ])
        log.debug(url)
        response = self.load_pages(url, timing=True, log=log.info)
        return json.dumps(response)

    def slug_valid(self, slug):
        return self.get_account_by_slug(slug)
