"""
Common code for zephyr report
"""

import os
import sqlite3
import pandas as pd
import xlsxwriter

from decimal import Decimal
from ..core.ddh import DDH

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
    "pie_chart" : {
        "type" : "pie",
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
    "book_options" : {
        "strings_to_numbers": True,
    },
}

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

def clean_data(data):
    new_data = []
    for row in data:
        new_row = []
        for cell in row:
            if isinstance(cell, Decimal):
                new_row.append(float(cell))
                continue
            new_row.append(cell)
        new_data.append(new_row)
    return new_data

def count_by(header, data, column):
    """Count rows in data grouping by values in the column specified"""
    con = sqlite3.connect(":memory:")
    df = pd.DataFrame(data, columns=header)
    df.to_sql("df", con, if_exists="replace")
    if column != "Status" and ("running" or "stopped") in data[0]:
        query = """
            SELECT
                 {col},
                 COUNT({col}) as Total
             FROM df
             WHERE Status = "running"
             GROUP BY {col}
             ORDER BY COUNT({col}) DESC
        """.format(col=column)
    else:
        query = """
            SELECT
                 {col},
                 COUNT({col}) as Total
             FROM df
             GROUP BY {col}
             ORDER BY COUNT({col}) DESC
        """.format(col=column)

    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

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
    put_chart(book, sheet, column_name, top, left, table_loc, "pie", formatting)
    return book

def header_format_xlsx(headers, header_format, total_row):
    """Create the header format dict for Xlsxwriter."""
    header = [{"header": col, "header_format": header_format} for col in headers]
    [header[i].update(total_row[i]) for i in range(len(total_row))]
    return header

def put_chart(book, sheet, title, top, left, data_loc, chart_type, formatting):
    """Add a chart to an xlsx workbook located at data_loc."""
    chart = book.add_chart(dict(type=chart_type))
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

def put_two_series_chart(book, sheet, title, top, left, data_loc, chart_type, formatting):
    """Add RI chart to an xlsx workbook located at data_loc."""
    chart = book.add_chart(dict(type=chart_type))
    legend_options = formatting["legend_options"]
    top_, bottom, col_keys, col_values = data_loc

    # Add first column
    series_categories = [sheet.name, top_, col_keys, bottom, col_keys]
    series1_values = [sheet.name, top_, col_values-1, bottom, col_values-1] # Looks at first column
    series1 = dict(
        categories=series_categories,
        values=series1_values,
        data_labels=formatting["data_labels"],
    )
    chart.add_series(series1)

    # Add the second column
    series2_values = [sheet.name, top_, col_values, bottom, col_values]
    series2 = dict(
        categories=series_categories,
        values=series2_values,
        data_labels=formatting["data_labels"],
    )
    chart.add_series(series2)

    chart.set_title({"name": title})
    chart.set_legend(legend_options)
    sheet.insert_chart(top, left, chart)
    return sheet

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
