import datetime
import pandas as pd

from ..core.client import Client
from ..report.common import put_label

class Report(Client):
    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        client = self.cls(config=config)
        response = client.cache_policy(
            account,
            date,
            None,
            expire_cache,
            log=log,
        )
        client.parse(response)
        self.client = client

    def to_xlsx(self, book, formatting):
        ddh = self.client.to_ddh()
        if not ddh.data:
            return False
        return self._xlsx(
            book,
            ddh,
            self.title,
            name=self.name,
            formatting=formatting
        )

class ReportCoverPage(Client):
    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        self.account = account
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.date = date_obj.strftime("%B %Y")

    def get_account_by_slug(self, slug):
        return pd.read_sql("""
            SELECT a.name AS client
            FROM
                accounts AS a LEFT OUTER JOIN
                projects AS p ON (a.Id=p.Account__c) LEFT OUTER JOIN
                aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws.name = '{slug}'
            """.format(slug=slug),
            self.database
        )["client"][0]

    def to_xlsx(self, book, formatting):
        sheet = book.add_worksheet("Cover Page")
        acct = self.get_account_by_slug(self.account)
        label = "{} Account Review".format(acct)
        put_label(book, sheet, label, formatting=formatting)
        put_label(book, sheet, self.date, top=1, formatting=formatting)

        return sheet
