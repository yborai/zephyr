import datetime
import pandas as pd
import sqlite3
from operator import itemgetter

from ..ddh import DDH
from ..report import Report
from .calls import (
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    DBDetailsWarp,
)

class ReportEC2(Report):
    name = "EC2s"
    title = "EC2 Details"
    cls = ComputeDetailsWarp

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the EC2 report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing
        chart_ceil = self.chart_height + 1

        # Insert instances by region.
        self.count_by_pie_chart(
            book, sheet, "Region", ddh, chart_start_row, 0, "ec2_region"
        )

        # Insert instances by platform
        platform_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            book, sheet, "PricingPlatform", ddh, platform_top, 0, "pric_plat"
        )

        # Insert instances by status
        status_top = platform_top + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            book, sheet, "Status", ddh, status_top, 0, "status"
        )

        # Insert RI Qualifications
        ri_qual_top = status_top + chart_ceil + self.cell_spacing
        self.days_since_launch_pie_chart(
            book, sheet, ddh, ri_qual_top, 0, "ri_qual"
        )

        # Insert instances by type
        instance_top = ri_qual_top + chart_ceil + self.cell_spacing
        self.count_by_column_chart(
            book, sheet, "InstanceType", ddh, instance_top, 0, "instance_type"
        )
        return sheet

    def count_by_column_chart(
        self, book, sheet, column_name, ddh, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        # Get first 4 data rows
        header, data_ = self.count_by(ddh.header, ddh.data, column_name)
        data = data_[:4]

        # Rollup remaining values into "other" column
        other_values = [item[1] for item in data_[4:]]
        other_row = ["Other", sum(other_values)]

        # Append data
        data.append(other_row)
        data = sorted(data, key=itemgetter(1), reverse=True)
        counts = DDH(header=header, data=data)

        self.put_label(book, sheet, column_name, top, self.table_left)

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            counts,
            top=table_top,
            left=self.table_left,
            name=name
        )
        # Compute series information.
        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 1,
        )

        # Create chart formatting
        dlf = dict()
        dlf.update(self.formatting["data_labels"])
        dlf["category"] = False
        dlf["value"] = True
        ccf = dict(
            legend_options=self.formatting["legend_options"],
            data_labels=dlf
        )
        self.put_chart(
            book, sheet, column_name, top, left, table_loc, "column", ccf
        )
        return book

    def days_since_launch_pie_chart(self, book, sheet, ddh, top, left, name):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        launch_times, days_90, days_180, days_270 = self.get_launch_times(ddh)

        header = ["Days Since Launch", "Total"]
        data = [
            ["< 90 Days", len(launch_times) - sum([days_90, days_180, days_270])],
            ["> 90 Days", days_90],
            ["> 180 Days", days_180],
            ["> 270 Days", days_270],
        ]
        counts = DDH(header=header, data=data)
        title = "RI Qualified"

        self.put_label(book, sheet, title, top, self.table_left)

        sheet = self.put_table(
            book,
            sheet,
            counts,
            top=table_top,
            left=self.table_left,
            name=name
        )

        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 1,
        )

        self.put_chart(book, sheet, title, top, left, table_loc, "pie")
        return book

    def get_launch_times(self, ddh):
        launch_times = []
        for row in ddh.data:
            if row[3] != "running": # Status is the 4th column: only include running instances
                continue
            launch_times.append(row[-1])

        now = datetime.datetime.now().date()
        days_90 = 0
        days_180 = 0
        days_270 = 0
        for date in launch_times:
            day = datetime.datetime.strptime(date, "%m/%d/%y %H:%M").date()
            delta = now - day
            if delta.days > 90 and delta.days < 181:
                days_90 += 1
            if delta.days > 180 and delta.days < 271:
                days_180 += 1
            if delta.days > 270:
                days_270 += 1

        return launch_times, days_90, days_180, days_270

class ReportMigration(Report):
    name = "Migration"
    title = "EC2 Migration Recommendations"
    cls = ComputeMigrationWarp

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        return sheet

