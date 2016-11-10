import json
import os

import pandas as pd
import requests

from urllib.parse import urlencode

from .client import Client
from .utils import account_ids, get_config_values, timed

class CloudCheckr(Client):
    def __init__(self, config):
        super().__init__(config)
        cc_config_keys = ("api_key", "base")
        api_key, base = get_config_values("cloudcheckr", cc_config_keys, config)
        self.api_key = api_key
        self.base = base

    def cache(
            self,
            account,
            date,
            log=None
        ):
        cache_key = self.cache_key(account, date)
        cc_name = self.get_account_by_slug(account, self.database)
        params = self.get_params(self.api_key, cc_name, date)
        url = "".join([
            self.base,
            self.uri,
            "?",
            urlencode(params),
        ])
        log.info(url)
        response = self.load_pages(url, timing=True, log=log.info)
        cache_local = os.path.join(self.cache_root, cache_key)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        with open(cache_local, "w") as f:
            json.dump(response, f)
        # Save a copy the response on S3
        s3 = self.session.resource("s3")
        s3.meta.client.upload_file(cache_local, self.bucket, self.cache_key)
        return json.dumps(response)

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

def get_accounts(database, config, log=None):
    base = "https://api.cloudcheckr.com/api/"
    uri_accts = "account.json/get_accounts_v2"
    api_key = config[0]
    params = dict(access_key=api_key)
    url = "".join([
        base,
        uri_accts,
        "?",
        urlencode(params),
    ])
    r = timed(lambda:requests.get(url), log=log)()
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
    df.to_sql("cloudcheckr_accounts", database, if_exists="replace")
