#!/usr/bin/env python3
"""更新GitHub Release
"""
import urllib.request
import urllib.error
import json
import os
from pathlib import Path

# 配置
REPO_OWNER = "1525745393"
REPO_NAME = "syno-videoinfo-plugin-AI"
TAG_NAME = "v1.4.5"
RELEASE_NAME = "v1.4.5 - 源管理系统增强版"
RELEASE_BODY = """## Syno VideoInfo Plugin v1.4.5

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

# 从git remote获取token
import subprocess
try:
    git_url = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], 
                                     text=True).strip()
    if 'x-access-token:' in git_url:
        token = git_url.split('x-access-token:')[1].split('@')[0]
        print(f"✓ 已获取GitHub token")
    else:
        print("✗ 无法从git remote获取token")
        exit(1)
except Exception as e:
    print(f"✗ 获取token失败: {e}")
    exit(1)

def make_request(url, method='GET', data=None, headers=None):
    """发送HTTP请求
    """
    req_headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    if headers:
        req_headers.update(headers)
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req_headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=json_data, headers=req_headers, method=method)
    else:
        req = urllib.request.Request(url, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode('utf-8'))
    except Exception as e:
        return 0, {'error': str(e)}

# 检查是否已有Release
print("\n检查现有Release...")
api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG_NAME}"
status, result = make_request(api_url)

release_id = None
upload_url = None

if status == 200:
    print(f"✓ Release已存在")
    release_id = result['id']
    upload_url = result['upload_url'].split('{')[0]
    print(f"  Release ID: {release_id}")
    
    # 删除现有资产（如果有）
    print("\n删除现有资产...")
    for asset in result.get('assets', []):
        print(f"  删除: {asset['name']}")
        delete_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/assets/{asset['id']}"
        delete_status, delete_result = make_request(delete_url, method='DELETE')
        if delete_status == 204:
            print(f"    ✓ 删除成功")
        else:
            print(f"    ⚠ 删除失败: {delete_status}")
    
    # 更新Release描述
    print("\n更新Release描述...")
    update_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}"
    update_data = {
        'name': RELEASE_NAME,
        'body': RELEASE_BODY,
    }
    update_status, update_result = make_request(update_url, method='PATCH', data=update_data)
    if update_status in (200, 201):
        print(f"✓ Release描述已更新")
    else:
        print(f"⚠ 更新描述失败: {update_status}")
else:
    print(f"创建新Release...")
    create_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    create_data = {
        'tag_name': TAG_NAME,
        'name': RELEASE_NAME,
        'body': RELEASE_BODY,
        'draft': False,
        'prerelease': False,
    }
    status, result = make_request(create_url, method='POST', data=create_data)
    
    if status in (200, 201):
        print(f"✓ Release创建成功")
        release_id = result['id']
        upload_url = result['upload_url'].split('{')[0]
        print(f"  URL: {result['html_url']}")
    else:
        print(f"✗ 创建Release失败: {status}")
        print(f"  {result}")
        exit(1)

# 上传发布包
zip_path = Path("dist/syno-videoinfo-plugin-1.4.5.zip")
if zip_path.exists():
    print(f"\n上传发布包: {zip_path.name}")
    try:
        with open(zip_path, 'rb') as f:
            file_data = f.read()
        
        upload_req = urllib.request.Request(
            f"{upload_url}?name={zip_path.name}",
            data=file_data,
            headers={
                'Authorization': f'token {token}',
                'Content-Type': 'application/zip',
            },
            method='POST'
        )
        
        with urllib.request.urlopen(upload_req) as resp:
            if resp.status in (200, 201):
                print(f"✓ 发布包上传成功!")
                print(f"\n✅ 发布完成!")
                print(f"访问: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{TAG_NAME}")
            else:
                print(f"✗ 上传失败: {resp.status}")
    except urllib.error.HTTPError as e:
        print(f"✗ 上传失败: {e.code}")
        print(f"  {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"✗ 上传出错: {e}")
else:
    print(f"\n✗ 未找到发布包: {zip_path}")
