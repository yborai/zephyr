from ..report import Report
from .calls import ServiceRequests

class ReportSRs(Report):
    name = "SRs"
    title = "Service Requests"
    cls = ServiceRequests

    def to_xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        self.book = book

        # Insert raw report data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        # Retrieve the data if it does not exist yet.
        if(not self.ddh):
            self.to_ddh()

        self.put_table(self.ddh, top=1, name=self.name)

        # Where do charts and other tables go?
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing # Label, table, spacing
        chart_ceil = self.chart_height + 1

        # Insert SRs by Area pie chart.
        self.count_by_pie_chart("Area", chart_start_row, 0, "sr_area")

        # Place SRs by Severity pie chart
        severity_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart("Severity", severity_top, 0, "sr_sev")
        return self.sheet