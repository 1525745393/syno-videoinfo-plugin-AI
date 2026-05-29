#!/usr/bin/env python3
"""创建GitHub Release并上传发布包"""
import os
import sys
import json
import requests
from pathlib import Path

def get_repo_info():
    """从git remote获取仓库信息"""
    import subprocess
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                             capture_output=True, text=True)
        url = result.stdout.strip()
        # 解析URL，格式类似：https://github.com/owner/repo.git
        if url.endswith('.git'):
            url = url[:-4]
        parts = url.split('/')
        owner = parts[-2]
        repo = parts[-1]
        return owner, repo
    except Exception as e:
        print(f"无法获取仓库信息: {e}", file=sys.stderr)
        return None, None

def main():
    # 获取仓库信息
    owner, repo = get_repo_info()
    if not owner or not repo:
        print("无法获取仓库信息", file=sys.stderr)
        return 1
    
    print(f"仓库: {owner}/{repo}")
    
    # 获取GitHub token
    # 尝试从git remote URL中提取
    import subprocess
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                             capture_output=True, text=True)
        url = result.stdout.strip()
        if 'x-access-token:' in url:
            token_part = url.split('@')[0].split('x-access-token:')[1]
            token = token_part
        else:
            token = os.environ.get('GITHUB_TOKEN')
    except:
        token = os.environ.get('GITHUB_TOKEN')
    
    if not token:
        print("未找到GitHub token，请设置GITHUB_TOKEN环境变量", file=sys.stderr)
        return 1
    
    # Release信息
    tag_name = "v1.4.5"
    release_name = "v1.4.5 - 源管理系统增强版"
    release_body = """## Syno VideoInfo Plugin v1.4.5

### ✨ 主要更新

- 🎯 **完整的源管理系统** - 健康监控、智能排序、优先级管理
- 🎨 **现代化Web界面** - 源管理仪表盘、实时状态监控
- 📊 **73+ 刮削源** - 覆盖各类影视元数据
- 🔧 **配置管理系统** - 灵活的配置选项
- 📈 **性能监控** - 实时统计和健康检查
- 🧪 **完整测试套件** - 44个单元和集成测试

### 📦 安装

1. 下载下方的 `syno-videoinfo-plugin-1.4.5.zip`
2. 打开群晖 **Video Station** → **设置** → **视频信息插件**
3. 点击 **[新增]**，选择下载的 zip 文件

### 🚀 功能特性

- 零依赖，纯 Python 实现
- 73+ 刮削源（电影、电视剧、动漫、成人内容等）
- Web 配置界面（访问 `http://<NAS_IP>:5125`）
- 源管理界面（访问 `http://<NAS_IP>:5125/sourcemgmt`）
- 智能排序和健康监控
- 完整的测试和文档
"""
    
    # API端点
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 检查是否已存在Release
    print("检查是否已存在Release...")
    try:
        response = requests.get(f"{api_url}/tags/{tag_name}", headers=headers)
        if response.status_code == 200:
            print(f"Release {tag_name} 已存在")
            release = response.json()
            release_id = release['id']
            upload_url = release['upload_url'].split("{")[0]
        else:
            # 创建新Release
            print("创建新的Release...")
            data = {
                "tag_name": tag_name,
                "name": release_name,
                "body": release_body,
                "draft": False,
                "prerelease": False
            }
            response = requests.post(api_url, json=data, headers=headers)
            if response.status_code not in (200, 201):
                print(f"创建Release失败: {response.status_code}")
                print(response.text, file=sys.stderr)
                return 1
            release = response.json()
            release_id = release['id']
            upload_url = release['upload_url'].split("{")[0]
            print(f"Release创建成功: {release['html_url']}")
    except Exception as e:
        print(f"处理Release时出错: {e}", file=sys.stderr)
        return 1
    
    # 上传发布包
    zip_file = Path("dist/syno-videoinfo-plugin-1.4.5.zip")
    if zip_file.exists():
        print(f"上传发布包: {zip_file.name}")
        try:
            with open(zip_file, 'rb') as f:
                upload_headers = headers.copy()
                upload_headers["Content-Type"] = "application/zip"
                upload_response = requests.post(
                    f"{upload_url}?name={zip_file.name}",
                    data=f,
                    headers=upload_headers
                )
            if upload_response.status_code in (200, 201):
                print(f"✓ 发布包上传成功！")
            else:
                print(f"上传失败: {upload_response.status_code}")
                print(upload_response.text, file=sys.stderr)
        except Exception as e:
            print(f"上传发布包时出错: {e}", file=sys.stderr)
    
    print("\n✅ 发布完成！")
    return 0

if __name__ == "__main__":
    sys.exit(main())
