from operator import itemgetter
import sqlite3
import pandas as pd
import xlsxwriter

from ..core.ddh import DDH
from ..core.cc.calls import DBDetailsWarp
from .common import (
    chart_dimensions,
    put_chart,
    put_label,
    put_table,
)

def rds_sheet(book, ddh, title, name=None, formatting=None):
    """Format the sheet and insert the data for the SR report."""
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    put_label(book, sheet, title, formatting=formatting)

    put_table(
        book, sheet, ddh, top=1, name=name, formatting=formatting
    )

    # Where charts and other tables go
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    n_rows = len(ddh.data)
    table_height = n_rows + 1
    chart_start_row = 1 + table_height + cell_spacing

    sum_and_count_by_column_chart(
        book, sheet, "DbInstanceClass", "MonthlyCost", ddh, chart_start_row, 0,
        "month_cost", formatting
    )

def rds_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of EC2 instances in an Excel workbook."""
    ddh = DBDetailsWarp(json_string).to_ddh()
    title = "RDS Details"
    name = "RDS"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("rds.xlsx", options) as book:
            return rds_sheet(book, ddh, title, name=name, formatting=formatting)
    return rds_sheet(book, ddh, title, name=name, formatting=formatting)

def sum_and_count_by(header, data, column_name, cost_column):
    """Count and sum rows in data grouping by values in the column specified"""
    con = sqlite3.connect(":memory:")
    df = pd.DataFrame(data, columns=header)
    df.to_sql("df", con, if_exists="replace")
    query = """
        SELECT
             {col},
             COUNT({col}) AS "Count",
             SUM({cost}) AS "Sum"
         FROM df
         GROUP BY {col}
         ORDER BY Sum DESC
    """.format(col=column_name, cost=cost_column)

    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

def sum_and_count_by_column_chart(
    book, sheet, column_name, cost_column, ddh, top, left, name, formatting
):
    """Insert a column chart with data specified."""
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    table_left = int(chart_width) + cell_spacing
    table_top = top + 1 # Account for label.

    header, data = sum_and_count_by(ddh.header, ddh.data, column_name, cost_column)

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
    # Compute series information.
    table_loc = (
        table_top + 1,
        table_top + len(data),
        table_left,
        table_left + 2, # Sum is the third column and is the data we are graphing.
    )
    # Create chart formatting
    dlf = dict()
    dlf.update(formatting["data_labels"])
    dlf["category"] = False
    dlf["value"] = True
    ccf = dict(
        legend_options=formatting["legend_options"],
        data_labels=dlf
    )
    put_chart(book, sheet, column_name, top, left, table_loc, "column", ccf)
    return book
