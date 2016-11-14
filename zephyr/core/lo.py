import json
import os

import pandas as pd
import requests

from datetime import datetime

from .client import Client
from .utils import get_config_values

class Logicops(Client):
    @classmethod
    def cache_key(cls, account, date):
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "service-requests.{date}.json".format(date=date)
        return os.path.join(account, month, filename)

    @classmethod
    def get_cookies(cls, username, password):
        url_auth = "https://logicops.logicworks.net"
        lo_ = dict(login=username, passphrase=password)
        r = requests.post(url_auth, data=lo_, verify=False)
        return r.cookies

    def __init__(self, config):
        super().__init__(config)
        self.base = "https://logicops.logicworks.net/api/v1/"
        lo_config_keys = ("login", "passphrase")
        user, passwd = get_config_values("lw-lo", lo_config_keys, config)
        self.user = user
        self.passwd = passwd
        self.cookies = self.get_cookies(self.user, self.passwd)

    def cache(self, response, cache_key, log=None):
        cache_local = os.path.join(self.cache_root, cache_key)
        log.info("Caching service-requests response locally.")
        with open(cache_local, "w") as f:
            f.write(response)
        log.info("Caching service-requests response in S3.")
        # Save a copy the response on S3
        s3 = self.session.resource("s3")
        s3.meta.client.upload_file(cache_local, self.bucket, cache_key)

    def cache_policy(self, account, date, cache_file, expired, log=None):
        #
        #
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
        cache_key_ = self.cache_key(account, date)
        cache_local = os.path.join(self.cache_root, cache_key_)
        os.makedirs(os.path.dirname(cache_local), exist_ok=True)
        cache_local_exists = os.path.isfile(cache_local)
        if(cache_local_exists and not expired):
            log.info("Using cached response: {cache}".format(cache=cache_local))
            with open(cache_local, "r") as f:
                return f.read()
        # If local does not exist and expired is false then check s3
        cache_s3 = self.get_object_from_s3(cache_key_)
        if(cache_s3 and not expired):
            log.info("Using cached response from S3.")
            with open(cache_local, "wb") as cache_fd:
                cache_fd.write(cache_s3)
            return cache_s3.decode("utf-8")
        # If no cache exists and the report is not for today then break.
        today = now.strftime("%Y-%m-%d")
        if(date != today and not expired):
            raise ZephyrException(
                "Cache not found for date {}. "
                "Specify today's date to run this report "
                "for current Service Requests.".format(date)
        )
        # If we are this far then contact the API and cache the result
        log.info("Retrieving data from Logicops.")
        response = self.request(account)
        self.cache(response, cache_key_, log=log)
        return response

    def get_account_by_slug(self, slug):
        return pd.read_sql("""
            SELECT a.name AS slug, l.name AS lo_name
            FROM
                aws AS a LEFT OUTER JOIN
                projects AS p ON (p."Id" = a."Assoc_Project__c") LEFT OUTER JOIN
                logicops_accounts AS l ON (p.LogicOps_ID__c = l.id)
            WHERE a.name = '{slug}'
            """.format(slug=slug),
            self.database
        )["lo_name"][0]

    def request(self, account):
        raise NotImplementedError

class LogicopsAccounts(Logicops):
    def __init__(self, config):
        super().__init__(config)

    def request(self):
        url_accts = "https://logicops.logicworks.net/api/v1/accounts/"
        r = requests.get(url_accts, cookies=self.cookies, verify=False)
        accts = r.json()
        accounts = accts["accounts"]
        header = ["id", "name"]
        data = [[account[col] for col in header] for account in accounts]
        df = pd.DataFrame(data, columns=header)
        df.to_sql("logicops_accounts", self.database, if_exists="replace")
        return r.content.decode("utf-8")
