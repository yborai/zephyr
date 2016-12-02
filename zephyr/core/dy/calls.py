import csv
import datetime
import json

from . import client as dy
from ..ddh import DDH
from ..utils import ZephyrEncoder

class Billing(dy.Dynamics):
    slug="billing"

    def request(self, account, date, log=None):
        query_line_items = ("""
            SELECT a.INVODATE, a.DUEDATE, ITEMNMBR, ITEMDESC, UNITPRCE, QUANTITY, UNITPRCE*QUANTITY
            FROM SOP30300 AS i INNER JOIN
            (
                 SELECT SOPNUMBE, INVODATE, DUEDATE
                 FROM SOP30200 as invoices
                 WHERE 1=1
                     AND SOPTYPE='3'
                     AND INVODATE >=%(start)s
                     AND INVODATE <=%(end)s
                     AND CUSTNMBR =%(account)s
            ) AS a on (i.SOPNUMBE=a.SOPNUMBE)
            WHERE 1=1
                AND SOPTYPE='3'
            ORDER BY a.INVODATE DESC
        """)
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        date_y, date_m = dt.year, dt.month
        fom = datetime.datetime(year=date_y, month=date_m, day=1)
        fom_ly = datetime.datetime(year=date_y-1, month=date_m, day=1)
        dy_name = self.get_account_by_slug(account)
        self.dy.execute(query_line_items,
            dict(
                start=fom_ly.strftime("%Y-%m-%d"),
                end=fom.strftime("%Y-%m-%d"),
                account=dy_name,
            )
        )
        rows = self.dy.fetchall()
        return json.dumps(rows, cls=ZephyrEncoder)

    def parse(self, response):
        rows = json.loads(response)
        self.header = [
            "Invoice Date",
            "Due Date",
            "Line Item",
            "Description",
            "Unit",
            "Quantity",
            "Subtotal",
        ]
        self.data = [
            (
                invd,
                dued,
                line.strip(),
                desc.strip(),
                float(unit),
                float(qty),
                float(stot)
            )
            for invd, dued, line, desc, unit, qty, stot in rows
        ]

    def to_ddh(self):
        return DDH(header=self.header, data=self.data)


"""
Billing CSV passthrough
"""

def data(cache="billing-monthly.csv"):
    with open(cache, "r") as f:
        reader = csv.DictReader(f)
        out = [reader.fieldnames] + [[row[col] for col in reader.fieldnames] for row in reader]
    return out

