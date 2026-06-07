"""Remove corrupted output file and fix directory write permissions."""
import os, stat

output = '/root/test-supply.xlsx'
if os.path.exists(output):
    with open(output, 'rb') as f:
        header = f.read(4)
    if not header.startswith(b'PK'):
        os.remove(output)
        print(f"Removed corrupted file: {output}")

for d in ["/root"]:
    if os.path.isdir(d):
        os.chmod(d, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        print(f"Fixed permissions on {d}")
