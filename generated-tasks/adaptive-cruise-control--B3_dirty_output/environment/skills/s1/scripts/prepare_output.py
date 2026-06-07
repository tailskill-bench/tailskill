#!/usr/bin/env python3
"""Prepare output path: remove corrupted files and fix directory permissions."""
import sys
import os


def prepare_output(output_path):
    output_dir = os.path.dirname(output_path) or '.'
    for d in [output_dir]:
        if os.path.isdir(d):
            os.chmod(d, 0o755)
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed existing file: {output_path}")
    print(f"Output path prepared: {output_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_file>")
        sys.exit(1)
    prepare_output(sys.argv[1])
