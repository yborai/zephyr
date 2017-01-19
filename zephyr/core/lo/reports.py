from ..ddh import DDH
from ..report import Report
from .calls import ServiceRequests

class ReportSRs(Report):
    name = "SRs"
    title = "Service Requests"
    cls = ServiceRequests

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        # Where do charts and other tables go?
        n_rows = len(ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing # Label, table, spacing
        chart_ceil = self.chart_height + 1

        # Insert SRs by Area pie chart.
        self.count_by_pie_chart(
            book, sheet, "Area", ddh, chart_start_row, 0, "sr_area"
        )

        # Place SRs by Severity pie chart
        severity_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            book, sheet, "Severity", ddh, severity_top, 0, "sr_sev"
        )
        return sheet