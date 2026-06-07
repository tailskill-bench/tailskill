#!/usr/bin/env python3
"""Prepare output directory for writing by fixing permissions."""
import os
import sys


def prepare_output(output_path):
    """Fix directory permissions to allow writing."""
    output_dir = output_path if os.path.isdir(output_path) else os.path.dirname(output_path)
    if output_dir:
        output_dir = output_dir.rstrip('/')
        for d in [output_dir]:
            if os.path.isdir(d):
                os.chmod(d, 0o755)
                print(f"Fixed permissions: {d} -> 755")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    prepare_output(sys.argv[1])
