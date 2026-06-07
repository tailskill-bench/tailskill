#!/usr/bin/env python3
"""Prepare output directory — fix read-only permissions for B1_readonly_output variant."""
import os
import sys


def prepare(output_path):
    for d in ["/root/output"]:
        if os.path.isdir(d) and not os.access(d, os.W_OK):
            os.chmod(d, 0o755)
    out_dir = os.path.dirname(output_path)
    if out_dir and os.path.isdir(out_dir) and not os.access(out_dir, os.W_OK):
        os.chmod(out_dir, 0o755)
    if os.path.exists(output_path):
        os.remove(output_path)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/root/output/output.nc"
    prepare(target)
