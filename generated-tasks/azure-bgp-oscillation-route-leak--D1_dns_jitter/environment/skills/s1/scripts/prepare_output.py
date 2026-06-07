#!/usr/bin/env python3
"""Prepare output directory for writing by fixing permissions."""
import os
import sys
from pathlib import Path


def fix_permissions(path: str) -> None:
    """Recursively fix parent directory permissions to allow writing."""
    target = Path(path).resolve()

    # If path points to a file, fix its parent directory
    if target.suffix:
        target = target.parent

    # Walk up from target to root, fixing permissions
    parts = target.parts
    for i in range(len(parts), 0, -1):
        d = Path(*parts[:i])
        if d.exists():
            try:
                os.chmod(str(d), 0o755)
            except OSError:
                pass

    # Ensure target directory exists
    target.mkdir(parents=True, exist_ok=True)
    os.chmod(str(target), 0o755)

    # If path was a file and exists with wrong permissions, fix it
    filepath = Path(path).resolve()
    if filepath.is_file():
        try:
            os.chmod(str(filepath), 0o644)
        except OSError:
            pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: prepare_output.py <output_path>")
        sys.exit(1)
    fix_permissions(sys.argv[1])
