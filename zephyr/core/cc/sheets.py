import pandas as pd
import sqlite3

from decimal import Decimal
from operator import itemgetter
from datetime import datetime

from ..ddh import DDH
from ..sheet import Sheet
from .calls import (
    ComputeDetailsWarp,
    ComputeMigrationWarp,
    ComputeRIWarp,
    ComputeUnderutilizedWarp,
    DBDetailsWarp,
)


class SheetEC2(Sheet):
    name = "EC2s"
    title = "EC2 Details"
    calls = (ComputeDetailsWarp,)

    def to_xlsx(self, book, **kwargs):
        """Format the sheet and insert the data for the EC2 sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        self.put_table(top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing
        chart_ceil = self.chart_height + 1

        # Insert instances by region.
        self.count_by_pie_chart("Region", chart_start_row, 0, "ec2_region")

        # Insert instances by platform
        platform_top = chart_start_row + chart_ceil + self.cell_spacing
        self.count_by_pie_chart(
            "PricingPlatform", platform_top, 0, "pric_plat"
        )

        # Insert instances by status
        status_top = platform_top + chart_ceil + self.cell_spacing
        self.count_by_pie_chart("Status", status_top, 0, "status")

        # Insert RI Qualifications
        ri_qual_top = status_top + chart_ceil + self.cell_spacing
        self.days_since_launch_pie_chart(ri_qual_top, 0, "ri_qual")

        # Insert instances by type
        instance_top = ri_qual_top + chart_ceil + self.cell_spacing
        self.count_by_column_chart(
            "InstanceType", instance_top, 0, "instance_type"
        )
        return self.sheet

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
        self, column_name, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1  # Account for label.

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

        self.put_label(column_name, top, self.table_left)

        # Write the data table to the sheet.
        self.sheet = self.put_table(
            ddh=counts, top=table_top, left=self.table_left, name=name
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
        self.put_chart(column_name, top, left, table_loc, "column", ccf)
        return self.book

    def days_since_launch_pie_chart(self, top, left, name):
        """Insert a column chart with data specified."""
        table_top = top + 1  # Account for label.

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

        self.put_label(title, top, self.table_left)

        self.sheet = self.put_table(
            ddh=counts, top=table_top, left=self.table_left, name=name
        )

        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 1,
        )

        self.put_chart(title, top, left, table_loc, "pie")
        return self.book

    def get_launch_times(self):
        launch_times = []
        status_index = self.ddh.header.index("Status")
        lt_index = self.ddh.header.index("LaunchTime")
        for row in self.ddh.data:
            if row[status_index] != "running":  # Only include running instances
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


class SheetMigration(Sheet):
    name = "Migration"
    title = "EC2 Migration Recommendations"
    calls = (ComputeMigrationWarp,)

    def to_xlsx(self, book, **kwargs):
        """Format the Migration sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        self.put_table(top=1, name=self.name)

        return self.sheet


class SheetRDS(Sheet):
    name = "RDS"
    title = "RDS Details"
    calls = (DBDetailsWarp,)

    def to_xlsx(self, book, **kwargs):
        """Format the RDS sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        self.put_table(top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_and_count_by_column_chart(
            "DbInstanceClass",
            "MonthlyCost",
            chart_start_row,
            0,
            "month_cost"
        )
        return self.sheet

    def sum_and_count_by(self, column_name, cost_column):
        """Count and sum rows in data grouping by values in the given column."""
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
        self, column_name, cost_column, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1  # Account for label.

        header, data = self.sum_and_count_by(column_name, cost_column)

        counts = DDH(header=header, data=data)

        self.put_label(column_name, top, self.table_left)

        # Write the data table to the sheet.
        self.sheet = self.put_table(
            ddh=counts, top=table_top, left=self.table_left, name=name
        )
        # Compute series information.
        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 2,  # The sum to be graphed is the third column.
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
        self.put_chart(column_name, top, left, table_loc, "column", ccf)
        return self.book


class SheetRIs(Sheet):
    name = "RIs"
    title = "EC2 RI Recommendations"
    calls = (ComputeRIWarp,)

    def clean_data(self):
        new_data = []
        for row in self.ddh.data:
            new_row = []
            for cell in row:
                if isinstance(cell, Decimal):
                    new_row.append(float(cell))
                    continue
                new_row.append(cell)
            new_data.append(new_row)
        return new_data

    def put_two_series_chart(
        self, title, top, left, data_loc, chart_type, formatting
    ):
        """Add RI chart to an xlsx workbook located at data_loc."""
        chart = self.book.add_chart(dict(type=chart_type))
        legend_options = formatting["legend_options"]
        top_, bottom, col_keys, col_values = data_loc

        # Add first column
        series_categories = [self.sheet.name, top_, col_keys, bottom, col_keys]
        # Look at first column
        series1_values = [
            self.sheet.name, top_, col_values-1, bottom, col_values-1
        ]
        series1 = dict(
            categories=series_categories,
            values=series1_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series1)

        # Add the second column
        series2_values = [self.sheet.name, top_, col_values, bottom, col_values]
        series2 = dict(
            categories=series_categories,
            values=series2_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series2)

        chart.set_title({"name": title})
        chart.set_legend(legend_options)
        self.sheet.insert_chart(top, left, chart)
        return self.sheet

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
        self, column_name, top, left, name
    ):
        """Insert a column chart with data specified."""
        table_top = top + 1  # Account for label.

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

        self.put_label(column_name, top, self.table_left)

        # Write the data table to the sheet.
        self.sheet = self.put_table(
            ddh=sums, top=table_top, left=self.table_left, name=name
        )
        # Compute series information.
        table_loc = (
            table_top + 1,
            table_top + len(data),
            self.table_left,
            self.table_left + 2,  # The sum to be graphed is the third column.
        )
        # Create chart formatting
        dlf = dict()
        dlf.update(self.formatting["data_labels"])
        dlf["category"] = False
        ccf = dict(
            legend_options=self.formatting["legend_options"],
            data_labels=dlf
        )
        self.put_two_series_chart(
            column_name, top, left, table_loc, "column", ccf
        )
        return self.book

    def to_xlsx(self, book, **kwargs):
        """Format the Reserved Instance sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = self.book.add_worksheet(self.title)
        self.put_label(self.title)

        self.put_table(top=1, name=self.name)

        # Where charts and other tables go
        n_rows = len(self.ddh.data)
        table_height = n_rows + 1
        chart_start_row = 1 + table_height + self.cell_spacing

        self.sum_by_column_chart(
            "Annual Savings", chart_start_row, 0, "ri_savings"
        )
        return self.sheet


