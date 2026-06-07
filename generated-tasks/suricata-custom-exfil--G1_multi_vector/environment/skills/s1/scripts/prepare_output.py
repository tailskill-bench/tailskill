#!/usr/bin/env python3
"""Fix permissions and reinstall missing deps for G1_multi_vector variant."""
import os
import sys
import stat
import subprocess


def fix_permissions(path):
    target = os.path.dirname(path) if os.path.isfile(path) else path
    p = target
    while p and p != '/':
        try:
            mode = os.stat(p).st_mode
            if not (mode & stat.S_IWUSR):
                os.chmod(p, mode | stat.S_IWUSR | stat.S_IXUSR)
        except OSError:
            pass
        p = os.path.dirname(p)


def ensure_scapy():
    try:
        import scapy
        print("scapy already available")
    except ImportError:
        print("scapy not found, installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'scapy==2.5.0', '--no-cache-dir'], check=True)
        print("scapy installed successfully")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    fix_permissions(sys.argv[1])
    ensure_scapy()
    print(f"Fixed: {sys.argv[1]}")
