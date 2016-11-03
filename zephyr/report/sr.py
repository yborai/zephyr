import xlsxwriter

from ..core.ddh import DDH
from ..data.service_requests import ServiceRequests
from .common import count_by, rows_to_excel

def book_formats(book, formatting):
    table = formatting["table_style"]
    header_format = book.add_format(formatting["header_format"])
    cell_format = book.add_format(formatting["label_format"])
    return table, header_format, cell_format

def chart_dimensions(formatting):
    """Compute chart dimensions from a formatting specification. """
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

    # Aggregate the data, grouping by the given column_name
    header, data = count_by(ddh.header, ddh.data, column_name)
    counts = DDH(header=header, data=data)

    # Write the data table to the sheet
    sheet = put_table(
        book,
        sheet,
        counts,
        top=top,
        left=table_left,
        title=column_name,
        name=name,
        formatting=formatting,
    )

    # Compute series location.
    table_header_top = top + 1 # Account for label from put_table.
    table_loc = (
        table_header_top + 1, # Start of data series, accounting for header
        table_header_top + len(data),
        table_left,
        table_left + 1,
    )
    put_chart(book, sheet, column_name, top, left, table_loc, formatting)
    return book

def header_format_xslx(headers, header_format, total_row):
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

def put_table(
    book, sheet, table, top=0, left=0, title=None, name=None, formatting=None,
):
    # Configure formatting
    table_fmt, header_format, cell_format = book_formats(book, formatting)

    # Create label with cell_format
    sheet.write(top, left, title, cell_format)

    # Write data to sheet
    sheet = rows_to_excel(sheet, table.data, top=top+2, left=left)

    # Create format dict for xlsxwriter
    total_row = []
    header = header_format_xslx(table.header, header_format, total_row)
    table_format = dict(
        columns=header,
        name=name,
        style=table_fmt["style"],
        total_row=bool(total_row),
    )

    # Compute dimensions of Excel table
    n_rows = len(table.data)
    n_cols = len(table.data[0])

    # Tell Excel this array is a table.
    sheet.add_table(top+1, left, n_rows+top+1, n_cols+left-1, table_format)
    return sheet

def sr_xlsx(book=None, json_string=None, formatting=None):
    info = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    name = "SRs"
    if not book:
        options = formatting["wkbk_options"]
        with xlsxwriter.Workbook("srs.xlsx", options) as book:
            return sr_sheet(book, info, title, name=name, formatting=formatting)
    return sr_sheet(book, info, title, name=name, formatting=formatting)

def sr_sheet(book, ddh, title, name=None, formatting=None):
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    sheet = put_table(
        book, sheet, ddh, title=title, name=name, formatting=formatting
    )

    # Where do charts and other tables go?
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    n_rows = len(ddh.data)
    table_height = n_rows + 1
    chart_start_row = table_height + cell_spacing + 1
    chart_row_index = chart_start_row + int(chart_height) + 1
    table_left = int(chart_width) + cell_spacing

    # Insert SRs by Area pie chart.
    count_by_pie_chart(
        book, sheet, "Area", ddh, chart_start_row, 0, "sr_area", formatting=formatting,
    )

    # Place SRs by Severity pie chart
    severity_top = chart_start_row + int(chart_height) + 1 + cell_spacing + 1
    count_by_pie_chart(
        book, sheet, "Severity", ddh, severity_top, 0, "sr_sev", formatting,
    )
    return sheet
