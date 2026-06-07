import openpyxl, unicodedata, pytest

class TestTailVariant:
    def test_no_zero_width_in_xlsx(self):
        wb = openpyxl.load_workbook('/root/data.xlsx')
        found = []
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    if isinstance(cell.value, str):
                        for ch in cell.value:
                            if unicodedata.category(ch) == 'Cf':
                                found.append(f"{ws.title}!{cell.coordinate}")
                                break
        wb.close()
        assert not found, f"Zero-width chars still present in: {found}"
