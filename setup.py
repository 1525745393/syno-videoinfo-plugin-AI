"""Package script for this plugin."""
import string
from pathlib import Path

from setuptools import setup

from version import version

# get the root directory of this plugin
ROOT_DIR = Path(__file__).resolve().parent

# hardcode the correct plugin ID from git repository name
PLUGIN_ID = "syno-videoinfo-plugin-AI"

# write the INFO file for this plugin
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

# use 'python setup.py sdist --formats=zip' command to create the zip file
setup(
    name=PLUGIN_ID,
    version=version(),
    packages=[
        "",
        "scraper",
        "scraper.functions",
        "scrapeflows",
        "configserver"
    ],
    package_data={
        "": ["run.sh", "resolvers.conf", "INFO", "config.example.json", ".env.example"],
        "scrapeflows": ["*.json"],
        "configserver": ["templates/*.html"],
    },
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
        "yaml": [
            "PyYAML>=5.0"
        ],
    },
)
