import xlsxwriter

from ..data.compute_underutilized import ComputeUnderutilizedWarp
from ..data.compute_underutilized_breakdown import ComputeUnderutilizedBreakdownWarp
from .common import (
    put_label,
    put_table,
)

def underutil_xlsx(book=None, json_string=None, define_category_func=None, formatting=None):
    """Save a list of SRs in an Excel workbook."""
    ddh = ComputeUnderutilizedWarp(json_string).to_ddh()
    if not ddh.data:
        return False
    if define_category_func:
        breakdown_ddh = ComputeUnderutilizedBreakdownWarp(
            json_string, define_category_func
        ).to_ddh()
    title = "EC2 Underutilized Instances"
    name = "Underutil"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("underutilized.xlsx", options) as book:
            return underutil_sheet(book, ddh, breakdown_ddh, title, name=name, formatting=formatting)
    return underutil_sheet(book, ddh, breakdown_ddh, title, name=name, formatting=formatting)

def underutil_sheet(book, ddh, breakdown_ddh, title, name=None, formatting=None):
    """Format the sheet and insert the data for the SR report."""
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    put_label(book, sheet, title, formatting=formatting)

    put_table(
        book, sheet, ddh, top=1, name=name, formatting=formatting
    )

    put_label(
        book, sheet, title, left=8, formatting=formatting
    )

    put_table(
        book, sheet, breakdown_ddh, top=1, left=8, name="Breakdown", formatting=formatting
    )
