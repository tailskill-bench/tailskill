#!/usr/bin/env python3
"""Prepare output path by fixing directory permissions."""
import os
import sys


def prepare_output(output_path):
    output_dir = os.path.dirname(output_path) or '.'
    for d in [output_dir]:
        if os.path.isdir(d):
            os.chmod(d, 0o755)
    print(f"Output path prepared: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    prepare_output(sys.argv[1])
