import sqlite3
import pandas as pd

from ...report.common import (
    chart_dimensions,
    put_label,
    put_table,
)
from ..ddh import DDH
from ..report import Report
from .calls import Billing

class ReportBilling(Report):
    name = "Billing"
    title = "Billing Line Items"
    cls = Billing

    def group_by_lineitem(self, header, data):
        """Groups rows by line item"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(data, columns=header)
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

    def group_by_month(self, header, data):
        """Groups rows by month"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(data, columns=header)
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

    def sheet(self, book, ddh, title, name=None, formatting=None):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(title)
        put_label(book, sheet, title, formatting=formatting)

        put_table(
            book, sheet, ddh, top=1, name=name, formatting=formatting
        )

        cell_spacing = 1
        aggs_name = "Aggregates"
        aggs_title = "Billing Line Item Aggregates"
        monthly_name = "Monthly"
        monthly_title = "Billing Monthly"

        n_cols = len(ddh.header)
        table_width = n_cols + cell_spacing

        aggs_ddh = self.group_by_lineitem(ddh.header, ddh.data)

        put_label(
            book, sheet, aggs_title, left=table_width, formatting=formatting
        )

        put_table(
            book, sheet, aggs_ddh, cell_spacing, table_width, aggs_name, formatting
        )

        aggs_n_rows = len(aggs_ddh.data)
        aggs_table_height = aggs_n_rows + cell_spacing
        monthly_ddh = self.group_by_month(ddh.header, ddh.data)
        monthly_top = 1 + aggs_table_height + cell_spacing # Account for label

        put_label(
            book, sheet, monthly_title, top=monthly_top, left=table_width, formatting=formatting
        )

        table_top = monthly_top + cell_spacing
        put_table(
            book, sheet, monthly_ddh, table_top, table_width, monthly_name, formatting
        )

        return sheet

    def _xlsx(self, *args, **kwargs):
        return self.sheet(*args, **kwargs)

