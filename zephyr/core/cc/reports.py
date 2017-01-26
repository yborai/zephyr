import pandas as pd
import sqlite3

from operator import itemgetter
from datetime import datetime

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

    def _xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the EC2 report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing
        chart_ceil = self.chart_height + 1

        # Insert instances by region.
        self.count_by_pie_chart(
            book, sheet, "Region", chart_start_row, 0, "ec2_region"
        )

        # Insert instances by platform
        platform_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            book, sheet, "PricingPlatform", platform_top, 0, "pric_plat"
        )

        # Insert instances by status
        status_top = platform_top + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            book, sheet, "Status", status_top, 0, "status"
        )

        # Insert RI Qualifications
        ri_qual_top = status_top + chart_ceil + self.cell_spacing
        self.days_since_launch_pie_chart(
            book, sheet, ri_qual_top, 0, "ri_qual"
        )

        # Insert instances by type
        instance_top = ri_qual_top + chart_ceil + self.cell_spacing
        self.count_by_column_chart(
            book, sheet, "InstanceType", instance_top, 0, "instance_type"
        )
        return sheet

    def count_by(self, column):
        """Count rows in data grouping by values in the column specified"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
        df.to_sql("df", con, if_exists="replace")
        where = ""
        if column != "Status":
            where = """WHERE "Status" = 'running' """
        query = """
            SELECT
                 {col},
                 COUNT({col}) as Total
             FROM df
             {where}
             GROUP BY {col}
             ORDER BY COUNT({col}) DESC
        """.format(col=column, where=where)
        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        return header, data

    def count_by_column_chart(
        self, book, sheet, column_name, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        # Get first 4 data rows
        header, data_ = self.count_by(column_name)
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
            ddh=counts,
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

    def days_since_launch_pie_chart(self, book, sheet, top, left, name):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        launch_times, days_90, days_180, days_270 = self.get_launch_times()

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
            ddh=counts,
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

    def get_launch_times(self):
        launch_times = []
        status_index = self.ddh.header.index("Status")
        lt_index = self.ddh.header.index("LaunchTime")
        for row in self.ddh.data:
            if row[status_index] != "running": # Only include running instances
                continue
            launch_times.append(row[lt_index])

        now = datetime.strptime(self.date, "%Y-%m-%d").date()
        days_90 = 0
        days_180 = 0
        days_270 = 0
        for date in launch_times:
            day = datetime.strptime(date, "%m/%d/%y %H:%M").date()
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

    def _xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, top=1, name=self.name)

        return sheet

class ReportRDS(Report):
    name = "RDS"
    title = "RDS Details"
    cls = DBDetailsWarp

    def _xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_and_count_by_column_chart(
            book, sheet,
            "DbInstanceClass",
            "MonthlyCost",
            chart_start_row,
            0,
            "month_cost"
        )
        return sheet

    def sum_and_count_by(self, column_name, cost_column):
        """Count and sum rows in data grouping by values in the column specified"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
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
        self, book, sheet, column_name, cost_column, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        header, data = self.sum_and_count_by(column_name, cost_column)

        counts = DDH(header=header, data=data)

        self.put_label(book, sheet, column_name, top, self.table_left)

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            ddh=counts,
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

    def _xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.put_label(book, sheet, self.title)

        self.put_table(book, sheet, top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_by_column_chart(
            book, sheet, "Annual Savings", chart_start_row, 0, "ri_savings"
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

    def sum_by(self):
        """Sum rows in data grouping by values in the column specified"""
        # Create data with correct float values

        new_data = self.clean_data()

        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(new_data, columns=self.ddh.header)
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
        self, book, sheet, column_name, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1 # Account for label.

        # Get first 4 data rows
        header, data_ = self.sum_by()
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
            ddh=sums,
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

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        con = sqlite3.connect(":memory:")

        self.account = account
        self.con = con
        self.config = config
        self.date = date
        self.ddh = None
        self.expire_cache = expire_cache
        self.log = log

    def predicted_cost_by_environment(self, top=0, left=0):
        book = self.book
        con = self.con
        sheet = self.sheet

        df = pd.read_sql("""
            SELECT
                CASE cd."Environment"
                    WHEN '' THEN 'No environment'
                    ELSE cd."Environment"
                END AS "Environment",
                SUM(uu."Predicted Monthly Cost") AS "Cost"
            FROM
                cd LEFT OUTER JOIN
                uu ON (cd."InstanceId"=uu."Instance ID")
            WHERE uu."Average CPU Util" IS NOT NULL
            GROUP BY cd."Environment"
            ORDER BY SUM(uu."Predicted Monthly Cost") DESC
        """, con)

        # Account for hidden column
        table_left = left + self.chart_width + self.cell_spacing + 1
        table_top = top + self.cell_spacing

        data = [list(row) for row in df.values]
        ddh = DDH(data=data, header=list(df.columns))

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            ddh=ddh,
            top=table_top,
            left=table_left,
            name="PredPrice_by_Env",
        )

        # Compute series location.
        table_loc = (
            table_top + 1, # Start of data series, accounting for header
            table_top + len(data),
            table_left,
            table_left + 1,
        )
        title = "Predicted Monthly Cost by Environment"
        self.put_chart(book, sheet, title, top+1, left, table_loc, "column")

    def to_ddh(self):
        account = self.account
        con = self.con
        config = self.config
        date = self.date
        expire_cache = self.expire_cache
        log = self.log

        # cd for compute-details
        cd_report = ReportEC2(config, account, date, expire_cache, log)
        cd_report.to_sql("cd", con)

        # uu for underutilized
        uu_client = ComputeUnderutilizedWarp(config=config)
        uu_report = uu_client.cache_policy(account, date, expire_cache, log=log)
        uu_client.parse(uu_report)
        uu_ddh = uu_client.to_ddh()
        uu_data = [[str(cell) for cell in row] for row in uu_ddh.data]
        uu_df = pd.DataFrame(uu_data, columns=uu_ddh.header)
        uu_df.to_sql("uu", con)

        # cu for compute-details and underutilized joined 
        cu_df = pd.read_sql("""
            SELECT
                cd."InstanceId",
                cd."InstanceName",
                cd."Environment",
                uu."Average CPU Util",
                uu."Predicted Monthly Cost"
            FROM
                cd LEFT OUTER JOIN
                uu ON (cd."InstanceId"=uu."Instance ID")
            WHERE uu."Average CPU Util" IS NOT NULL
            ORDER BY cd."Environment" DESC
        """, con)
        cu_data = [list(row) for row in cu_df.values]
        cu_ddh = DDH(data=cu_data, header=list(cu_df.columns))
        self.ddh = cu_ddh
        return self.ddh

    def to_xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the SR report."""
        self.book = book

        # Insert raw report data.
        sheet = book.add_worksheet(self.title)
        self.sheet = sheet
        self.get_formatting()
        self.put_label(book, sheet, self.title)

        # Retrieve the data if it does not exist yet.
        if(not self.ddh):
            self.to_ddh()

        # Hide the environment column by default
        env_idx = self.ddh.header.index("Environment")
        sheet.set_column(env_idx+1, env_idx+1, None, None, dict(hidden=1))

        # Format the report to visually separate the environments.
        environment = None
        header = [" "] + self.ddh.header
        out = []
        for row in self.ddh.data:
            if environment != row[env_idx]:
                environment = row[env_idx]
                out.append(
                    [environment]
                    + [""]*env_idx
                    + [environment]
                    + [""]*(len(header) - (env_idx + 2))
                )
            out.append([""] + row)

        ddh = DDH(header=header, data=out)

        self.put_table(book, sheet, ddh=ddh, top=1)

        top = len(out) + 2 # Account for label and table columns
        self.predicted_cost_by_environment(top=top, left=0)

        return sheet

