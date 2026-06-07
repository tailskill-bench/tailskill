#!/usr/bin/env python3
"""Fix readonly permissions on output directory"""
import os
import stat

def make_writable(path):
    if os.path.exists(path):
        os.chmod(path, os.stat(path).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        for root, dirs, files in os.walk(path):
            for d in dirs:
                dp = os.path.join(root, d)
                os.chmod(dp, os.stat(dp).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            for f in files:
                fp = os.path.join(root, f)
                os.chmod(fp, os.stat(fp).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

for p in ['/root/data', '/root']:
    make_writable(p)
print("Fixed permissions")