class ReportRDS(Report):
    name = "RDS"
    title = "RDS Details"
    cls = DBDetailsWarp

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_and_count_by_column_chart(
            book, sheet,
            "DbInstanceClass",
            "MonthlyCost",
            ddh,
            chart_start_row,
            0,
            "month_cost"
        )
        return sheet

    def sum_and_count_by(self, header, data, column_name, cost_column):
        """Count and sum rows in data grouping by values in the column specified"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(data, columns=header)
        df.to_sql("df", con, if_exists="replace")
        query = """
            SELECT
                 {col},
                 COUNT({col}) AS "Count",
                 SUM({cost}) AS "Sum"
             FROM df
             GROUP BY {col}
             ORDER BY Sum DESC
        """.format(col=column_name, cost=cost_column)

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        return header, data

    def sum_and_count_by_column_chart(
        self, book, sheet, column_name, cost_column, ddh, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        header, data = self.sum_and_count_by(
            ddh.header, ddh.data, column_name, cost_column
        )

        counts = DDH(header=header, data=data)

        self.put_label(book, sheet, column_name, top, self.table_left)

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            counts,
            top=table_top,
            left=self.table_left,
            name=name
        )
        # Compute series information.
        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 2, # Sum is the third column and is the data we are graphing.
        )
        # Create chart formatting
        dlf = dict()
        dlf.update(self.formatting["data_labels"])
        dlf["category"] = False
        dlf["value"] = True
        ccf = dict(
            legend_options=self.formatting["legend_options"],
            data_labels=dlf
        )
        self.put_chart(
            book, sheet, column_name, top, left, table_loc, "column", ccf
        )
        return book

class ReportRIs(Report):
    name = "RIs"
    title = "EC2 RI Recommendations"
    cls = ComputeRIWarp

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_by_column_chart(
            book, sheet, "Annual Savings", ddh, chart_start_row, 0, "ri_savings"
        )
        return sheet

    def put_two_series_chart(
        self, book, sheet, title, top, left, data_loc, chart_type, formatting
    ):
        """Add RI chart to an xlsx workbook located at data_loc."""
        chart = book.add_chart(dict(type=chart_type))
        legend_options = formatting["legend_options"]
        top_, bottom, col_keys, col_values = data_loc

        # Add first column
        series_categories = [sheet.name, top_, col_keys, bottom, col_keys]
        series1_values = [sheet.name, top_, col_values-1, bottom, col_values-1] # Looks at first column
        series1 = dict(
            categories=series_categories,
            values=series1_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series1)

        # Add the second column
        series2_values = [sheet.name, top_, col_values, bottom, col_values]
        series2 = dict(
            categories=series_categories,
            values=series2_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series2)

        chart.set_title({"name": title})
        chart.set_legend(legend_options)
        sheet.insert_chart(top, left, chart)
        return sheet

    def sum_by(self, header, data):
        """Sum rows in data grouping by values in the column specified"""
        # Create data with correct float values

        new_data = self.clean_data(data)

        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(new_data, columns=header)
        df.to_sql("df", con, if_exists="replace")
        query = """
            SELECT
                "Instance Type",
                SUM("On-Demand Monthly Cost"*12) AS "On-Demand Instance Cost",
                SUM("Reserved Monthly Cost"*12+"Upfront RI Cost") AS "RI Cost"
            FROM df
            GROUP BY "Instance Type"
            ORDER BY "On-Demand Instance Cost" DESC
        """

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data_ = [list(row) for row in sql_group.values]

        return header, data_

    def sum_by_column_chart(
        self, book, sheet, column_name, ddh, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        # Get first 4 data rows
        header, data_ = self.sum_by(ddh.header, ddh.data)
        data = data_[:4]

        # Rollup remaining values into "other" column
        od_cost_values = [item[1] for item in data_[:4]]
        ri_cost_values = [item[2] for item in data_[:4]]
        other_row = ["Other", sum(od_cost_values), sum(ri_cost_values)]

        # Append data
        data.append(other_row)
        data = sorted(data, key=itemgetter(1), reverse=True)
        sums = DDH(header=header, data=data)

        self.put_label(book, sheet, column_name, top, self.table_left)

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            sums,
            top=table_top,
            left=self.table_left,
            name=name
        )
        # Compute series information.
        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 2, # Sum is the third column and is the data we are graphing.
        )
        # Create chart formatting
        dlf = dict()
        dlf.update(self.formatting["data_labels"])
        dlf["category"] = False
        ccf = dict(
            legend_options=self.formatting["legend_options"],
            data_labels=dlf
        )
        self.put_two_series_chart(book, sheet, column_name, top, left, table_loc, "column", ccf)
        return book

class ReportUnderutilized(Report):
    name = "Underutil"
    title = "EC2 Underutilized Instances"
    cls = ComputeUnderutilizedWarp

    def _xlsx(self, book, ddh, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, ddh, top=1, name=self.name)

        breakdown_title = "EC2 Underutilized Instance Breakdown"
        breakdown_name = "Breakdown"
        breakdown_left = len(ddh.data[0]) + self.cell_spacing

        self.put_label(book, sheet, breakdown_name, left=breakdown_left)

        header, data_ = self.get_category(ddh.header, ddh.data)
        data = self.remove_repeated_names(data_)

        ddh = DDH(header=header, data=data)

        self.put_table(book, sheet, ddh, 1, breakdown_left, breakdown_name)

        return sheet


    def get_category(self, header, data):
        """Returns the underutilized breakdown dataset including the category column."""
        con = sqlite3.connect(":memory:")
        data_ = self.clean_data(data)
        df = pd.DataFrame(data_, columns=header)
        df.to_sql("df", con, if_exists="replace", index=False)
        query = """
            SELECT
                substr("Instance Name", 0, instr("Instance Name", '-')) AS Category,
                *
            FROM df
            ORDER BY substr("Instance Name", 0, instr("Instance Name", '-'))
        """

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        return header, data

    def remove_repeated_names(self, data):
        seen = set()
        with_tags = list()
        no_tags = list()
        for row in data:
            if "-" not in row[2]:
                no_tags.append(row)
                continue
            if row[0] not in seen:
                seen.add(row[0])
                with_tags.append(row)
                continue
            row[0] = ""
            with_tags.append(row)
        if(len(no_tags)):
            no_tags[0][0] = "No tag"

        out = with_tags + no_tags

        return out
