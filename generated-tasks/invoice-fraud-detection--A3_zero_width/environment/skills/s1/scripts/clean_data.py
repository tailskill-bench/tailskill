"""Strip zero-width Unicode characters from vendors.xlsx and purchase_orders.csv."""
import openpyxl, unicodedata, csv

# Clean XLSX
wb = openpyxl.load_workbook('/root/vendors.xlsx')
count = 0
for ws in wb.worksheets:
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, str):
                cleaned = ''.join(c for c in cell.value if unicodedata.category(c) != 'Cf')
                if cleaned != cell.value:
                    cell.value = cleaned
                    count += 1
wb.save('/root/vendors.xlsx')
print(f"Cleaned {count} cells in vendors.xlsx")

# Clean CSV
rows = []
with open('/root/purchase_orders.csv', 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append([''.join(c for c in v if unicodedata.category(c) != 'Cf') for v in row])

with open('/root/purchase_orders.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
print("Cleaned purchase_orders.csv")
