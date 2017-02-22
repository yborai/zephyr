import pandas as pd
import pymssql

from ..client import Client
from ..utils import get_config_values, ZephyrException

class Dynamics(Client):
    name = "Dynamics"

    def __init__(self, config, log=None, **kwargs):
        super().__init__(config, log=log)
        self._dy = None

    @property
    def dy(self):
        if self._dy:
            return self._dy
        dy_config_keys = ("DY_HOST", "DY_USER", "DY_PASSWORD")
        host, user, password = get_config_values("lw-dy", dy_config_keys, self.config)
        try:
            self.conn = pymssql.connect(host, user, password, "DTI", login_timeout=5)
        except pymssql.OperationalError:
            raise ZephyrException("Could not connect to Dynamics.")
        self._dy = self.conn.cursor()
        return self._dy

    def get_account_by_slug(self, slug):
        name = pd.read_sql("""
            SELECT a.name AS slug, p."Dynamics_ID__c" AS dy_name
            FROM
                sf_aws AS a LEFT OUTER JOIN
                sf_projects AS p ON (p."Id" = a."Assoc_Project__c")
            WHERE a.name = :slug
            """,
            self.database,
            params=dict(slug=slug),
        )["dy_name"]

        if not len(name):
            raise ZephyrException(
                "No matching Dynamics ID found in Salesforce."
            )

        return name[0]

    def request(self, account):
        raise NotImplementedError
