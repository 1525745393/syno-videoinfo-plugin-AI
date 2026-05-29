#!/usr/bin/env python3
"""手动打包脚本 - 不依赖setuptools"""
import os
import zipfile
from pathlib import Path
import sys

# 导入版本函数
def get_version():
    """获取版本号"""
    try:
        import subprocess
        cmd = "git describe --tags --match v[0-9]*".split()
        tag_describe = subprocess.check_output(cmd, stderr=subprocess.PIPE).decode().strip()
        tag_version = tag_describe[1:]
        if "-" in tag_version:
            tag_version = tag_version.split("-", 1)[0]
        return tag_version
    except (subprocess.CalledProcessError, OSError, FileNotFoundError):
        return "1.4.5"

VERSION = get_version()
PLUGIN_ID = "syno-videoinfo-plugin"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)

# 生成INFO文件
INFO_CONTENT = f"""{{
  "id": "{PLUGIN_ID}-{VERSION}",
  "entry_file": "run.sh",
  "type": ["movie", "tvshow"],
  "language": ["chs"],
  "test_example": {{
    "movie": {{
      "title": "--install"
    }},
    "tvshow": {{
      "title": "--install"
    }},
    "tvshow_episode": {{
      "title": "--install",
      "season": 1,
      "episode": 1
    }}
  }}
}}
"""

with open("INFO", "w", encoding="utf-8") as f:
    f.write(INFO_CONTENT)

# 需要包含的文件
INCLUDE_FILES = [
    "run.sh",
    "INFO",
    "main.py",
    "version.py",
    "resolvers.conf",
    "config.example.json",
    ".env.example",
    "source_groups.json",
]

# 需要包含的目录
INCLUDE_DIRS = [
    "scraper",
    "scrapeflows",
    "configserver",
]

# 排除的文件
EXCLUDE_EXTENSIONS = [".pyc", ".pyo", ".pyd", ".so", ".o", ".a"]
EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", "dist", "tests", "docs", "source_data"]
EXCLUDE_PATTERNS = [".backup", "~"]

print(f"🎁 正在打包 Syno VideoInfo Plugin v{VERSION}")
print("=" * 60)

ZIP_PATH = DIST_DIR / f"{PLUGIN_ID}-{VERSION}.zip"

with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zipf:
    # 添加根目录文件
    for filename in INCLUDE_FILES:
        filepath = Path(filename)
        if filepath.exists():
            zipf.write(filename, filename)
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} (不存在，跳过)")
    
    # 添加目录
    for dirname in INCLUDE_DIRS:
        dirpath = Path(dirname)
        if dirpath.exists() and dirpath.is_dir():
            for root, dirs, files in os.walk(dirname):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
                
                for file in files:
                    # 排除不需要的文件扩展名
                    if any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                        continue
                    
                    # 排除包含特定模式的文件
                    if any(pattern in file for pattern in EXCLUDE_PATTERNS):
                        continue
                    
                    filepath = os.path.join(root, file)
                    arcname = filepath
                    zipf.write(filepath, arcname)
                    print(f"  ✓ {arcname}")

print("=" * 60)
print(f"\n✅ 打包完成！")
print(f"📦 输出文件: {ZIP_PATH}")
print(f"📊 文件大小: {ZIP_PATH.stat().st_size / 1024 / 1024:.2f} MB")

# 验证包内容
print("\n📋 包内容统计:")
with zipfile.ZipFile(ZIP_PATH, "r") as zipf:
    all_files = zipf.namelist()
    py_files = [f for f in all_files if f.endswith(".py")]
    json_files = [f for f in all_files if f.endswith(".json")]
    html_files = [f for f in all_files if f.endswith(".html")]
    
    print(f"  总文件数: {len(all_files)}")
    print(f"  Python 文件: {len(py_files)}")
    print(f"  JSON 配置: {len(json_files)}")
    print(f"  HTML 模板: {len(html_files)}")
