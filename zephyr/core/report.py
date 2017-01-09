import datetime
import pandas as pd

from ..core.client import Client
from ..core.utils import ZephyrException
from ..report.common import put_label

class Report(Client):
    name = None
    title = None

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
    name = "coverpage"
    title = "Cover Page"

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        self.account = account
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.date = date_obj.strftime("%B %d, %Y")

    def get_account_by_slug(self, slug):
        matches = pd.read_sql("""
            SELECT a.name AS client
            FROM
                accounts AS a LEFT OUTER JOIN
                projects AS p ON (a.Id=p.Account__c) LEFT OUTER JOIN
                aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws.name = '{slug}'
            """.format(slug=slug),
            self.database
        )
        if not len(matches):
            raise ZephyrException("There are no projects associated with this slug.")
        return matches["client"][0]

    def to_xlsx(self, book, formatting):
        sheet = book.add_worksheet(self.title)
        acct = self.get_account_by_slug(self.account)
        put_label(book, sheet, "Account Review", formatting=formatting)
        put_label(book, sheet, acct, top=1, formatting=formatting)
        put_label(book, sheet, self.date, top=2, formatting=formatting)

        return sheet
