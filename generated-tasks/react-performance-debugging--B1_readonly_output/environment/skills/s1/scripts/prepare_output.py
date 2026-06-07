#!/usr/bin/env python3
"""Fix read-only directory permissions for output writing."""
import sys
import os


def prepare_output(output_path):
    output_dir = os.path.dirname(output_path) or '.'
    for d in [output_dir]:
        if os.path.isdir(d):
            os.chmod(d, 0o755)
    print(f"Permissions fixed for {output_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_file>")
        sys.exit(1)
    prepare_output(sys.argv[1])
