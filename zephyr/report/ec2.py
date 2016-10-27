import xlsxwriter

from .common import insert_label, group_data, create_xlsx
from ..data.compute_details import ComputeDetailsWarp

def compute_details_report(workbook=None, json_string=None, formatting=None):
    class_ddh = ComputeDetailsWarp(json_string).to_ddh()
    title = "EC2 Details"
    create_xlsx(formatting=formatting, class_ddh=class_ddh, title=title)

