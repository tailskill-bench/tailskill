"""Strip zero-width Unicode characters from data.xlsx cell values."""
import openpyxl, unicodedata

wb = openpyxl.load_workbook('/root/data.xlsx')
count = 0
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                cleaned = ''.join(c for c in cell.value if unicodedata.category(c) != 'Cf')
                if cleaned != cell.value:
                    # Try to convert back to number if it was numeric
                    try:
                        cell.value = float(cleaned)
                        if cell.value == int(cell.value):
                            cell.value = int(cell.value)
                    except ValueError:
                        cell.value = cleaned
                    count += 1
wb.save('/root/data.xlsx')
print(f"Cleaned {count} cells with zero-width chars")
