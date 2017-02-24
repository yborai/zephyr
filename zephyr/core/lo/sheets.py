from ..sheet import Sheet
from .calls import ServiceRequests


class SheetSRs(Sheet):
    name = "SRs"
    title = "Service Requests"
    calls = (ServiceRequests,)

    def to_xlsx(self, book, **kwargs):
        """Format the SR sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        self.put_table(self.ddh, top=1, name=self.name)

        # Where do charts and other tables go?
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        # Label, table, spacing
        chart_start_row = 1 + table_height + self.cell_spacing
        chart_ceil = self.chart_height + 1

        # Insert SRs by Area pie chart.
        self.count_by_pie_chart("Area", chart_start_row, 0, "sr_area")

        # Place SRs by Severity pie chart
        severity_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart("Severity", severity_top, 0, "sr_sev")
        return self.sheet
