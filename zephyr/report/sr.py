import xlsxwriter

from ..core.ddh import DDH
from ..data.service_requests import ServiceRequests
from .common import count_by, rows_to_excel

def book_formats(book, formatting):
    """Get format objects from book."""
    table = formatting["table_style"]
    header_format = book.add_format(formatting["header_format"])
    cell_format = book.add_format(formatting["label_format"])
    return table, header_format, cell_format

def chart_dimensions(formatting):
    """Compute chart dimensions from a formatting specification."""
    cell = formatting["cell_options"]
    chart = formatting["chart_options"]
    chart_width = chart["width"]/cell["width"]
    chart_height = chart["height"]/cell["height"]
    cell_spacing = 1
    return chart_width, chart_height, cell_spacing

def count_by_pie_chart(
    book, sheet, column_name, ddh, top, left, name, formatting
):
    """Insert a pie chart with data specified."""
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    table_left = int(chart_width) + cell_spacing
    table_top = top + 1 # Account for label.

    # Aggregate the data, grouping by the given column_name.
    header, data = count_by(ddh.header, ddh.data, column_name)
    counts = DDH(header=header, data=data)

    put_label(book, sheet, column_name, top, table_left, formatting=formatting)

    # Write the data table to the sheet.
    sheet = put_table(
        book,
        sheet,
        counts,
        top=table_top,
        left=table_left,
        name=name,
        formatting=formatting,
    )

    # Compute series location.
    table_loc = (
        table_top + 1, # Start of data series, accounting for header
        table_top + len(data),
        table_left,
        table_left + 1,
    )
    put_chart(book, sheet, column_name, top, left, table_loc, formatting)
    return book

def header_format_xlsx(headers, header_format, total_row):
    """Create the header format dict for Xlsxwriter."""
    header = [{"header": col, "header_format": header_format} for col in headers]
    [header[i].update(total_row[i]) for i in range(len(total_row))]
    return header

def put_chart(book, sheet, title, top, left, data_loc, formatting):
    """Add a chart to an xlsx workbook located at data_loc."""
    chart = book.add_chart(formatting["chart_type"])
    legend_options = formatting["legend_options"]
    top_, bottom, col_keys, col_values = data_loc

    series_categories = [sheet.name, top_, col_keys, bottom, col_keys]
    series_values = [sheet.name, top_, col_values, bottom, col_values]
    series = dict(
        categories=series_categories,
        values=series_values,
        data_labels=formatting["data_labels"],
    )
    chart.add_series(series)

    chart.set_title({"name": title})
    chart.set_legend(legend_options)
    sheet.insert_chart(top, left, chart)
    return sheet

def put_label(book, sheet, title, top=0, left=0, formatting=None):
    """Inserts a properly formatted label into a workbook."""
    # Configure formatting
    cell_format = book_formats(book, formatting)[2]

    # Create label with cell_format
    sheet.write(top, left, title, cell_format)
    return sheet

def put_table(
    book, sheet, ddh, top=0, left=0, name=None, formatting=None,
):
    """Creates an Excel table in a workbook."""
    # Configure formatting
    table_fmt, header_format, cell_format = book_formats(book, formatting)

    # Write data to sheet
    sheet = rows_to_excel(sheet, ddh.data, top=top+1, left=left)

    # Create format dict for xlsxwriter
    total_row = []
    header = header_format_xlsx(ddh.header, header_format, total_row)
    table_format = dict(
        columns=header,
        name=name,
        style=table_fmt["style"],
        total_row=bool(total_row),
    )

    # Compute dimensions of Excel table
    n_rows = len(ddh.data)
    n_cols = len(ddh.data[0])

    # Tell Excel this array is a table. Note: Xlsxwriter is 0 indexed.
    sheet.add_table(top, left, top + n_rows, left + n_cols - 1, table_format)
    return sheet

def sr_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of SRs in an Excel workbook."""
    ddh = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    name = "SRs"
    if not book:
        options = formatting["wkbk_options"]
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
