"""Version number management."""
import subprocess
import sys

__all__ = ["version"]


def version():
    """Extract the version number from git describe command."""
    try:
        cmd = "git describe --tags --match v[0-9]*".split()
        tag_describe = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode().strip()
        tag_version = tag_describe[1:]
        if "-" in tag_version:
            tag_version = tag_version.split("-", 1)[0]
        return tag_version
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        # Fallback to default version if git is not available
        return "1.4.5"

