from ...report.common import (
    chart_dimensions,
    put_label,
    put_table,
)
from ..report import Report
from .calls import Billing

class ReportBilling(Report):
    name = "Billing"
    title = "Billing"
    cls = Billing

    @staticmethod
    def sheet(book, ddh, title, name=None, formatting=None):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(title)
        put_label(book, sheet, title, formatting=formatting)

        put_table(
            book, sheet, ddh, top=1, name=name, formatting=formatting
        )

        # Where do charts and other tables go?
        chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
        n_rows = len(ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + cell_spacing # Label, table, spacing
        chart_ceil = int(chart_height) + 1

        return sheet

    def _xlsx(self, *args, **kwargs):
        return self.sheet(*args, **kwargs)

