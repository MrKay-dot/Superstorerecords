"""Refresh the static dashboard data from the checked-in source workbook."""
import csv
from pathlib import Path
from datetime import datetime, date
import openpyxl

root = Path(__file__).resolve().parent.parent
columns = ['Order ID', 'Order Date', 'Region', 'Segment', 'Category', 'Sub-Category', 'Product Name', 'Quantity', 'Sales', 'Profit', 'State', 'Sales Rep', 'Sales Team Manager']
workbook = openpyxl.load_workbook(root / 'SuperStoreData.xlsx', read_only=True, data_only=True)
rows = iter(workbook.active.values)
headers = next(rows)
indices = [headers.index(column) for column in columns]
with (root / 'public' / 'sales.csv').open('w', newline='', encoding='utf-8') as output:
    writer = csv.writer(output)
    writer.writerow(columns)
    for row in rows:
        values = [row[index] for index in indices]
        if any(values[columns.index(column)] is None for column in ['Order Date', 'Sales', 'Profit', 'Quantity']):
            continue
        writer.writerow([value.isoformat()[:10] if isinstance(value, (datetime, date)) else value for value in values])
workbook.close()
