"""A1_bom injector: Create CSV sidecar with UTF-8 BOM next to data.xlsx."""
import csv, os

sidecar = '/root/data.csv'
with open(sidecar, 'wb') as f:
    f.write(b'\xef\xbb\xbf')
with open(sidecar, 'a', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Game', 'Turn', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6'])
    w.writerow([1, 1, 3, 5, 2, 6, 1, 4])
    w.writerow([1, 2, 4, 2, 6, 3, 5, 1])
print(f"Created BOM sidecar: {sidecar}")
