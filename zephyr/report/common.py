"""
Common code for zephyr report
"""

import sqlite3
import pandas as pd

def group_data(header, data, review_type):
    con = sqlite3.connect(":memory:")
    srs = pd.DataFrame(data, columns=header)

    sr_sql = srs.to_sql("srs", con, if_exists="replace")
    query = """
        SELECT
             {col},
             count({col}) as Total 
         FROM
             srs
         GROUP BY {col}
    """.format(col=review_type)
    
    sql_group = pd.read_sql(query, con)
    header = list(sql_group)
    data = [list(row) for row in sql_group.values]

    return header, data

def insert_label(workbook, worksheet, row, col, label, formatting=None):
    """
    insert_label fucntion inserts
    given label to the given worksheet
    on the provided coordinates.
    """
    cell_format = workbook.add_format(formatting["label_format"])
    worksheet.write(row, col, label, cell_format)