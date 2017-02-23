import pandas as pd
import requests

from ..client import Client
from ..utils import get_config_values, ZephyrException

class Logicops(Client):
    name = "Logicops"
    slug = "service-requests"

    @classmethod
    def get_cookies(cls, username, password):
        url_auth = "https://logicops.logicworks.net"
        lo_ = dict(login=username, passphrase=password)
        r = requests.post(url_auth, data=lo_, verify=False)
        return r.cookies

    def __init__(self, config, log=None):
        super().__init__(config, log=log)
        self._LO_API_BASE = None
        self.LO_PASSWORD = None
        self.LO_USER = None
        self.cookies = None

    @property
    def LO_API_BASE(self):
        if self._LO_API_BASE:
            return self._LO_API_BASE
        self._LO_API_BASE = "https://logicops.logicworks.net/api/v1/"
        lo_config_keys = ("LO_USER", "LO_PASSWORD")
        user, passwd = get_config_values("lw-lo", lo_config_keys, self.config)
        self.LO_PASSWORD = passwd
        self.LO_USER = user
        self.cookies = self.get_cookies(user, passwd)
        return self._LO_API_BASE

    def get_account_by_slug(self, slug):
        name = pd.read_sql("""
            SELECT a.name AS slug, l.name AS lo_name
            FROM
                sf_aws AS a LEFT OUTER JOIN
                sf_projects AS p ON (p."Id" = a."Assoc_Project__c") LEFT OUTER JOIN
                lo_accounts AS l ON (p.LogicOps_ID__c = l.id)
            WHERE a.name = '{slug}'
            """.format(slug=slug),
            self.database
        )["lo_name"]

        if not len(name):
            raise ZephyrException(
                "No matching Logicops ID found in Salesforce."
            )

        return name[0]

    def request(self, account):
        raise NotImplementedError
