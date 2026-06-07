#!/usr/bin/env python3
"""Prepare output directory: fix permissions for B1_readonly_output variant."""
import os
import sys
from pathlib import Path


def fix_permissions(output_path: str):
    """Recursively fix parent directory permissions to allow writing."""
    p = Path(output_path).resolve()
    # Fix all parent directories up to /root
    parts = p.parts
    for i in range(1, len(parts) + 1):
        d = Path(*parts[:i])
        if d.exists():
            try:
                os.chmod(str(d), 0o755)
            except OSError:
                pass
    # Create output directory if it doesn't exist
    p.mkdir(parents=True, exist_ok=True)
    # Remove any pre-existing dirty files in output directory
    if p.is_dir():
        for f in p.iterdir():
            try:
                f.unlink()
            except OSError:
                pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    fix_permissions(sys.argv[1])
