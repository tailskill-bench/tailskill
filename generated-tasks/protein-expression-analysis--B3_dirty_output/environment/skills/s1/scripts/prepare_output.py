#!/usr/bin/env python3
"""Detect corrupted output file and restore from backup."""
import os, shutil, sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root/protein_expression.xlsx"
bu_path = target.replace('.xlsx', '_backup.xlsx')

if os.path.exists(target):
    with open(target, 'rb') as f:
        header = f.read(4)
    if header != b'PK\x03\x04':
        os.remove(target)
        shutil.copy2(bu_path, target)
        print(f"Restored corrupted file from {bu_path}")
    else:
        print("File is valid XLSX, no action needed")
else:
    shutil.copy2(bu_path, target)
    print(f"Restored missing file from {bu_path}")
