import datetime
import pandas as pd
import sqlite3
import xlsxwriter

from decimal import Decimal
from ..core.client import Client
from ..core.utils import ZephyrException
from .ddh import DDH

class Report(Client):
    name = None
    title = None
    formatting = {
            "cell_options" : {
                "height" : 20,
                "width" : 64,
            },
            "chart_options" : {
                "height" : 288,
                "width" : 480,
            },
            "data_labels": {
                "category": True,
                "percentage": True,
                "position": "outside_end",
            },
            "header_format" : {
                "font_color" : "#000000",
                "bg_color" : "#DCE6F1",
                "bottom" : 2,
            },
            "label_format" : {
                "bold": True,
                "font_size": 16,
                "font_color": "#000000",
            },
            "legend_options" : {
                "none" : True,
            },
            "pie_chart" : {
                "type" : "pie",
            },
            "table_style" : {
                "style" : "Table Style Light 1",
            },
            "titles" : {
                "Service Requests" : "srs",
                "EC2 Details" : "ec2",
            },
            "total_row" : [
                {"total_string" : "Total"},
                {"total_function" : "sum"},
            ],
            "book_options" : {
                "strings_to_numbers": True,
            },
        }

    @classmethod
    def book_formats(cls, book):
        """Get format objects from book."""
        table = cls.formatting["table_style"]
        header_format = book.add_format(cls.formatting["header_format"])
        cell_format = book.add_format(cls.formatting["label_format"])
        return table, header_format, cell_format

    @classmethod
    def put_label(cls, book, sheet, title, top=0, left=0):
        """Inserts a properly formatted label into a workbook."""
        # Configure formatting
        cell_format = cls.book_formats(book)[2]

        # Create label with cell_format
        sheet.write(top, left, title, cell_format)
        return sheet

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        client = self.cls(config=config)
        response = client.cache_policy(
            account,
            date,
            expire_cache,
            log=log,
        )
        client.parse(response)
        self.client = client
        self.cell = self.formatting["cell_options"]
        self.chart = self.formatting["chart_options"]
        self.chart_width = int(self.chart["width"]/self.cell["width"])
        self.chart_height = int(self.chart["height"]/self.cell["height"])
        self.cell_spacing = 1
        self.date = date
        self.table_left = int(self.chart_width) + self.cell_spacing

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

    def count_by(self, column):
        """Count rows in data grouping by values in the column specified"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
        df.to_sql("df", con, if_exists="replace")
        if column != "Status" and ("running" or "stopped") in self.ddh.data[0]:
            query = """
                SELECT
                     {col},
                     COUNT({col}) as Total
                 FROM df
                 WHERE Status = "running"
                 GROUP BY {col}
                 ORDER BY COUNT({col}) DESC
            """.format(col=column)
        else:
            query = """
                SELECT
                     {col},
                     COUNT({col}) as Total
                 FROM df
                 GROUP BY {col}
                 ORDER BY COUNT({col}) DESC
            """.format(col=column)

        sql_group = pd.read_sql(query, con)
        header = list(sql_group)
        data = [list(row) for row in sql_group.values]

        return header, data

    def count_by_pie_chart(
        self, book, sheet, column_name, top, left, name
    ):
        """Insert a pie chart with data specified."""
        table_left = int(self.chart_width) + self.cell_spacing
        table_top = top + 1 # Account for label.

        # Aggregate the data, grouping by the given column_name.
        header, data = self.count_by(column_name)
        counts = DDH(header=header, data=data)

        self.put_label(book, sheet, column_name, top, table_left)

        # Write the data table to the sheet.
        sheet = self.put_table(
            book,
            sheet,
            ddh=counts,
            top=table_top,
            left=table_left,
            name=name
        )

        # Compute series location.
        table_loc = (
            table_top + 1, # Start of data series, accounting for header
            table_top + len(data),
            table_left,
            table_left + 1,
        )
        self.put_chart(book, sheet, column_name, top, left, table_loc, "pie")
        return book

    def header_format_xlsx(self, headers, header_format, total_row):
        """Create the header format dict for Xlsxwriter."""
        header = [{"header": col, "header_format": header_format} for col in headers]
        [header[i].update(total_row[i]) for i in range(len(total_row))]
        return header

    def put_chart(
            self,
            book,
            sheet,
            title,
            top,
            left,
            data_loc,
            chart_type,
            formatting=None
        ):
        """Add a chart to an xlsx workbook located at data_loc."""
        if not formatting:
            formatting = self.formatting
        chart = book.add_chart(dict(type=chart_type))
        legend_options = formatting["legend_options"]
        top_, bottom, col_keys, col_values = data_loc

        series_categories = [sheet.name, top_, col_keys, bottom, col_keys]
        series_values = [sheet.name, top_, col_values, bottom, col_values]
        series = dict(
            categories=series_categories,
            values=series_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series)

        chart.set_title({"name": title})
        chart.set_legend(legend_options)
        sheet.insert_chart(top, left, chart)
        return sheet

    def put_table(
        self, book, sheet, ddh=None, top=0, left=0, name=None
    ):
        if not ddh:
            ddh = self.ddh
        """Creates an Excel table in a workbook."""
        # Configure formatting
        table_fmt, header_format, cell_format = self.book_formats(book)

        # Write data to sheet
        sheet = self.rows_to_excel(sheet, ddh.data, top=top+1, left=left)

        # Create format dict for xlsxwriter
        total_row = []
        header = self.header_format_xlsx(ddh.header, header_format, total_row)
        table_format = dict(
            columns=header,
            name=name,
            style=table_fmt["style"],
            total_row=bool(total_row),
        )

        # Compute dimensions of Excel table
        n_rows = len(ddh.data)
        n_cols = len(ddh.data[0])

        # Tell Excel this array is a table. Note: Xlsxwriter is 0 indexed.
        sheet.add_table(top, left, top + n_rows, left + n_cols - 1, table_format)
        return sheet

    def rows_to_excel(self, sheet, rows, top=1, left=0):
        """
        Take rows, an iterable of iterables, and write it to a given sheet
        with the top, left cell at (top, left).
        """
        n_rows = len(rows)
        n_cells = len(rows[0])
        for i in range(n_rows):
            row = rows[i]
            for j in range(n_cells):
                sheet.write(top+i, left+j, row[j])
        return sheet

    def to_xlsx(self, book):
        self.ddh = self.client.to_ddh()
        if not self.ddh.data:
            return False
        return self._xlsx(
            book,
            name=self.name
        )

class ReportCoverPage(Client):
    name = "coverpage"
    title = "Cover Page"

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config)
        self.account = account
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.date = date_obj.strftime("%B %d, %Y")

    def get_account_by_slug(self, slug):
        matches = pd.read_sql("""
            SELECT a.name AS client
            FROM
                accounts AS a LEFT OUTER JOIN
                projects AS p ON (a.Id=p.Account__c) LEFT OUTER JOIN
                aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws.name = '{slug}'
            """.format(slug=slug),
            self.database
        )
        if not len(matches):
            raise ZephyrException("There are no projects associated with this slug.")
        return matches["client"][0]

    def to_xlsx(self, book):
        sheet = book.add_worksheet(self.title)
        acct = self.get_account_by_slug(self.account)
        Report.put_label(book, sheet, "Account Review")
        Report.put_label(book, sheet, acct, top=1)
        Report.put_label(book, sheet, self.date, top=2)

        return sheet
