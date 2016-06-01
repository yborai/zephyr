from datetime import datetime
import json

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
            "summary", "status", "severity", "created_date", "created_by"
        )

    def _datetime_fields(self):
        return (
            "created_date",
        )
