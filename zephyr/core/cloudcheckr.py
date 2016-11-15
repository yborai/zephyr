import json
import os

import pandas as pd
import requests

from datetime import datetime
from urllib.parse import urlencode

from .client import Client
from .utils import get_config_values, timed

class CloudCheckr(Client):
    def __init__(self, config):
        super().__init__(config)
        cc_config_keys = ("api_key", "base")
        api_key, base = get_config_values("cloudcheckr", cc_config_keys, config)
        self.api_key = api_key
        self.base = base
        self.name = "CloudCheckr"

    def cache_policy(self, account, date, cache_file, expired, log=None):
        # If cache_file is specified then use that
        if(cache_file):
            log.info("Using specified cached response: {cache}".format(cache=cache_file))
            with open(cache_file, "r") as f:
                return f.read()
        # If no date is given then default to the first of last month.
        now = datetime.now()
        if(not date):
            date = datetime(year=now.year, month=now.month-1, day=1).strftime("%Y-%m-%d")
        # If local exists and expired is false then use the local cache
        cache_key = self.cache_key(account, date)
        cache_local = os.path.join(self.cache_root, cache_key)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        cache_s3 = self.get_object_from_s3(cache_key)
        if(cache_s3 and not expired):
            log.info("Using cached response from S3.")
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        # If we are this far then contact the API and cache the result
        log.info("Retrieving data from {}.".format(self.name))
        response = self.request(account, date, log=log)
        self.cache(response, cache_key, log=log)
        return response

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
            obj = resp.json()
            page_next = obj.get("HasNext", False)
            token = ""
            if(page_next):
                token = obj["NextToken"]
            out.append(obj)
        return out

    def request(self, account, date, log=None):
        cc_name = self.get_account_by_slug(account)
        params = self.get_params(self.api_key, cc_name, date)
        url = "".join([
            self.base,
            self.uri,
            "?",
            urlencode(params),
        ])
        log.info(url)
        response = self.load_pages(url, timing=True, log=log.info)
        return json.dumps(response)

class CloudCheckrAccounts(CloudCheckr):
    uri = "account.json/get_accounts_v2"
    def __init__(self, config, log=None):
        super().__init__(config)
        self.log = log

    def request(self):
        params = dict(access_key=self.api_key)
        url = "".join([
            self.base,
            self.uri,
            "?",
            urlencode(params),
        ])
        r = timed(lambda:requests.get(url), log=self.log.info)()
        accts = r.json()
        header = ["aws_account", "id", "name"]
        data = [[
                acct["aws_account_id"],
                acct["cc_account_id"],
                acct["account_name"],
            ]
            for acct in accts["accounts_and_users"]
        ]
        df = pd.DataFrame(data, columns=header)
        df.to_sql("cloudcheckr_accounts", self.database, if_exists="replace")
