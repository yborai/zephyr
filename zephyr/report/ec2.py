import xlsxwriter

from operator import itemgetter
from ..core.ddh import DDH
from ..data.compute_details import ComputeDetailsWarp
from .common import ( 
    book_formats,
    chart_dimensions,
    count_by,
    count_by_pie_chart,
    header_format_xlsx,
    put_chart,
    put_label,
    put_table,
    rows_to_excel
)

def count_by_column_chart(
    book, sheet, column_name, ddh, top, left, name, formatting
):
    """Insert a column chart with data specified."""
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    table_left = int(chart_width) + cell_spacing
    table_top = top + 1 # Account for label.

    # Get first 4 data rows
    header, data_ = count_by(ddh.header, ddh.data, column_name)
    data = data_[:4]

    # Rollup remaining values into "other" column
    other_values = [item[1] for item in data_[4:]]
    other_row = ["Other", sum(other_values)]

    # Append data
    data.append(other_row)
    data = sorted(data, key=itemgetter(1), reverse=True)
    counts = DDH(header=header, data=data)

    put_label(book, sheet, column_name, top, table_left, formatting=formatting)

    # Write the data table to the sheet.
    sheet = put_table(
        book,
        sheet,
        counts,
        top=table_top,
        left=table_left,
        name=name,
        formatting=formatting,
    )
    # Compute series information.
    table_loc = (
        table_top + 1,
        table_top + len(data),
        table_left,
        table_left + 1,
    )
    dlf = dict()
    dlf.update(formatting["data_labels"])
    dlf["category"] = False
    dlf["value"] = True
    ccf = dict(
        legend_options=formatting["legend_options"],
        data_labels=dlf
    )
    put_chart(book, sheet, column_name, top, left, table_loc, "column", ccf)
    return book

def ec2_sheet(book, ddh, title, name=None, formatting=None):
    """Format the sheet and insert the data for the SR report."""
    # Insert raw report data.
    sheet = book.add_worksheet(title)
    put_label(book, sheet, title, formatting=formatting)

    put_table(
        book, sheet, ddh, top=1, name=name, formatting=formatting
    )

    # Where charts and other tables go
    chart_width, chart_height, cell_spacing = chart_dimensions(formatting)
    n_rows = len(ddh.data)
    table_height = n_rows + 1
    chart_start_row = 1 + table_height + cell_spacing
    table_left = int(chart_width) + cell_spacing
    chart_ceil = int(chart_height) + 1

    # Insert instances by region.
    count_by_pie_chart(
        book, sheet, "Region", ddh, chart_start_row, 0, "ec2_region", formatting
    )

    # Insert instances by platform
    platform_top = chart_start_row + chart_ceil + cell_spacing
    count_by_pie_chart(
        book, sheet, "PricingPlatform", ddh, platform_top, 0, "pric_plat", formatting
    )

    # Insert instances by type
    instance_top = platform_top + chart_ceil + cell_spacing # Account for second chart
    count_by_column_chart(
        book, sheet, "InstanceType", ddh, instance_top, 0, "instance_type", formatting
    )
    return sheet

def ec2_xlsx(book=None, json_string=None, formatting=None):
    """Save a list of EC2 instances in an Excel workbook."""
    ddh = ComputeDetailsWarp(json_string).to_ddh()
    title = "EC2 Details"
    name = "EC2s"
    if not book:
        options = formatting["book_options"]
        with xlsxwriter.Workbook("ec2.xlsx", options) as book:
            return ec2_sheet(book, ddh, title, name=name, formatting=formatting)
    return ec2_sheet(book, ddh, title, name=name, formatting=formatting)
