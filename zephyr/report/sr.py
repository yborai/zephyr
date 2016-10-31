import xlsxwriter

from ..core.ddh import DDH
from ..data.common import rows_to_excel
from ..data.service_requests import ServiceRequests
from .common import insert_label, group_data


def create_headers(workbook, headers, formatting=None):
    hdr = {k:v for k,v in formatting.items() if k not in ["total_row"]}
    header_format = workbook.add_format(hdr)
    header = [{"header": col, "header_format": header_format} for col in headers]
    if formatting["total_row"]:
        header[0]["total_string"] = "Total"
        header[1]["total_function"] = "sum"
    return header

def service_request_xlsx(book=None, json_string=None, formatting=None):
    info = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    name = "SRs"
    if not book:
        options = formatting["wkbk_options"]
        with xlsxwriter.Workbook("srs.xlsx", options) as book:
            return write_xlsx(book, info, title, name=name, formatting=formatting)
    return write_xlsx(book, info, title, name=name, formatting=formatting)

def write_grouped_table(
        workbook, worksheet, column, start_row, start_col,
        instance, formatting=None
    ):
    headers, data = group_data(instance.header, instance.data, column)

    header_format = formatting["header_format"]
    table_style = formatting["table_style"]
    legend_options = formatting["legend_options"]

    header = create_headers(workbook, headers, header_format)

    table_format = dict(
        columns=header,
        name=column,
        style=table_style["style"],
        total_row=table_style["total_row"],
    )

    row_index = start_row
    for row in data:
        column_index = start_col
        for col in row:
            worksheet.write(row_index+1, column_index, col)
            column_index += 1
        row_index += 1

    worksheet.add_table(
        start_row,
        start_col,
        row_index+1,
        column_index-1,
        table_format
    )

    chart = workbook.add_chart(formatting["chart_type"])

    series_categories = [
        "Service Requests",
        start_row+1,
        start_col,
        row_index,
        start_col,
    ]
    series_values =[
        "Service Requests",
        start_row+1,
        column_index-1,
        row_index,
        column_index-1,
    ]
    series = dict(
        categories=series_categories,
        values=series_values,
        data_labels=formatting["data_labels"],
    )
    chart.add_series(series)

    chart.set_title({"name": review_type})
    chart.set_legend(legend_options)

    return chart


def table_options(formatting):
    table = formatting["table_style"]

    cell = formatting["cell_options"]
    chart = formatting["chart_options"]
    chart_width = chart["width"]/cell["width"]
    chart_height = chart["height"]/cell["height"]

    return table, chart_width, chart_height

def write_table(sheet, table, top=0, left=0, title=None, name=None, formatting=None, cell_format=None):
    table_fmt, chart_width, chart_height = table_options(formatting)

    header_format = formatting["header_format"]
    header_format["total_row"] = False
    header = create_headers(book, table.header, header_format)

    table_format = dict(
        columns=header,
        name=name,
        style=table_fmt["style"],
        total_row=table_fmt["total_row"],
    )

    sheet.write(top, left, title, cell_format)

    n_rows = len(table.data)
    n_cols = len(table.data[0])

    sheet = rows_to_excel(sheet, table.data)

    sheet.add_table(top+1, left, n_rows+top+1, n_cols, table_format)
    return sheet

def write_xlsx(book, instance, title, name=None, formatting=None):
    sheet = book.add_worksheet(title)
    cell_format = book.add_format(formatting["label_format"])

    sheet = write_table(sheet, instance, name=name, formatting=formatting, cell_format=cell_format)

    n_rows = len(instance.data)
    table_height = n_rows + 1
    cell_spacing = 1
    chart_start_row = table_height + cell_spacing
    chart_row_index = chart_start_row + int(chart_height) + 1
    chart_col_index = int(chart_width) + 1
    summary_left = chart_width + cell_spacing

    area_header, area_data = group_data(instance.header, instance.data, "Area")
    area_ddh = DDH(header=area_header, data=area_data)
    sheet = write_table(
        book,
        area_ddh,
        top=chart_start_row,
        left=summary_left,
        name="sr_area",
        formatting=formatting,
        cell_format=cell_format
    )

    header_format["total_row"] = True
    insert_label(
        book,
        sheet,
        table_height,
        chart_col_index,
        "Summary",
        formatting
    )

    area_chart = write_grouped_table(
        book,
        sheet,
        "Area",
        chart_start_row,
        chart_col_index,
        instance,
        formatting
    )

    sheet.insert_chart(chart_start_row, 0, area_chart)

    severity_chart = write_grouped_table(
        book,
        sheet,
        "Severity",
        chart_row_index,
        chart_col_index,
        instance,
        formatting
    )

    sheet.insert_chart(chart_row_index, 0, severity_chart)

    return sheet
