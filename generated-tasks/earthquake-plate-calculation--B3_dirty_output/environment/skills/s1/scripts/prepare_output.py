#!/usr/bin/env python3
"""Prepare output file for writing by fixing permissions and removing stale content."""
import os
import sys


def prepare_output(output_path):
    """Fix permissions on output file to allow overwriting."""
    if os.path.exists(output_path):
        os.chmod(output_path, 0o644)
        print(f"Fixed permissions: {output_path} -> 644")
    output_dir = os.path.dirname(output_path)
    if output_dir:
        output_dir = output_dir.rstrip('/')
        if os.path.isdir(output_dir):
            os.chmod(output_dir, 0o755)
            print(f"Fixed permissions: {output_dir} -> 755")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    prepare_output(sys.argv[1])
