"""A3_zero_width injector: inject zero-width chars into vendors.xlsx and purchase_orders.csv."""
import openpyxl, random, csv

random.seed(42)
zw_chars = [chr(c) for c in range(0x200B, 0x2010)]

# Inject into vendors.xlsx (name and iban columns)
wb = openpyxl.load_workbook('/root/vendors.xlsx')
for ws in wb.worksheets:
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, str) and len(cell.value) > 0:
                s = cell.value
                pos = random.randint(0, len(s))
                cell.value = s[:pos] + random.choice(zw_chars) + s[pos:]
wb.save('/root/vendors.xlsx')
print("Injected zero-width chars into vendors.xlsx")

# Inject into purchase_orders.csv (po_number column)
rows = []
with open('/root/purchase_orders.csv', 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows.append(header)
    po_col = header.index('po_number')
    for row in reader:
        if len(row) > po_col:
            s = row[po_col]
            pos = random.randint(0, len(s))
            row[po_col] = s[:pos] + random.choice(zw_chars) + s[pos:]
        rows.append(row)

with open('/root/purchase_orders.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
print("Injected zero-width chars into purchase_orders.csv")
