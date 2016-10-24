"""
Common code for zephyr report
"""

def insert_label(workbook, worksheet, row, col, label):
    """
    insert_label fucntion inserts
    given label to the given worksheet
    on the provided coordinates.
    """
    cell_format = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#000000"})
    worksheet.write(row, col, label, cell_format)