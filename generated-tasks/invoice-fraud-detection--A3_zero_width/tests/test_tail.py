import openpyxl, unicodedata, csv, pytest

class TestTailVariant:
    def test_no_zero_width_in_xlsx(self):
        wb = openpyxl.load_workbook('/root/vendors.xlsx')
        found = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    if isinstance(cell.value, str):
                        for ch in cell.value:
                            if unicodedata.category(ch) == 'Cf':
                                found.append(f"{ws.title}!{cell.coordinate}")
                                break
        wb.close()
        assert not found, f"Zero-width chars in vendors.xlsx: {found[:10]}"

    def test_no_zero_width_in_csv(self):
        with open('/root/purchase_orders.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                for j, val in enumerate(row):
                    for ch in val:
                        if unicodedata.category(ch) == 'Cf':
                            pytest.fail(f"Zero-width char in CSV row {i+1} col {j+1}")
