#!/usr/bin/env python3
"""Fix read-only permissions on output directory."""
import os, stat, sys

target = sys.argv[1] if len(sys.argv) > 1 else "/root"
os.chmod(target, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
print(f"Fixed permissions on {target}")
