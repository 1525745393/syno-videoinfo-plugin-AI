#!/usr/bin/env python3
"""Proper package creation script that matches original project structure."""
import os
import zipfile
from pathlib import Path
import string

# Version
from version import version

# Root dir
ROOT_DIR = Path(__file__).resolve().parent
PLUGIN_ID = ROOT_DIR.name

# Create INFO file
INFO_TMPL = """
{
  "id": "${plugin_id}-${version}",
  "entry_file": "run.sh",
  "type": ["movie", "tvshow"],
  "language": ["chs"],
  "test_example": {
    "movie": {
      "title": "--install"
    },
    "tvshow": {
      "title": "--install"
    },
    "tvshow_episode": {
      "title": "--install",
      "season": 1,
      "episode": 1
    }
  }
}
"""
with open(ROOT_DIR / "INFO", "w", encoding="utf-8") as writer:
    template = string.Template(INFO_TMPL)
    writer.write(template.substitute(plugin_id=PLUGIN_ID, version=version()))

# Clean dist
if os.path.exists("dist"):
    import shutil
    shutil.rmtree("dist")
os.makedirs("dist", exist_ok=True)

# Create zip
zip_filename = f"dist/{PLUGIN_ID}-{version()}.zip"
print(f"Creating package: {zip_filename}")

# Files to include at root level
root_files = [
    "INFO",
    "run.sh", 
    "main.py",
    "version.py",
    "resolvers.conf",
    "config.example.json",
    ".env.example",
    "source_groups.json"
]

# Directories to include (recursively)
include_dirs = [
    "scraper",
    "scrapeflows", 
    "configserver"
]

# Exclude patterns
exclude_patterns = [
    "__pycache__",
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".o",
    ".a",
    ".backup",
    "~"
]

with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    # Add root files
    for filename in root_files:
        file_path = ROOT_DIR / filename
        if file_path.exists():
            zipf.write(file_path, filename)
            print(f"  Added: {filename}")
    
    # Add directories
    for dir_name in include_dirs:
        dir_path = ROOT_DIR / dir_name
        if dir_path.exists() and dir_path.is_dir():
            for root, _, files in os.walk(dir_path):
                # Skip excluded directories
                if any(pat in root for pat in exclude_patterns):
                    continue
                    
                for file in files:
                    # Skip excluded file types
                    if any(file.endswith(ext) for ext in exclude_patterns):
                        continue
                    if any(pat in file for pat in exclude_patterns):
                        continue
                        
                    file_path = Path(root) / file
                    # Make archive path relative to plugin root
                    arcname = str(file_path.relative_to(ROOT_DIR))
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")

# Verify
print(f"\nPackage created: {zip_filename}")
print(f"Size: {os.path.getsize(zip_filename) / 1024:.1f} KB")
print("\nPackage contents (first 20 files):")
with zipfile.ZipFile(zip_filename, 'r') as zipf:
    for name in zipf.namelist()[:20]:
        print(f"  {name}")
    if len(zipf.namelist()) > 20:
        print(f"  ... and {len(zipf.namelist()) - 20} more files")
