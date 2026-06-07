"""A1_bom injector: create CSV sidecar with UTF-8 BOM next to vendors.xlsx."""
import csv

sidecar = '/root/vendors.csv'
with open(sidecar, 'wb') as f:
    f.write(b'\xef\xbb\xbf')
with open(sidecar, 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 'name', 'iban'])
    w.writerow([1, 'Test Vendor', 'XX00TEST000'])
print(f"Created BOM sidecar: {sidecar}")
