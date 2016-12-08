from operator import itemgetter
import sqlite3
import pandas as pd
import xlsxwriter

from ..core.ddh import DDH
from ..core.cc.calls import ComputeRIWarp
from .common import (
    chart_dimensions,
    clean_data,
    put_label,
    put_table,
    put_two_series_chart,
)

def ri_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of EC2 instances in an Excel workbook."""
    ddh = ComputeRIWarp(json_string).to_ddh()
    if not ddh.data:
        return False
    title = "EC2 RI Recommendations"
    name = "RIs"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("ri_recs.xlsx", options) as book:
            return ri_sheet(book, ddh, title, name=name, formatting=formatting)
    return ri_sheet(book, ddh, title, name=name, formatting=formatting)

def ri_sheet(book, ddh, title, name=None, formatting=None):
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

    sum_by_column_chart(
        book, sheet, "Annual Savings", ddh, chart_start_row, 0, "ri_savings", formatting
    )
    return sheet

def sum_by(header, data):
    """Sum rows in data grouping by values in the column specified"""
    # Create data with correct float values

    new_data = clean_data(data)

    con = sqlite3.connect(":memory:")
    df = pd.DataFrame(new_data, columns=header)
    df.to_sql("df", con, if_exists="replace")
    query = """
        SELECT
            "Instance Type",
            SUM("On-Demand Monthly Cost"*12) AS "On-Demand Instance Cost",
            SUM("Reserved Monthly Cost"*12+"Upfront RI Cost") AS "RI Cost"
        FROM df
        GROUP BY "Instance Type"
        ORDER BY "On-Demand Instance Cost" DESC
    """

    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data_ = [list(row) for row in sql_group.values]

    return header, data_

def sum_by_column_chart(
    book, sheet, column_name, ddh, top, left, name, formatting
):
    """Insert a column chart with data specified."""
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    table_left = int(chart_width) + cell_spacing
    table_top = top + 1 # Account for label.

    # Get first 4 data rows
    header, data_ = sum_by(ddh.header, ddh.data)
    data = data_[:4]

    # Rollup remaining values into "other" column
    od_cost_values = [item[1] for item in data_[:4]]
    ri_cost_values = [item[2] for item in data_[:4]]
    other_row = ["Other", sum(od_cost_values), sum(ri_cost_values)]

    # Append data
    data.append(other_row)
    data = sorted(data, key=itemgetter(1), reverse=True)
    sums = DDH(header=header, data=data)

    put_label(book, sheet, column_name, top, table_left, formatting=formatting)

    # Write the data table to the sheet.
    sheet = put_table(
        book,
        sheet,
        sums,
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
    ccf = dict(
        legend_options=formatting["legend_options"],
        data_labels=dlf
    )
    put_two_series_chart(book, sheet, column_name, top, left, table_loc, "column", ccf)
    return book
