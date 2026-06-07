#!/usr/bin/env python3
"""Remove dirty output file and fix permissions"""
import os
import stat

output_file = "/root/results.csv"
if os.path.exists(output_file):
    os.remove(output_file)
    print(f"Removed dirty output: {output_file}")

for p in ['/root/data', '/root']:
    if os.path.exists(p):
        os.chmod(p, os.stat(p).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        for root, dirs, files in os.walk(p):
            for f in files:
                fp = os.path.join(root, f)
                os.chmod(fp, os.stat(fp).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
print("Fixed output")
