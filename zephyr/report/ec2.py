import xlsxwriter

from .common import count_by
from ..data.compute_details import ComputeDetailsWarp

def compute_details_report(workbook=None, json_string=None, formatting=None):
    class_ddh = ComputeDetailsWarp(json_string).to_ddh()
    title = "EC2 Details"
