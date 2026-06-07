#!/usr/bin/env python3
"""Output preparation helper — ensures output directory is writable and clean."""

import os
import stat
import sys


def prepare_output(output_path):
    """Ensure the output directory exists and is writable."""
    output_dir = os.path.dirname(output_path) or '.'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    elif not os.access(output_dir, os.W_OK):
        os.chmod(output_dir, stat.S_IRWXU)
        print(f"[prepare_output] Fixed permissions on {output_dir}")

    # Also check parent if output_dir is a subdirectory
    parent = os.path.dirname(output_dir)
    if parent and not os.access(parent, os.W_OK):
        os.chmod(parent, stat.S_IRWXU)
        print(f"[prepare_output] Fixed permissions on {parent}")


def main():
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_file>")
        sys.exit(1)

    prepare_output(sys.argv[1])


if __name__ == "__main__":
    main()
