"""Fix read-only directory permissions so output can be written."""
import os, sys

dirs_to_fix = ["/root"]
for d in dirs_to_fix:
    if os.path.isdir(d):
        os.chmod(d, 0o755)
        print(f"Fixed permissions: {d} -> 755")

if len(sys.argv) > 1:
    outdir = os.path.dirname(sys.argv[1])
    if outdir and os.path.isdir(outdir):
        os.chmod(outdir, 0o755)
        print(f"Fixed permissions: {outdir} -> 755")
