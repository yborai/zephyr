"""
Common code for zephyr
"""
import datetime

from decimal import Decimal

DAY = datetime.timedelta(days=1)

def end_of_month_before(date):
    """
    Takes a datetime and returns the datetime
    for the last day of the previous month.
    """
    date_y, date_m = date.year, date.month
    fom = datetime.datetime(year=date_y, month=date_m, day=1)
    return fom - DAY

def month_range(date):
    """
    Returns a tuple of datetimes corresponding to
    the extreme dates in a month given a date.
    As an example 1955-11-05 would give (1955-11-01, 1955-11-30).
    """
    dy, dm = date.year, date.month
    begin_dt = datetime.datetime(year=dy, month=dm, day=1)
    month_next = begin_dt + DAY * 31  # a day in the month after report_begin
    nmy, nmm = month_next.year, month_next.month
    # last day of report date month
    end_dt = datetime.datetime(year=nmy, month=nmm, day=1) - DAY
    return (begin_dt, end_dt)

def percent(numer, denom, digits=2):
    return round(Decimal(100.) * numer / denom, digits)

def rows_to_excel(workbook, sheet, rows, table_name, top=1, left=0):
    """
    Take rows, an iterable of iterables, and write it to a given sheet
    with the top, left cell at (top, left).
    """
    headers = rows[0]
    header_format = workbook.add_format({"font_color": "#000000", "bg_color": "#DCE6F1", "bottom": 2})
    header = [{"header": name, "header_format": header_format} for name in headers]
    n_rows = len(rows)
    n_cells = len(rows[0])
    for i in range(n_rows):
        row = rows[i]
        for j in range(n_cells):
            sheet.write(top+i, left+j, row[j])
    sheet.add_table(top, left, top+i, left+j,
        {
            "columns": header, "name": table_name,
            "style": "Table Style Light 1"
        }
    )
