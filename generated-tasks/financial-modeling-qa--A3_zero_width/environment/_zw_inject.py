"""A3_zero_width injector: inject zero-width Unicode chars into data.xlsx numeric cells."""
import openpyxl, random, unicodedata

wb = openpyxl.load_workbook('/root/data.xlsx')
zw_chars = [chr(c) for c in range(0x200B, 0x2010)]  # U+200B..U+200F

for ws in wb.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, (int, float)):
                s = str(cell.value)
                pos = random.randint(0, len(s))
                cell.value = s[:pos] + random.choice(zw_chars) + s[pos:]

wb.save('/root/data.xlsx')
print("Injected zero-width chars into data.xlsx")
