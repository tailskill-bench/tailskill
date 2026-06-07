#!/usr/bin/env python3
"""Output preparation helper — removes dirty pre-existing output files and ensures directory is writable."""

import os
import stat
import sys


def prepare_output(output_path):
    """Remove any existing dirty output file and ensure directory is writable."""
    # Remove pre-existing file (may be corrupted)
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"[prepare_output] Removed existing file: {output_path}")

    # Ensure directory exists and is writable
    output_dir = os.path.dirname(output_path) or '.'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    elif not os.access(output_dir, os.W_OK):
        os.chmod(output_dir, stat.S_IRWXU)
        print(f"[prepare_output] Fixed permissions on {output_dir}")


def main():
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_file>")
        sys.exit(1)

    prepare_output(sys.argv[1])


if __name__ == "__main__":
    main()
