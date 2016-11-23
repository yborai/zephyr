import os

import pandas as pd
import pymssql

from datetime import datetime

from ..client import Client
from ..utils import get_config_values, ZephyrException

class Dynamics(Client):
    @classmethod
    def cache_key(cls, account, date):
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m")
        filename = "{slug}.json".format(slug=cls.slug)
        return os.path.join(account, month, filename)

    def __init__(self, config):
        super().__init__(config)
        dy_config_keys = ("host", "user", "password")
        host, user, password = get_config_values("lw-dy", dy_config_keys, config)
        self.name = "Dynamics"
        conn = pymssql.connect(host, user, password, "DTI")
        self.dy = conn.cursor()

    def get_account_by_slug(self, slug):
        return pd.read_sql("""
            SELECT a.name AS slug, p."Dynamics_ID__c" AS dy_name
            FROM
                aws AS a LEFT OUTER JOIN
                projects AS p ON (p."Id" = a."Assoc_Project__c")
            WHERE a.name = :slug
            """,
            self.database,
            params=dict(slug=slug),
        )["dy_name"][0]

    def request(self, account):
        raise NotImplementedError
