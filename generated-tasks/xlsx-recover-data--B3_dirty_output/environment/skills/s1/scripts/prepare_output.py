#!/usr/bin/env python3
"""Remove corrupted output file and fix permissions"""
import os, sys

output = sys.argv[1] if len(sys.argv) > 1 else "/root/nasa_budget_recovered.xlsx"

if os.path.exists(output):
    os.remove(output)
    print(f"Removed corrupted file: {output}")

print(f"Output path ready: {output}")
