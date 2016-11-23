import datetime
import json

from . import client as dy
from ..ddh import DDH

class MonthlyInvoice(dy.Dynamics):
    slug="billing-monthly"

    def request(self, account, date, log=None):
        query_invm = ("""
            SELECT year(INVODATE), month(INVODATE), sum(SUBTOTAL)
            FROM SOP30200 AS invoices
            WHERE 1=1
                AND SOPTYPE='3'
                AND INVODATE>= %(start)s
                AND INVODATE<= %(end)s
                AND CUSTNMBR= %(account)s
            GROUP BY year(INVODATE), month(INVODATE)
            ORDER BY concat(year(INVODATE), month(INVODATE)) DESC
            """
        )
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        date_y, date_m = dt.year, dt.month
        fom = datetime.datetime(year=date_y, month=date_m, day=1)
        fom_ly = datetime.datetime(year=date_y-1, month=date_m, day=1)
        dy_name = self.get_account_by_slug(account)
        self.dy.execute(query_invm,
            dict(
                start=fom_ly.strftime("%Y-%m-%d"),
                end=fom.strftime("%Y-%m-%d"),
                account=dy_name,
            )
        )
        rows = self.dy.fetchall()
        return json.dumps(rows)

    def parse(self, response):
        rows = json.loads(response)
        self.header = ["Month", "Total"]
        self.data = [
            (
                datetime.datetime(year=year, month=month, day=1).strftime("%Y-%m"),
                str(round(stot,2))
            )
            for year, month, stot in rows
        ]

    def to_ddh(self):
        return DDH(header=self.header, data=self.data)

