import datetime
import json

from decimal import Decimal

DAY = datetime.timedelta(days=1)

class ZephyrEncoder(json.JSONEncoder):
    """Serialize decimal.Decimal objects into JSON as floats."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d")
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class ZephyrException(Exception):
    pass

def first_of_previous_month(date=None):
	if not date:
		date = datetime.datetime.now()
	fom = datetime.datetime(year=date.year, month=date.month, day=1)
	dlm = fom - DAY
	return datetime.datetime(year=dlm.year, month=dlm.month, day=1)

def get_config_values(section, keys, config):
    """Get a list of configuration values from the same section."""
    return [config.get(section, key) for key in keys]

def timed(func, log=None):
    """
    Wrap a function in a timer.
    """
    if log is None:
        log = print
    def timed_func(*args, **kwargs):
        now = datetime.datetime.now
        s_0 = now()
        value = func(*args, **kwargs)
        s_1 = now()
        log("%s" % (s_1 - s_0))
        return value
    return timed_func
