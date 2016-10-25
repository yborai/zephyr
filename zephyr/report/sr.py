import sqlite3
import pandas as pd
import xlsxwriter

from .common import insert_label
from ..data.service_requests import ServiceRequests


def create_headers(workbook, headers, total_row, formatting=None):
    header_format = workbook.add_format(formatting)
    header = [{"header": col, "header_format": header_format} for col in headers]
    if total_row:
        header[0]["total_string"] = "Total"
        header[1]["total_function"] = "sum"
    return header

def group_data(header, data, review_type):
    con = sqlite3.connect(":memory:")
    srs = pd.DataFrame(data, columns=header)

    sr_sql = srs.to_sql("srs", con, if_exists="replace")
    query = """
        SELECT
             {col},
             count({col}) as Total 
         FROM
             srs
         GROUP BY {col}
    """.format(col=review_type)
    
    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

def service_request_xlsx(workbook=None, json_string=None, formatting=None):
    info = ServiceRequests(json_string).to_ddh()
    title = "Service Requests"
    if not workbook:
        options = formatting["wkbk_options"]
        with xlsxwriter.Workbook("srs.xlsx", workbook_options) as workbook:
            return write_xlsx(workbook, info, title, formatting=formatting)
    return write_xlsx(workbook, info, title, formatting=formatting)

def write_grouped_tables(workbook, worksheet, review_type, start_row, start_col, instance, formatting=None):
    headers, data = group_data(instance.header, instance.data, review_type)
    header = create_headers(workbook, headers, True, formatting=formatting)
    row_index = start_row
    for row in data:
        column_index = start_col
        for col in row:
            worksheet.write(row_index+1, column_index, col)
            column_index += 1
        row_index += 1
    worksheet.add_table(
        start_row, start_col, row_index+1, column_index-1,
        {
            "columns": header, "name": review_type,
            "style": "Table Style Light 1", "total_row": True
        }
    )
    chart = workbook.add_chart({"type": "pie"})
    chart.add_series(
        {
            "categories": [
                "Service Requests", start_row+1, start_col, row_index, start_col
            ],
            "values": [
                "Service Requests", start_row+1, column_index-1, row_index, column_index-1
            ],
            "data_labels": {
                "category": True, "percentage": True, "position": "outside_end"
            }
        }
    )

    chart.set_title({"name": review_type})
    chart.set_legend({"none": True})

    return chart


def write_xlsx(workbook, instance, title, formatting=None):
    cell = formatting["cell_options"]
    chart = formatting["chart_options"]
    chart_width_cell = chart["width"]/cell["width"]
    chart_height_cell = chart["height"]/cell["height"]

    current_worksheet = workbook.add_worksheet(title)
    row_index = 1
    insert_label(workbook, current_worksheet, 0, 0, title)
    header = create_headers(workbook, instance.header, False)
    for row in instance.data:
        column_index = 0
        for col in row:
            current_worksheet.write(row_index+1, column_index, col)
            column_index += 1
        row_index += 1
    current_worksheet.add_table(1, 0, row_index, column_index-1,
        {
            "columns": header, "name": "SRs", 
            "style": "Table Style Light 1", "total_row": False
        }
    )

    table_height = row_index + 1
    cell_spacing = 1
    chart_start_row = table_height + cell_spacing
    chart_row_index = chart_start_row + int(chart_height_cell) + 1
    chart_col_index = int(chart_width_cell) + 1

    insert_label(
        workbook, current_worksheet, table_height, chart_col_index, "Summary"
    )

    area_chart = write_grouped_tables(
        workbook, current_worksheet, "Area", chart_start_row,
        chart_col_index, instance
    )
    current_worksheet.insert_chart(chart_start_row, 0, area_chart)


    severity_chart = write_grouped_tables(
        workbook, current_worksheet, "Severity", chart_row_index,
        chart_col_index, instance
    )
    current_worksheet.insert_chart(chart_row_index, 0, severity_chart)

    return current_worksheet
