import os
import csv
import json
from datetime import datetime
from itertools import groupby

from .core import CoreProcessor


def create_sheet(json_string, csv_filename='service_requests.csv'):
    processor = ServiceRequestProcessor(json_string)
    return processor.write_csv(csv_filename)


class ServiceRequestProcessor(CoreProcessor):
    def __init__(self, json_string):
        parsed_result = json.loads(json_string)
        self.parsed_details = {"result": []}

        for row in parsed_result["data"]:
            self.parsed_details["result"].append(
                dict(zip(parsed_result["header"], row))
            )

        self.grouped_by_area = self._group_by_area()
        self.grouped_by_severity = self._group_by_severity()

    def write_csv(self, csv_filename):
        super().write_csv(csv_filename)
        area_csv_filepath = self._write_area_total_csv(csv_filename)
        severity_csv_filepath = self._write_severity_total_csv(csv_filename)

        return csv_filename, area_csv_filepath, severity_csv_filepath

    def _write_area_total_csv(self, csv_filename):
        area_csv_filepath = os.path.splitext(csv_filename)[0] + "_area_total.csv"
        with open(area_csv_filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=("category", "total"))

            writer.writeheader()
            grand_total_area = 0
            for area, rows in self.grouped_by_area:
                total = len(list(rows))
                grand_total_area += total
                writer.writerow({"category": area, "total": total})
            writer.writerow({"category": "Grand Total", "total": grand_total_area})

        return area_csv_filepath

    def _write_severity_total_csv(self, csv_filename):
        severity_csv_filepath = os.path.splitext(csv_filename)[0] + "_severity_total.csv"
        with open(severity_csv_filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=("severity", "total"))

            writer.writeheader()
            grand_total_severity = 0
            for severity, rows in self.grouped_by_severity:
                total = len(list(rows))
                grand_total_severity += total
                writer.writerow({"severity": severity, "total": total})
            writer.writerow({"severity": "Grand Total", "total": grand_total_severity})

        return severity_csv_filepath

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

        return self._format_datefields(filtered_row)

    def _group_by_area(self):
        rows = sorted(
            self.parsed_details[self._data_key()],
            key=lambda row: row["area"], reverse=False
        )
        return groupby(rows, lambda row: row["area"])

    def _group_by_severity(self):
        rows = sorted(
            self.parsed_details[self._data_key()],
            key=lambda row: row["severity"], reverse=False
        )
        return groupby(rows, lambda row: row["severity"])

    def _format_datefields(self, row):
        for datefields in self._datetime_fields():
            row[datefields] = datetime.strptime(
                row[datefields], '%Y-%m-%d %H:%M:%S'
            ).strftime('%m/%d/%y %H:%M')

        return row

    def _data_key(self):
        return "result"

    def _fieldnames(self):
        return (
            "summary", "status", "severity", "created_date", "created_by"
        )

    def _datetime_fields(self):
        return (
            "created_date",
        )
