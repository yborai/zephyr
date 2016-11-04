import xlsxwriter

from ..core.ddh import DDH
from ..data.service_requests import ServiceRequests
from .common import ( 
    book_formats,
    chart_dimensions,
    count_by,
    count_by_pie_chart,
    header_format_xlsx,
    put_chart,
    put_label,
    put_table,
    rows_to_excel
)

def sr_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of SRs in an Excel workbook."""
    ddh = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    name = "SRs"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("srs.xlsx", options) as book:
            return sr_sheet(book, ddh, title, name=name, formatting=formatting)
    return sr_sheet(book, ddh, title, name=name, formatting=formatting)

def sr_sheet(book, ddh, title, name=None, formatting=None):
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
    table_left = int(chart_width) + cell_spacing
    chart_ceil = int(chart_height) + 1

    # Insert SRs by Area pie chart.
    count_by_pie_chart(
        book, sheet, "Area", ddh, chart_start_row, 0, "sr_area", formatting=formatting,
    )

    # Place SRs by Severity pie chart
    severity_top = chart_start_row + chart_ceil + cell_spacing
    count_by_pie_chart(
        book, sheet, "Severity", ddh, severity_top, 0, "sr_sev", formatting,
    )
    return sheet
