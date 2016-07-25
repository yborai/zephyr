import os
import csv
import json
from datetime import datetime
from itertools import groupby

from cement.core import controller
from .core import Sheet
from .common import ToolkitDataController


class ToolkitServiceRequests(ToolkitDataController):
    class Meta:
        label = "service-requests"
        stacked_on = "data"
        stacked_type = "nested"
        description = "get the detailed service requests meta information."

        arguments = ToolkitDataController.Meta.arguments #+[(
        #    ["--cc_api_key"], dict (
        #        type=str,
        #        help="The CloudCheckr API key to use."
        #        )
        #)]

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # we will add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache,"r") as f:
            response = f.read()
        sheet = ServiceRequestSheet(response)
        self.app.render(sheet.get_data())

def create_sheet(json_string, csv_filename='service_requests.csv'):
    processor = ServiceRequestSheet(json_string)
    return processor.write_csv(csv_filename)


class ServiceRequestSheet(Sheet):
    def __init__(self, json_string):
        parsed_result = json.loads(json_string)
        self.parsed_details = {"result": []}

        for row in parsed_result["data"]:
            self.parsed_details["result"].append(
                dict(zip(parsed_result["header"], row))
            )

        self.grouped_by_area = self._group_by("area")
        self.grouped_by_severity = self._group_by("severity")

    def write_csv(self, csv_filename):
        super().write_csv(csv_filename)

        area_csv_filepath = self._write_grouped_review_csv(
            csv_filename, "area", self.grouped_by_area
        )
        severity_csv_filepath = self._write_grouped_review_csv(
            csv_filename, "severity", self.grouped_by_severity
        )

        return csv_filename, area_csv_filepath, severity_csv_filepath

    def _write_grouped_review_csv(self, csv_filename, review_type, data):
        review_csv_filepath = os.path.splitext(csv_filename)[0] + "_" + review_type + "_total.csv"
        with open(review_csv_filepath, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=(review_type, "total"))

            writer.writeheader()
            grand_total = 0
            for grouper, rows in data:
                total = len(list(rows))
                grand_total += total
                writer.writerow({review_type: grouper, "total": total})
            writer.writerow({review_type: "Grand Total", "total": grand_total})

        return review_csv_filepath

    def _group_by(self, group_identifier):
        rows = sorted(
            self.parsed_details[self._data_key()],
            key=lambda row: row[group_identifier], reverse=False
        )
        return groupby(rows, lambda row: row[group_identifier])

    def _filter_row(self, details_row):
        filtered_row = {
            key: details_row[key] for key in self._fieldnames() if key in details_row.keys()
        }

        return self._format_datefields(filtered_row)

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
            "summary", "status", "severity", "area", "created_date", "created_by"
        )

    def _datetime_fields(self):
        return (
            "created_date",
        )
