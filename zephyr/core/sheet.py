import datetime
import pandas as pd
import sqlite3

from ..core.client import Client
from .ddh import DDH

FORMATTING = {
    "cell_options": {
        "height": 20,
        "width": 64,
    },
    "chart_options": {
        "height": 288,
        "width": 480,
    },
    "data_labels": {
        "category": True,
        "percentage": True,
        "position": "outside_end",
    },
    "header_format": {
        "font_color": "#000000",
        "bg_color": "#DCE6F1",
        "bottom": 2,
    },
    "label_format": {
        "bold": True,
        "font_size": 16,
        "font_color": "#000000",
    },
    "legend_options": {
        "none": True,
    },
    "table_style": {
        "style": "Table Style Light 1",
    },
    "book_options": {
        "strings_to_numbers": True,
    },
}


class Sheet(Client):
    formatting = FORMATTING
    name = None
    title = None

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config, log=log)
        self.account = account
        self.con = sqlite3.connect(":memory:")
        self.date = date
        self.expire_cache = expire_cache
        self.get_formatting()
        self.sheet = None
        self.table_left = int(self.chart_width) + self.cell_spacing
        self.clients = tuple(
            [Call(config=config, log=log) for Call in self.calls]
        )

    @property
    def ddh(self):
        if self._ddh:
            return self._ddh
        self.load_data()
        self._ddh = self.to_ddh()
        return self._ddh

    def book_formats(self):
        """Get format objects from book."""
        table = self.formatting["table_style"]
        header_format = self.book.add_format(self.formatting["header_format"])
        cell_format = self.book.add_format(self.formatting["label_format"])
        return table, header_format, cell_format

    def count_by(self, column):
        """Count rows in data grouping by values in the column specified"""
        con = sqlite3.connect(":memory:")
        df = pd.DataFrame(self.ddh.data, columns=self.ddh.header)
        df.to_sql("df", con, if_exists="replace")
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
        self, column_name, top, left, name
    ):
        """Insert a pie chart with data specified."""
        table_left = int(self.chart_width) + self.cell_spacing
        table_top = top + 1  # Account for label.

        # Aggregate the data, grouping by the given column_name.
        header, data = self.count_by(column_name)
        counts = DDH(header=header, data=data)

        self.put_label(column_name, top, table_left)

        # Write the data table to the sheet.
        self.sheet = self.put_table(
            ddh=counts,
            top=table_top,
            left=table_left,
            name=name
        )

        # Compute series location.
        table_loc = (
            table_top + 1,  # Start of data series, accounting for header
            table_top + len(data),
            table_left,
            table_left + 1,
        )
        self.put_chart(column_name, top, left, table_loc, "pie")
        return self.book

    def get_formatting(self):
        self.cell = self.formatting["cell_options"]
        self.chart = self.formatting["chart_options"]
        self.chart_width = int(self.chart["width"]/self.cell["width"])
        self.chart_height = int(self.chart["height"]/self.cell["height"])
        self.cell_spacing = 1

    def header_format_xlsx(self, headers, header_format, total_row):
        """Create the header format dict for Xlsxwriter."""
        header = [
            {"header": col, "header_format": header_format}
            for col in headers
        ]
        [header[i].update(total_row[i]) for i in range(len(total_row))]
        return header

    def load_data(self):
        client_data = list()
        for client in self.clients:
            response = client.cache_policy(
                self.account, self.date, self.expire_cache
            )
            client.parse(response)
            ddh = client.to_ddh()
            client_data.append(bool(ddh) and bool(ddh.data))
            data = [[str(cell) for cell in row] for row in ddh.data]
            df = pd.DataFrame(data, columns=ddh.header)
            df.to_sql(client.slug, self.con, if_exists='replace')

        return all(client_data)

    def put_chart(
            self, title, top, left, data_loc, chart_type, formatting=None
    ):
        """Add a chart to an xlsx workbook located at data_loc."""
        if not formatting:
            formatting = self.formatting
        chart = self.book.add_chart(dict(type=chart_type))
        legend_options = formatting["legend_options"]
        top_, bottom, col_keys, col_values = data_loc

        series_categories = [self.sheet.name, top_, col_keys, bottom, col_keys]
        series_values = [self.sheet.name, top_, col_values, bottom, col_values]
        series = dict(
            categories=series_categories,
            values=series_values,
            data_labels=formatting["data_labels"],
        )
        chart.add_series(series)

        chart.set_title({"name": title})
        chart.set_legend(legend_options)
        self.sheet.insert_chart(top, left, chart)
        return self.sheet

    def put_label(self, title, top=0, left=0):
        """Inserts a properly formatted label into a workbook."""
        # Configure formatting
        cell_format = self.book_formats()[2]

        # Create label with cell_format
        self.sheet.write(top, left, title, cell_format)
        return self.sheet

    def put_table(self, ddh=None, top=0, left=0, name=None):
        """Creates an Excel table in a workbook."""
        # Checks data
        if not ddh:
            ddh = self.ddh
        if not name:
            name = self.name
        if not len(ddh.data):
            return self.sheet
        # Configure formatting
        table_fmt, header_format, cell_format = self.book_formats()

        # Write data to sheet
        self.sheet = self.rows_to_excel(ddh.data, top=top+1, left=left)

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
        self.sheet.add_table(
            top, left, top + n_rows, left + n_cols - 1, table_format
        )
        return self.sheet

    def rows_to_excel(self, rows, top=1, left=0):
        """
        Take rows, an iterable of iterables, and write it to a given sheet
        with the top, left cell at (top, left).
        """
        n_rows = len(rows)
        n_cells = len(rows[0])
        for i in range(n_rows):
            row = rows[i]
            for j in range(n_cells):
                self.sheet.write(top+i, left+j, row[j])
        return self.sheet

    def to_ddh(self):
        if(self._ddh):
            return self._ddh
        if(len(self.calls) != 1):
            raise NotImplementedError
        client = self.clients[0]
        if(not client.ddh or not client.ddh.data):
            return False
        self._ddh = client.ddh
        return self._ddh


class CoverPage(Client):
    name = "coverpage"
    title = "Cover Page"
    calls = ()

    def __init__(
        self, config, account=None, date=None, expire_cache=None, log=None
    ):
        super().__init__(config, log=log)
        self.account = account
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
        self.date = date_obj.strftime("%B %d, %Y")

    def get_account_by_slug(self, slug):
        matches = pd.read_sql("""
            SELECT a.name AS client
            FROM
                sf_accounts AS a LEFT OUTER JOIN
                sf_projects AS p ON (a.Id=p.Account__c) LEFT OUTER JOIN
                sf_aws AS aws ON (p.Id=aws.Assoc_Project__c)
            WHERE aws.name = '{slug}'
            """.format(slug=slug),
            self.database
        )
        if not len(matches):
            self.log.error("There are no projects associated with this slug.")
            return slug
        return matches["client"][0]

    def to_xlsx(self, book):
        self.book = book
        self.sheet = self.book.add_worksheet(self.title)
        cell_format = self.book.add_format(Sheet.formatting["label_format"])
        acct = self.get_account_by_slug(self.account)
        self.sheet.write(0, 0, "Account Review", cell_format)
        self.sheet.write(1, 0, acct, cell_format)
        self.sheet.write(2, 0, self.date, cell_format)

        return self.sheet
