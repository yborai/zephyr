import sqlite3

import pandas as pd

from simple_salesforce import Salesforce
from ..client import Client
from ..utils import get_config_values


class SalesForce(Client):
    name = "Salesforce"

    def __init__(self, config, log=None, **kwargs):
        super().__init__(config, log=log)
        self._sf = None

    @property
    def sf(self):
        if self._sf:
            return self._sf
        sf_config_keys = ("SF_USER", "SF_PASSWORD", "SF_TOKEN")
        sf_config = get_config_values("lw-sf", sf_config_keys, self.config)
        username, password, token = sf_config
        self._sf = self.get_session(username, password, token)
        return self._sf

    def get_account_by_slug(self, slug):
        matches = pd.read_sql("""
            SELECT a.name AS client
            FROM
                sf_accounts AS a LEFT OUTER JOIN
                sf_projects AS p ON (a.Id=p.Account__c) LEFT OUTER JOIN
                sf_aws AS aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws.name = '{slug}'
            """.format(slug=slug),
            self.database
        )
        if not len(matches):
            self.log.error("There are no projects associated with this slug.")
            return slug
        return matches["client"][0]

    def get_session(self, username, password, token):
        return Salesforce(
            username=username,
            password=password,
            security_token=token,
        )

    def request(self):
        raise NotImplementedError

    def soql_to_sql(self, query, table):
        res = self.sf.query_all(query)
        header = list(zip(*res["records"][0].items()))[0][1:]
        data = [list(zip(*record.items()))[1][1:] for record in res["records"]]
        df = pd.DataFrame(data, columns=header)
        df.to_sql(table, self.database, if_exists="replace")
        return df
