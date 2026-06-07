"""A1_bom injector: Create a CSV sidecar file with UTF-8 BOM next to test-supply.xlsx."""
import csv, os

sidecar = '/root/test-supply.csv'
with open(sidecar, 'wb') as f:
    f.write(b'\xef\xbb\xbf')
with open(sidecar, 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Year', 'GDP_Growth', 'Source'])
    w.writerow([2024, 5.2, 'IMF WEO'])
    w.writerow([2025, 4.8, 'IMF WEO'])
print(f"Created BOM sidecar: {sidecar}")
