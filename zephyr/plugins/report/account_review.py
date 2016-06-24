import os
import csv
import shutil

import xlsxwriter

from ..data import service_requests, ec2_details, rds_details, ec2_ri_recommendations
from ..data import ri_pricings
from ..data import ec2_migration_recommendations, ec2_underutilized_instances
from ..data import ec2_underutilized_instances_breakdown


def create_xlsx_account_review(
        destination_filepath, xslx_filename='account_review.xlsx',
        service_requests_json=None, ec2_details_json=None,
        rds_details_json=None, ec2_ri_recommendations_json=None, ri_pricing_csv=None,
        ec2_migration_recommendations_json=None, ec2_underutilized_instances_json=None,
        define_category_func=None,
        temporary_folder_name='temp'):
    """
    create_xlsx_account_review function
    creates full review from the given data
    and stores it in xslx file with provided name.
    Only reviews with not `None` values are mentioned in total review.
    """
    workbook = xlsxwriter.Workbook(destination_filepath + '/' + xslx_filename)
    temp_filepath = create_temp_folder(destination_filepath, temporary_folder_name)

    create_review_sheet(
        workbook, ec2_details_json, ec2_details, 'EC2 details', temp_filepath
    )
    create_review_sheet(
        workbook, rds_details_json, rds_details, 'RDS details', temp_filepath
    )

    create_review_sheet(
        workbook, ec2_ri_recommendations_json, ec2_ri_recommendations,
        'EC2 RI recommendations', temp_filepath
    )

    create_review_sheet(
        workbook, ec2_migration_recommendations_json, ec2_migration_recommendations,
        'EC2 migration recommendations', temp_filepath
    )

    create_review_sheet(
        workbook, ri_pricing_csv, ri_pricings,
        'RI pricing', temp_filepath
    )

    if service_requests_json is not None:
        service_sheet, area_sheet, severity_sheet = service_requests.create_sheet(
            service_requests_json, temp_filepath + '/' + 'service_requests.csv'
        )
        service_requests_sheet = write_csv_to_worksheet(workbook, 'Service requests', service_sheet)
        insert_label_to_worksheet(service_requests_sheet, 0, 6, "Summary")

        insert_csv_to_worksheet(service_requests_sheet, area_sheet, 1, 6)
        insert_csv_to_worksheet(service_requests_sheet, severity_sheet, 12, 6)

    if ec2_underutilized_instances_json is not None:
        ec2_underutilized_instances_sheet = ec2_underutilized_instances.create_sheet(
            ec2_underutilized_instances_json,
            temp_filepath + '/' + 'ec2_underutilized_instances.csv'
        )
        ec2_underutilized_instances_xls_sheet = write_csv_to_worksheet(
            workbook, 'EC2 underutilized instances', ec2_underutilized_instances_sheet
        )

        if define_category_func is not None:
            ec2_underutilized_breakdown_sheet = ec2_underutilized_instances_breakdown.create_sheet(
                ec2_underutilized_instances_json,
                define_category_func,
                temp_filepath + '/' + 'ec2_underutilized_instances_breakdown.csv'
            )

            insert_label_to_worksheet(
                ec2_underutilized_instances_xls_sheet, 0, 6,
                "Breakdown of Underutilized EC2 Instances"
            )
            insert_csv_to_worksheet(
                ec2_underutilized_instances_xls_sheet, ec2_underutilized_breakdown_sheet, 1, 6
            )

    remove_temp_folder(temp_filepath)
    workbook.close()


def create_review_sheet(
        workbook, review_json, module, sheet_name, temp_filepath, temp_filename='temp.csv'):
    """
    create_review_sheet function creates a new worksheet
    inside the provided workbook and fills it with a data
    from prom provided review_json processed with given module's
    create_sheet function.
    """
    if review_json is not None:
        review_sheet = module.create_sheet(
            review_json, temp_filepath + '/' + temp_filename
        )
        write_csv_to_worksheet(workbook, sheet_name, review_sheet)
        return review_sheet


def write_csv_to_worksheet(workbook, worksheet_name, csv_filepath):
    """
    write_csv_to_worksheet function creates a new worksheet
    inside the provided workbook
    and writes data from csv file to it.
    Workseet object is returned.
    """
    current_worksheet = workbook.add_worksheet(worksheet_name)

    with open(csv_filepath, 'r') as f:
        reader = csv.reader(f)

        row_index = 0
        for row in reader:
            column_index = 0
            for col in row:
                current_worksheet.write(row_index, column_index, col)
                column_index += 1
            row_index += 1

    return current_worksheet


def insert_csv_to_worksheet(worksheet, csv_filepath, start_row, start_col):
    """
    insert_csv_to_worksheet function inserts
    data from csv file to the given worksheet.
    The data table starts from given row and column.
    """
    with open(csv_filepath, 'r') as f:
        reader = csv.reader(f)
        row_index = start_row
        for row in reader:
            column_index = start_col
            for col in row:
                worksheet.write(row_index, column_index, col)
                column_index += 1
            row_index += 1


def insert_label_to_worksheet(worksheet, row, col, label):
    """
    insert_label_to_worksheet fucntion inserts
    given label to the given worksheet
    on the provided coordinates.
    """
    worksheet.write(row, col, label)


def create_temp_folder(destination_filepath, temporary_folder_name):
    path = destination_filepath + '/' + temporary_folder_name
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def remove_temp_folder(temp_filepath):
    shutil.rmtree(temp_filepath)
