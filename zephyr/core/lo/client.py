import json
import os

import pandas as pd
import requests

from datetime import datetime

from ..client import Client
from ..utils import get_config_values

class Logicops(Client):
    slug = "service-requests"

    @classmethod
    def get_cookies(cls, username, password):
        url_auth = "https://logicops.logicworks.net"
        lo_ = dict(login=username, passphrase=password)
        r = requests.post(url_auth, data=lo_, verify=False)
        return r.cookies

    def __init__(self, config):
        super().__init__(config)
        self.LO_API_BASE = "https://logicops.logicworks.net/api/v1/"
        lo_config_keys = ("LO_USER", "LO_PASSWORD")
        user, passwd = get_config_values("lw-lo", lo_config_keys, config)
        self.name = "Logicops"
        self.LO_PASSWORD = passwd
        self.LO_USER = user
        self.cookies = self.get_cookies(user, passwd)

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
