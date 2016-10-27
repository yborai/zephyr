import xlsxwriter

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

def service_request_xlsx(workbook=None, json_string=None, formatting=None):
    info = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    if not workbook:
        options = formatting["wkbk_options"]
        with xlsxwriter.Workbook("srs.xlsx", options) as workbook:
            return write_xlsx(workbook, info, title, formatting)
    return write_xlsx(workbook, info, title, formatting)

def write_grouped_table(
        workbook, worksheet, review_type, start_row, start_col,
        instance, formatting=None
    ):
    headers, data = group_data(instance.header, instance.data, review_type)

    header_format = formatting["header_format"]
    table_options = formatting["table_options"]
    legend_options = formatting["legend_options"]

    header = create_headers(workbook, headers, header_format)

    table_format = dict(
        columns=header,
        name=review_type,
        style=table_options["style"],
        total_row=table_options["total_row_t"],
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


def write_xlsx(workbook, instance, title, formatting=None):
    table_options = formatting["table_options"]

    cell = formatting["cell_options"]
    chart = formatting["chart_options"]
    chart_width = chart["width"]/cell["width"]
    chart_height = chart["height"]/cell["height"]

    header_format = formatting["header_format"]
    header_format["total_row"] = False
    header = create_headers(workbook, instance.header, header_format)

    table_format = dict(
        columns=header,
        name="SRs",
        style=table_options["style"],
        total_row=table_options["total_row_f"],
    )

    current_worksheet = workbook.add_worksheet(title)
    insert_label(workbook, current_worksheet, 0, 0, title, formatting)

    row_index = 1
    for row in instance.data:
        column_index = 0
        for col in row:
            current_worksheet.write(row_index+1, column_index, col)
            column_index += 1
        row_index += 1

    current_worksheet.add_table(1, 0, row_index, column_index-1, table_format)

    table_height = row_index + 1
    cell_spacing = 1
    chart_start_row = table_height + cell_spacing
    chart_row_index = chart_start_row + int(chart_height) + 1
    chart_col_index = int(chart_width) + 1

    header_format["total_row"] = True
    insert_label(
        workbook,
        current_worksheet,
        table_height,
        chart_col_index,
        "Summary",
        formatting
    )

    area_chart = write_grouped_table(
        workbook,
        current_worksheet,
        "Area",
        chart_start_row,
        chart_col_index,
        instance,
        formatting
    )

    current_worksheet.insert_chart(chart_start_row, 0, area_chart)

    severity_chart = write_grouped_table(
        workbook,
        current_worksheet,
        "Severity",
        chart_row_index,
        chart_col_index,
        instance,
        formatting
    )

    current_worksheet.insert_chart(chart_row_index, 0, severity_chart)

    return current_worksheet
