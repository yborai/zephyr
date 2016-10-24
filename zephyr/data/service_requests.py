import csv
import json
from collections import OrderedDict

from ..core.ddh import DDH

class ServiceRequests(object):
    header_hash = OrderedDict([
        ("summary", "Summary"),
        ("status", "Status"),
        ("severity", "Severity"),
        ("area", "Area"),
        ("created_date", "Created Date"),
        ("created_by", "Created By"),
    ])

    def __init__(self, json_string):
        self.response = json.loads(json_string)
        header_raw = self.response["header"]
        data_raw = self.response["data"]

        self.header = list(self.header_hash.values())
        self.column_indexes = [header_raw.index(key) for key in list(self.header_hash.keys())]
        self.data = [[row[index] for index in self.column_indexes] for row in data_raw]

    def to_ddh(self):
        header = self.header
        data = self.data

        return DDH(header=header, data=data)


