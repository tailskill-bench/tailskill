#!/usr/bin/env python3
"""B1_readonly_output variant: Fix read-only output directory permissions."""

import os
import stat
import sys


def prepare_output(filepath):
    """Make the parent directory of filepath writable."""
    dir_path = os.path.dirname(os.path.abspath(filepath))
    os.makedirs(dir_path, exist_ok=True)
    # Fix read-only permissions: grant owner rwx, group/other r-x
    os.chmod(dir_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_file_path>", file=sys.stderr)
        sys.exit(1)
    prepare_output(sys.argv[1])
