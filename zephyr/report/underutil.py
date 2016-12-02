import xlsxwriter

from ..core.cc.calls import ComputeUnderutilizedWarp
from .common import (
    put_label,
    put_table,
)

def underutil_xlsx(book=None, json_string=None, define_category_func=None, formatting=None):
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

    return sheet
