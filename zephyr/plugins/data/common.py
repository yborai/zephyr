"""
Common code for zephyr
"""
import datetime
import json

from decimal import Decimal

from cement.core import controller

DAY = datetime.timedelta(days=1)

class DecimalEncoder(json.JSONEncoder):
    """Serialize decimal.Decimal objects into JSON as floats."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

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

def timed(func):
    """
    Wrap a function in a timer.
    """
    def timed_func(*args, **kwargs):
        now = datetime.datetime.now
        s_0 = now()
        value = func(*args, **kwargs)
        s_1 = now()
        print('%s' % (s_1 - s_0))
        return value
    return timed_func

class ToolkitDataController(controller.CementBaseController):
    class Meta:
        label = 'data'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Generate single table reports for an account."
        arguments = controller.CementBaseController.Meta.arguments + [(
            ["--config"], dict(
                type=str,
                help="Path to configuration file"
            )
        ),]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.print_help()
