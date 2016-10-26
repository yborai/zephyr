import xlsxwriter

from .common import insert_label, group_data
from ..data.compute_details import ComputeDetailsWarp

def compute_details_xlsx(json_string, workbook=None):
    warp_ddh = ComputeDetailsWarp(json_string).to_ddh()
    if not workbook:
