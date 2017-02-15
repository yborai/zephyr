import os

import pandas as pd
import pymssql

from datetime import datetime

from ..client import Client
from ..utils import get_config_values, ZephyrException

class Dynamics(Client):
    def __init__(self, config, log=None, **kwargs):
        super().__init__(config, log=log)
        dy_config_keys = ("DY_HOST", "DY_USER", "DY_PASSWORD")
        host, user, password = get_config_values("lw-dy", dy_config_keys, config)
        self.name = "Dynamics"
        try:
            conn = pymssql.connect(host, user, password, "DTI", login_timeout=5)
        except pymssql.OperationalError:
            raise ZephyrException("Could not connect to Dynamics.")
        self.dy = conn.cursor()

    def get_account_by_slug(self, slug):
        name = pd.read_sql("""
            SELECT a.name AS slug, p."Dynamics_ID__c" AS dy_name
            FROM
                aws AS a LEFT OUTER JOIN
                projects AS p ON (p."Id" = a."Assoc_Project__c")
            WHERE a.name = :slug
            """,
            self.database,
            params=dict(slug=slug),
        )["dy_name"]

        if not len(name):
            raise ZephyrException(
                "No matching Dynamics ID found in Salesforce."
            )

    def request(self, account):
        raise NotImplementedError
