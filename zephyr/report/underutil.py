import sqlite3
import xlsxwriter
import pandas as pd

from ..core.ddh import DDH
from ..core.cc.calls import ComputeUnderutilizedWarp
from .common import (
    clean_data,
    put_label,
    put_table,
)

def underutil_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of SRs in an Excel workbook."""
    ddh = ComputeUnderutilizedWarp(json_string).to_ddh()
    if not ddh.data:
        return False
    title = "EC2 Underutilized Instances"
    name = "Underutil"

    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("underutilized.xlsx", options) as book:
            return underutil_sheet(book, ddh, title=title, name=name, formatting=formatting)
    return underutil_sheet(book, ddh, title=title, name=name, formatting=formatting)

def underutil_sheet(book, ddh, title=None, name=None, formatting=None):
    """Format the sheet and insert the data for the SR report."""
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    put_label(book, sheet, title, formatting=formatting)

    put_table(
        book, sheet, ddh, top=1, name=name, formatting=formatting
    )

    cell_spacing = 2 # Extra spacing before breakdown
    breakdown_title = "EC2 Underutilized Instance Breakdown"
    breakdown_name = "Breakdown"
    breakdown_left = len(ddh.data[0]) + cell_spacing

    put_label(
        book, sheet, breakdown_name, left=breakdown_left, formatting=formatting
    )

    header, data_ = get_category(ddh.header, ddh.data)
    data = remove_repeated_names(data_)

    ddh = DDH(header=header, data=data)

    put_table(
        book, sheet, ddh, 1, breakdown_left, breakdown_name, formatting
    )

    return sheet


def get_category(header, data):
    """Returns the underutilized breakdown dataset including the category column."""
    con = sqlite3.connect(":memory:")
    data_ = clean_data(data)
    df = pd.DataFrame(data_, columns=header)
    df.to_sql("df", con, if_exists="replace", index=False)
    query = """
        SELECT
            substr("Instance Name", 0, instr("Instance Name", '-')) AS Category,
            *
        FROM df
        ORDER BY substr("Instance Name", 0, instr("Instance Name", '-'))
    """

    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

def remove_repeated_names(data):
    seen = set()
    with_tags = list()
    no_tags = list()
    for row in data:
        if "-" not in row[2]:
            no_tags.append(row)
            continue
        if row[0] not in seen:
            seen.add(row[0])
            with_tags.append(row)
            continue
        row[0] = ""
        with_tags.append(row)
    if(len(no_tags)):
        no_tags[0][0] = "No tag"

    out = with_tags + no_tags

    return out
