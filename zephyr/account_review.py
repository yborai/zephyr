import os
import csv
import shutil

import xlsxwriter

from . import service_requests, ec2_details, rds_details, ec2_ri_recommendations
from . import ec2_migration_recommendations, ec2_underutilized_instances
from . import ec2_underutilized_instances_breakdown


def create_xlsx_account_review(
        destination_filepath, xslx_filename='account_review.xlsx',
        service_requests_json=None, ec2_details_json=None,
        rds_details_json=None, ec2_ri_recommendations_json=None,
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

    if service_requests_json is not None:
        service_sheet, area_sheet, severity_sheet = service_requests.create_sheet(
            service_requests_json, temp_filepath + '/' + 'service_requests.csv'
        )
        service_requests_sheet = write_csv_to_worksheet(workbook, 'Service requests', service_sheet)
        insert_label_to_worksheet(service_requests_sheet, 0, 6, "Summary")

        insert_csv_to_worksheet(service_requests_sheet, area_sheet, 1, 6)
        insert_csv_to_worksheet(service_requests_sheet, severity_sheet, 12, 6)

    if ec2_details_json is not None:
        ec2_details_sheet = ec2_details.create_sheet(
            ec2_details_json, temp_filepath + '/' + 'ec2_details.csv'
        )
        write_csv_to_worksheet(workbook, 'EC2 details', ec2_details_sheet)

    if rds_details_json is not None:
        rds_details_sheet = rds_details.create_sheet(
            rds_details_json, temp_filepath + '/' + 'rds_details.csv'
        )
        write_csv_to_worksheet(workbook, 'RDS details', rds_details_sheet)

    if ec2_ri_recommendations_json is not None:
        ec2_ri_recommendations_sheet = ec2_ri_recommendations.create_sheet(
            ec2_ri_recommendations_json, temp_filepath + '/' + 'rds_details.csv'
        )
        write_csv_to_worksheet(workbook, 'EC2 RI recommendations', ec2_ri_recommendations_sheet)

    if ec2_migration_recommendations_json is not None:
        ec2_migration_recommendations_sheet = ec2_migration_recommendations.create_sheet(
            ec2_migration_recommendations_json, temp_filepath + '/' + 'rds_details.csv'
        )
        write_csv_to_worksheet(
            workbook, 'EC2 migration recommendations', ec2_migration_recommendations_sheet
        )

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
                ec2_underutilized_instances_xls_sheet, ec2_underutilized_breakdown_sheet, 1, 8
            )

    remove_temp_folder(temp_filepath)
    workbook.close()


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


def insert_csv_to_worksheet(worksheet, csv_filepath, row, col):
    """
    insert_csv_to_worksheet function inserts
    data from csv file to the given worksheet.
    The data table starts from given row and column.
    """
    with open(csv_filepath, 'r') as f:
        reader = csv.reader(f)
        row_index = 1
        for row in reader:
            column_index = 6
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
