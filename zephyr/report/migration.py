import xlsxwriter

from ..core.cc.calls import ComputeMigrationWarp
from .common import (
    put_label,
    put_table,
)

def migration_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of SRs in an Excel workbook."""
    ddh = ComputeMigrationWarp(json_string).to_ddh()
    if not ddh.data:
        return False
    title = "EC2 Migration Recommendations"
    name = "Migration"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("underutilized.xlsx", options) as book:
            return migration_sheet(book, ddh, title, name=name, formatting=formatting)
    return migration_sheet(book, ddh, title, name=name, formatting=formatting)

def migration_sheet(book, ddh, title, name=None, formatting=None):
    """Format the sheet and insert the data for the SR report."""
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    put_label(book, sheet, title, formatting=formatting)

    put_table(
        book, sheet, ddh, top=1, name=name, formatting=formatting
    )
