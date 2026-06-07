#!/usr/bin/env python3
"""Fix output directory permissions for B1_readonly_output variant."""
import os
import sys
import stat


def fix_permissions(path):
    """Fix write permissions on the target path and parent directories."""
    target = os.path.dirname(path) if os.path.isfile(path) else path
    p = target
    while p and p != '/':
        try:
            mode = os.stat(p).st_mode
            if not (mode & stat.S_IWUSR):
                os.chmod(p, mode | stat.S_IWUSR | stat.S_IXUSR)
        except OSError:
            pass
        p = os.path.dirname(p)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    output = sys.argv[1]
    fix_permissions(output)
    print(f"Permissions fixed for {output}")
