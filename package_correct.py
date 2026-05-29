#!/usr/bin/env python3
"""正确的打包脚本 - 模仿原始setup.py的sdist方式
"""
import os
import zipfile
from pathlib import Path
import string

version = "1.4.5"
plugin_id = "syno-videoinfo-plugin"

# 生成INFO文件
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

with open("INFO", "w", encoding="utf-8") as f:
    template = string.Template(INFO_TMPL)
    f.write(template.substitute(plugin_id=plugin_id, version=version))

# 清理旧的构建
if os.path.exists("dist"):
    import shutil
    shutil.rmtree("dist")
os.makedirs("dist", exist_ok=True)

# 创建zip文件 - 使用原始方式（类似setup.py的sdist
zip_path = f"dist/{plugin_id}-{version}.zip"

# 需要包含的文件和目录
include_files = [
    "run.sh",
    "INFO",
    "main.py",
    "version.py",
    "resolvers.conf",
    "config.example.json",
    ".env.example",
    "source_groups.json",
]

include_dirs = [
    "scraper",
    "scrapeflows",
    "configserver",
]

# 排除的文件
exclude_extensions = [".pyc", ".pyo", ".pyd", ".so", ".o", ".a", ".zip", ".egg-info"]
exclude_dirs = ["__pycache__", ".git", ".idea", "dist", "tests", "docs", "source_data", "temp_build"]
exclude_patterns = [".backup", "~", "test_"]

print(f"正在创建发布包: {zip_path}")

with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
    # 添加根目录文件
    for filename in include_files:
        filepath = Path(filename)
        if filepath.exists():
            zipf.write(filename, filename)
            print(f"  添加: {filename}")

    # 添加目录
    for dirname in include_dirs:
        dirpath = Path(dirname)
        if dirpath.exists() and dirpath.is_dir():
            for root, dirs, files in os.walk(dirname):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    # 排除不需要的文件扩展名
                    if any(file.endswith(ext) for ext in exclude_extensions):
                        continue
                    # 排除特定模式
                    if any(pattern in file for pattern in exclude_patterns):
                        continue
                    
                    filepath = os.path.join(root, file)
                    arcname = filepath
                    zipf.write(filepath, arcname)
                    print(f"  添加: {arcname}")

print(f"\n✅ 发布包创建成功: {zip_path}")

# 验证
print(f"\n文件大小: {os.path.getsize(zip_path) / 1024:.1f} KB")
print("内容:")
with zipfile.ZipFile(zip_path, "r") as zipf:
    for name in zipf.namelist()[:20]:
        print(f"  {name}")
    if len(zipf.namelist()) > 20:
        print(f"  ... 还有 {len(zipf.namelist()) - 20} 个文件")
