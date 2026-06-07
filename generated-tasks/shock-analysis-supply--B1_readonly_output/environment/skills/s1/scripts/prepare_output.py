"""Fix directory write permissions for output."""
import os, stat

for d in ["/root"]:
    if os.path.isdir(d):
        os.chmod(d, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
        print(f"Fixed permissions on {d}")
