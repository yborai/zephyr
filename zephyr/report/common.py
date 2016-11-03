"""
Common code for zephyr report
"""

import os
import sqlite3
import pandas as pd
import xlsxwriter

# 480 x 288 is the default size of the xlsxwriter chart.
# 64 x 20 is the default size of each cell.
formatting = {
    "cell_options" : {
        "height" : 20,
        "width" : 64,
    },
    "chart_options" : {
        "height" : 288,
        "width" : 480,
    },
    "chart_type" : {
        "type" : "pie",
    },
    "data_labels": {
        "category": True,
        "percentage": True,
        "position": "outside_end",
    },
    "header_format" : {
        "font_color" : "#000000",
        "bg_color" : "#DCE6F1",
        "bottom" : 2,
    },
    "label_format" : {
        "bold": True,
        "font_size": 16,
        "font_color": "#000000",
    },
    "legend_options" : {
        "none" : True,
    },
    "table_style" : {
        "style" : "Table Style Light 1",
    },
    "titles" : {
        "Service Requests" : "srs",
        "EC2 Details" : "ec2",
    },
    "total_row" : [
        {"total_string" : "Total"},
        {"total_function" : "sum"},
    ],
    "wkbk_options" : {
        "strings_to_numbers": True,
    },
}

def group_data(header, data, column):
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
    """.format(col=column)

    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

def rows_to_excel(sheet, rows, top=1, left=0):
    """
    Take rows, an iterable of iterables, and write it to a given sheet
    with the top, left cell at (top, left).
    """
    n_rows = len(rows)
    n_cells = len(rows[0])
    for i in range(n_rows):
        row = rows[i]
        for j in range(n_cells):
            sheet.write(top+i, left+j, row[j])
    return sheet
