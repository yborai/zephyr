import csv
from itertools import groupby

from cement.core import controller

from .compute_migration import ComputeMigrationWarp
from .common import ToolkitDataController

class ToolkitComputeUnderutilizedBreakdown(ToolkitDataController):
    class Meta:
        label = "underutilized-instances-breakdown"
        stacked_on = "data"
        stacked_type = "nested"
        description = "Get the underutilized instance breakdown meta information"

        arguments = ToolkitDataController.Meta.arguments #+ [(
        #    ["--cc_api_key"], dict(
        #        type=str,
        #        help="The CloudCheckr API key to use."
        #    )
        #)]

    @controller.expose(hide=True)
    def default(self):
        self.run(**vars(self.app.pargs))

    def run(self, **kwargs):
        cache = self.app.pargs.cache
        if(not cache):
            raise NotImplementedError # We'll add fetching later
        self.app.log.info("Using cached response: {cache}".format(cache=cache))
        with open(cache, "r") as f:
            response = f.read()
        warp = ComputeUnderutilizedBreakdownWarp(response)
        self.app.render(warp.to_ddh())


def create_sheet(json_string, define_category_func, csv_filename='compute-underutilized-breakdown.csv'):
    """
    This function creates new class instance
    with provided define_category function
    and immediately writes the parsed json review
    to specified csv file.

    define_category_func should take one string argument
    and returns string which contains category name.
    """
    processor = ComputeUnderutilizedBreakdownWarp(json_string, define_category_func)
    return processor.write_csv(csv_filename)


class ComputeUnderutilizedBreakdownWarp(ComputeMigrationWarp):
    def __init__(self, json_string, define_category_func):
        self.define_category_func = define_category_func
        super().__init__(json_string)

    def write_csv(self, csv_filename):
        filtered_rows = (
            self._filter_row(details_row)
            for details_row in self.parsed_details[self._data_key()]
        )

        grouped_rows = self._group_rows(filtered_rows)
        self._write_to_file(csv_filename, grouped_rows)

        return csv_filename

    def _write_to_file(self, csv_filename, grouped_rows):
        with open(csv_filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self._fieldnames())

            writer.writeheader()
            for category, group in grouped_rows:
                category_sum = 0
                for row in group:
                    category_sum += row["Predicted Monthly Cost"]
                    writer.writerow(row)
                writer.writerow({
                    "Category": row["Category"],
                    "Predicted Monthly Cost": category_sum,
                })
                writer.writerow(self._empty_row())
        return csv_filename

    def _filter_row(self, details_row):
        details_row["Instance ID"] = self._get_instance_id(details_row[self._instance_field()])
        details_row["Instance Name"] = self._get_instance_name(details_row[self._instance_field()])
        details_row["Category"] = self._define_category(details_row["Instance Name"].split("-")[0])

        return super()._filter_row(details_row)

    def _group_rows(self, filtered_rows):
        rows = sorted(filtered_rows, key=lambda row: row['Category'], reverse=True)
        return groupby(rows, lambda row: row['Category'])

    def _define_category(self, raw_category):
        """
        This method tries to call define_category function
        for current class instance and returns the result of computing
        or raises an exception if define_category_func isn't callable.
        """
        if callable(self.define_category_func):
            return self.define_category_func(raw_category)

        raise IllegalArgumentError("define_category_func parameter should be callable")

    def _fieldnames(self):
        return (
            "Category", "Instance ID", "Instance Name", "Average CPU Util",
            "Predicted Monthly Cost", "Region"
        )

    def _money_fields(self):
        return (
            "Predicted Monthly Cost",
        )

    def _empty_row(self):
        return {}


class IllegalArgumentError(ValueError):
    pass
