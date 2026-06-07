#!/usr/bin/env python3
"""Fix read-only output directory permissions."""
import os
import sys

for path in sys.argv[1:]:
    d = os.path.dirname(path)
    while d and d != '/':
        try:
            os.chmod(d, 0o755)
        except OSError:
            pass
        d = os.path.dirname(d)
    print(f"Fixed permissions for output: {path}")
