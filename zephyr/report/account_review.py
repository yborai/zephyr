import os
import csv
import shutil

import xlsxwriter

from cement.core import controller

from ..data import (
    billing,
    compute_migration,
    compute_underutilized,
    compute_underutilized_breakdown,
    db_details,
    ri_pricings,
)

from .common import formatting, rows_to_excel
from .ec2 import ec2_xlsx
from .rds import rds_xlsx
from .ri_recs import ri_xlsx
from .sr import sr_xlsx

def insert_label(workbook, worksheet, row, col, label, formatting=None):
    """
    insert_label fucntion inserts
    given label to the given worksheet
    on the provided coordinates.
    """
    cell_format = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#000000"})
    worksheet.write(row, col, label, cell_format)

def create_review_sheet(
        workbook, review_json, module, sheet_name, temp_filepath, table_name,
        temp_filename="temp.csv"
    ):
    """
    create_review_sheet function creates a new worksheet
    inside the provided workbook and fills it with a data
    from prom provided review_json processed with given module's
    create_sheet function.
    """
    if review_json is not None:
        review_sheet = module.create_sheet(
            review_json, temp_filepath + "/" + temp_filename
        )
        write_csv_to_worksheet(workbook, sheet_name, review_sheet, table_name, sheet_name)
        return review_sheet

def create_headers(workbook, csv_reader, total_row):
    header_format = workbook.add_format({"font_color": "#000000", "bg_color": "#DCE6F1", "bottom": 2})
    headers = next(csv_reader)
    header = [{"header": col, "header_format": header_format} for col in headers]
    if total_row:
        header[0]["total_string"] = "Total"
    return header

def write_csv_to_worksheet(workbook, worksheet_name, csv_filepath, table_name, title):
    """
    write_csv_to_worksheet function creates a new worksheet
    inside the provided workbook
    and writes data from csv file to it.
    Workseet object is returned.
    """

    current_worksheet = workbook.add_worksheet(worksheet_name)

    with open(csv_filepath, "r") as f:
        reader = csv.reader(f)
        header = create_headers(workbook, reader, True)
        f.seek(0)
        row_index = 1
        column_index = 0
        insert_label(workbook, current_worksheet, 0, 0, title)
        for row in reader:
            column_index = 0
            for col in row:
                current_worksheet.write(row_index, column_index, col)
                column_index += 1
            row_index += 1
        current_worksheet.add_table(1, 0,row_index, column_index-1,
            {
                "columns": header, "name": table_name,
                "style": "Table Style Light 1", "total_row": True
            }
        )

    return current_worksheet


def insert_csv_to_worksheet(workbook, worksheet, csv_filepath, start_row, start_col, table_name):
    """
    insert_csv_to_worksheet function inserts
    data from csv file to the given worksheet.
    The data table starts from given row and column.
    """
    with open(csv_filepath, "r") as f:
        reader = csv.reader(f)
        header = create_headers(workbook, reader, False)
        f.seek(0)
        row_index = start_row
        for row in reader:
            column_index = start_col
            for col in row:
                worksheet.write(row_index, column_index, col)
                column_index += 1
            row_index += 1
        worksheet.add_table(
            start_row, start_col, row_index, column_index-1,
            {
                "columns": header, "name": table_name,
                "style": "Table Style Light 1", "total_row": True
            }
        )

def create_temp_folder(destination_filepath, temporary_folder_name):
    path = destination_filepath + "/" + temporary_folder_name
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def remove_temp_folder(temp_filepath):
    shutil.rmtree(temp_filepath)

def billing_table(book, sheet, rows, table_name, top=1, left=0):
    """
    Take rows, an iterable of iterables, and write it to a given sheet
    with the top, left cell at (top, left).
    """
    header = rows[0]
    header_format = book.add_format({
        "font_color": "#000000",
        "bg_color": "#DCE6F1",
        "bottom": 2}
    )
    header = [{"header": name, "header_format": header_format} for name in header]

    rows_to_excel(sheet, rows, top=top, left=left)

    n_rows = len(rows)
    n_cols = len(header)
    sheet.add_table(top, left, top+n_rows-1, left+n_cols-1,
        {
            "columns": header, "name": table_name,
            "style": "Table Style Light 1"
        }
    )
    return book

def create_xlsx_account_review(
        destination_filepath,
        xslx_filename="account_review.xlsx",
        billing_monthly_cache=None,
        billing_line_items_cache=None,
        billing_line_item_aggs_cache=None,
        service_requests_json=None,
        ec2_details_json=None,
        rds_details_json=None,
        ec2_ri_recommendations_json=None,
        ri_pricing_csv=None,
        ec2_migration_recommendations_json=None,
        ec2_underutilized_instances_json=None,
        define_category_func=None,
        temporary_folder_name="temp"
    ):
    """
    create_xlsx_account_review function
    creates full review from the given data
    and stores it in xslx file with provided name.
    Only reviews with not `None` values are mentioned in total review.
    """
    workbook = xlsxwriter.Workbook(destination_filepath + "/" + xslx_filename, {"strings_to_numbers": True})
    temp_filepath = create_temp_folder(destination_filepath, temporary_folder_name)

    monthly_totals = billing.data(billing_monthly_cache)
    line_items = billing.data(billing_line_items_cache)
    line_item_aggs = billing.data(billing_line_item_aggs_cache)

    sheet_dy = workbook.add_worksheet("Billing")

    insert_label(workbook, sheet_dy, 0, 0, "Billing")
    billing_table(workbook, sheet_dy, line_items, "LineItems")
    billing_table(workbook, sheet_dy, line_item_aggs, "LineItemAggs", top=1, left=8)
    billing_table(workbook, sheet_dy, monthly_totals, "Monthly", top=len(line_item_aggs)+2, left=8)

    ec2_xlsx(workbook, ec2_details_json, formatting)

    rds_xlsx(workbook, rds_details_json, formatting)

    ri_xlsx(workbook, ec2_ri_recommendations_json, formatting)

    create_review_sheet(
        workbook, ec2_migration_recommendations_json, compute_migration,
        "EC2 Migration Recommendations", temp_filepath, "Migrations"
    )

    create_review_sheet(
        workbook, ri_pricing_csv, ri_pricings,
        "RI Pricing", temp_filepath, "Pricings"
    )

    if service_requests_json is not None:
        sr_xlsx(workbook, service_requests_json, formatting)

    if ec2_underutilized_instances_json is not None:
        ec2_underutilized_instances_sheet = compute_underutilized.create_sheet(
            ec2_underutilized_instances_json,
            temp_filepath + "/" + "ec2_underutilized_instances.csv"
        )
        ec2_underutilized_instances_xls_sheet = write_csv_to_worksheet(
            workbook, "EC2 underutilized instances", ec2_underutilized_instances_sheet, "Underutil", "EC2 Underutilized Instances"
        )

        if define_category_func is not None:
            ec2_underutilized_breakdown_sheet = compute_underutilized_breakdown.create_sheet(
                ec2_underutilized_instances_json,
                define_category_func,
                temp_filepath + "/" + "ec2_underutilized_instances_breakdown.csv"
            )

            insert_label(
                workbook, ec2_underutilized_instances_xls_sheet, 0, 8,
                "Breakdown of Underutilized EC2 Instances"
            )
            insert_csv_to_worksheet(
                workbook, ec2_underutilized_instances_xls_sheet, ec2_underutilized_breakdown_sheet, 1, 8, "Breakdown"
            )

    remove_temp_folder(temp_filepath)
    workbook.close()

