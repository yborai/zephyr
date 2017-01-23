import sqlite3
import pandas as pd

from ..ddh import DDH
from ..report import Report
from .calls import Billing

class ReportBilling(Report):
    name = "Billing"
    title = "Billing Line Items"
    cls = Billing

    def group_by_lineitem(self):
        """Groups rows by line item"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
        df.to_sql("df", con, if_exists="replace")
        query = """
            SELECT
                "Line Item",
                Description,
                SUM(Subtotal) as "Total"
            FROM df
            WHERE "Line Item" NOT LIKE '***Note'
            GROUP BY
                "Line Item"
            ORDER BY "Total" DESC
        """

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        ddh = DDH(header=header, data=data)

        return ddh

    def group_by_month(self):
        """Groups rows by month"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
        df.to_sql("df", con, if_exists="replace")
        query = """
            SELECT
                SUBSTR("Invoice Date", 0, 8) as "Month",
                SUM("Subtotal") as "Total"
            FROM df
            GROUP BY
                "Month"
            ORDER BY "Month"
        """

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        ddh = DDH(header=header, data=data)

        return ddh

    def _xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, top=1, name=self.name)

        aggs_name = "Aggregates"
        aggs_title = "Billing Line Item Aggregates"
        monthly_name = "Monthly"
        monthly_title = "Billing Monthly"

        n_cols = len(self.ddh.header)
        table_width = n_cols + self.cell_spacing

        aggs_ddh = self.group_by_lineitem()

        self.put_label(book, sheet, aggs_title, left=table_width)

        self.put_table(
            book, sheet, aggs_ddh, self.cell_spacing, table_width, aggs_name
        )

        aggs_n_rows = len(aggs_ddh.data)
        aggs_table_height = aggs_n_rows + self.cell_spacing
        monthly_ddh = self.group_by_month()
        monthly_top = 1 + aggs_table_height + self.cell_spacing # Account for label

        self.put_label(
            book, sheet, monthly_title, top=monthly_top, left=table_width
        )

        table_top = monthly_top + self.cell_spacing
        self.put_table(
            book, sheet, monthly_ddh, table_top, table_width, monthly_name
        )

        return sheet
