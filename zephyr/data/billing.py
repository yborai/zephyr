"""
Billing CSV passthrough
"""
import csv

def data(cache="billing-monthly.csv"):
    with open(cache, "r") as f:
        reader = csv.DictReader(f)
        out = [reader.fieldnames] + [[row[col] for col in reader.fieldnames] for row in reader]
    return out

