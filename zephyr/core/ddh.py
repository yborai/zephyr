import csv
import io
import json

from .utils import DecimalEncoder

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

    def to_csv(self, *args, **kwargs):
        if("template" in kwargs):
            del(kwargs["template"])
        fieldnames = self.header
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=fieldnames, *args, **kwargs)
        writer.writeheader()
        for row in self.data:
            writer.writerow(dict(zip(fieldnames, row)))
        return out.getvalue()

    def to_json(self, *args, **kwargs):
        if("template" in kwargs):
            del(kwargs["template"])
        out = dict(header=self.header, data=self.data)
        return json.dumps(out, cls=DecimalEncoder, *args, **kwargs)