class SheetUnderutilized(Sheet):
    name = "Underutil"
    title = "EC2 Underutilized Instances"
    calls = (ComputeDetailsWarp, ComputeUnderutilizedWarp)

    def predicted_cost_by_environment(self, top=0, left=0):
        con = self.con
        CD, UU = self.calls
        df = pd.read_sql("""
            SELECT
                CASE cd."Environment"
                    WHEN '' THEN 'No environment'
                    ELSE cd."Environment"
                END AS "Environment",
                SUM(uu."Predicted Monthly Cost") AS "Cost"
            FROM
                "{cd}" AS cd LEFT OUTER JOIN
                "{uu}" AS uu ON (cd."InstanceId"=uu."Instance ID")
            WHERE uu."Average CPU Util" IS NOT NULL
            GROUP BY cd."Environment"
            ORDER BY SUM(uu."Predicted Monthly Cost") DESC
        """.format(cd=CD.slug, uu=UU.slug), con)

        # Account for hidden column
        table_left = left + self.chart_width + self.cell_spacing + 1
        table_top = top + self.cell_spacing

        data = [list(row) for row in df.values]
        ddh = DDH(data=data, header=list(df.columns))

        # Write the data table to the sheet.
        self.sheet = self.put_table(
            ddh=ddh, top=table_top, left=table_left, name="PredPrice_by_Env"
        )

        # Compute series location.
        table_loc = (
            table_top + 1,  # Start of data series, accounting for header
            table_top + len(data),
            table_left,
            table_left + 1,
        )
        title = "Predicted Monthly Cost by Environment"
        # Create chart formatting.
        dlf = dict()
        dlf.update(self.formatting["data_labels"])
        dlf["category"] = False
        ccf = dict(
            legend_options=self.formatting["legend_options"],
            data_labels=dlf
        )
        self.put_chart(title, top+1, left, table_loc, "column", ccf)

    def to_ddh(self):
        if(self._ddh):
            return self._ddh

        # CD for compute-details, UU for underutilized
        CD, UU = self.calls
        con = self.con

        # cu for compute-details and underutilized joined
        cu_df = pd.read_sql("""
            SELECT
                cd."InstanceId",
                cd."InstanceName",
                cd."Environment",
                uu."Average CPU Util",
                uu."Predicted Monthly Cost"
            FROM
                "{cd}" AS cd LEFT OUTER JOIN
                "{uu}" AS uu ON (cd."InstanceId"=uu."Instance ID")
            WHERE uu."Average CPU Util" IS NOT NULL
            ORDER BY cd."Environment" DESC
        """.format(cd=CD.slug, uu=UU.slug), con)
        cu_data = [list(row) for row in cu_df.values]
        cu_ddh = DDH(data=cu_data, header=list(cu_df.columns))
        self._ddh = cu_ddh
        return self._ddh

    def to_xlsx(self, book, **kwargs):
        """Format the Underutilized sheet."""
        # Load the data.
        if not self.ddh:
            return

        self.book = book

        # Insert raw data.
        self.sheet = book.add_worksheet(self.title)
        self.get_formatting()
        self.put_label(self.title)

        # Hide the environment column by default
        env_idx = self.ddh.header.index("Environment")
        self.sheet.set_column(env_idx+1, env_idx+1, None, None, dict(hidden=1))

        # Visually separate the environments.
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

        self.put_table(ddh=ddh, top=1)

        top = len(out) + 2  # Account for label and table columns
        self.predicted_cost_by_environment(top=top, left=0)

        return self.sheet
