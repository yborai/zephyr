import csv
import io
import json

import texttable

from .utils import ZephyrEncoder

class DDH(object):
    def __init__(self, header=None, data=None):
        self.header = header or []
        self.data = data or []

    @classmethod
    def read_sql(cls, query, connection):
        cur = connection.cursor()
        cur.execute(query)
        header = list(zip(*cur.description))[0]
        data = cur.fetchall()
        return cls(header=header, data=data)

    @staticmethod
    def _discard_keys(kwargs, keys):
        for key in keys:
            if(key in kwargs):
                del(kwargs[key])
        return kwargs

    def to_csv(self, *args, **kwargs):
        kwargs = self._discard_keys(kwargs, ("line_width", "template"))
        fieldnames = self.header
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fieldnames, *args, **kwargs)
        writer.writeheader()
        for row in self.data:
            writer.writerow(dict(zip(fieldnames, row)))
        return out.getvalue()

    def to_json(self, *args, **kwargs):
        kwargs = self._discard_keys(kwargs, ("line_width", "template"))
        out = dict(header=self.header, data=self.data)
        return json.dumps(out, cls=ZephyrEncoder, *args, **kwargs)

    def to_table(self, *args, **kwargs):
        kwargs = self._discard_keys(kwargs, ("template"))
        ncols = len(self.header)
        col_width = max(int(kwargs.get("line_width", 120)/ncols), 8)
        rows = sum([[self.header], self.data], [])
        out = texttable.Texttable()
        out.set_cols_dtype(["t"]*ncols)
        out.set_cols_width((col_width,)*ncols)
        out.add_rows(rows)
        return "".join([out.draw(), "\n"])
