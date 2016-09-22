import json

class DecimalEncoder(json.JSONEncoder):
    """Serialize decimal.Decimal objects into JSON as floats."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

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
