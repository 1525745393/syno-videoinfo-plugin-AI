#!/bin/bash
# GitHub Release创建脚本

REPO_OWNER="1525745393"
REPO_NAME="syno-videoinfo-plugin-AI"
TAG_NAME="v1.4.5"
RELEASE_NAME="v1.4.5 - 源管理系统增强版"
RELEASE_BODY="## Syno VideoInfo Plugin v1.4.5

### ✨ 主要更新

- 🎯 **完整的源管理系统** - 健康监控、智能排序、优先级管理
- 🎨 **现代化Web界面** - 源管理仪表盘、实时状态监控
- 📊 **73+ 刮削源** - 覆盖各类影视元数据
- 🔧 **配置管理系统** - 灵活的配置选项
- 📈 **性能监控** - 实时统计和健康检查
- 🧪 **完整测试套件** - 44个单元和集成测试

### 📦 安装

1. 下载下方的 \`syno-videoinfo-plugin-1.4.5.zip\`
2. 打开群晖 **Video Station** → **设置** → **视频信息插件**
3. 点击 **[新增]**，选择下载的 zip 文件

### 🚀 功能特性

- 零依赖，纯 Python 实现
- 73+ 刮削源（电影、电视剧、动漫、成人内容等）
- Web 配置界面（访问 \`http://<NAS_IP>:5125\`）
- 源管理界面（访问 \`http://<NAS_IP>:5125/sourcemgmt\`）
- 智能排序和健康监控
- 完整的测试和文档
"

# 从git remote URL提取token
GIT_URL=$(git remote get-url origin)
if [[ "$GIT_URL" == *"x-access-token:"* ]]; then
    TOKEN=$(echo "$GIT_URL" | grep -oP '(?<=x-access-token:)[^@]+')
    echo "已从git remote获取token"
else
    echo "未找到token"
    exit 1
fi

# 检查Release是否已存在
echo "检查Release是否已存在..."
RELEASE_RESPONSE=$(curl -s -w "%{http_code}" -o release_info.json \
    -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/tags/$TAG_NAME")

HTTP_CODE=$(tail -n1 <<<"$RELEASE_RESPONSE")

if [ "$HTTP_CODE" == "200" ]; then
    echo "Release $TAG_NAME 已存在"
    RELEASE_ID=$(cat release_info.json | grep -oP '"id":\s*\K\d+')
    UPLOAD_URL=$(cat release_info.json | grep -oP '"upload_url":\s*"\K[^"]+' | cut -d'{' -f1)
    echo "Release ID: $RELEASE_ID"
else
    echo "创建新的Release..."
    # 创建Release
    RELEASE_DATA=$(jq -n \
        --arg tag "$TAG_NAME" \
        --arg name "$RELEASE_NAME" \
        --arg body "$RELEASE_BODY" \
        '{
            tag_name: $tag,
            name: $name,
            body: $body,
            draft: false,
            prerelease: false
        }')
    
    CREATE_RESPONSE=$(curl -s -w "%{http_code}" -o release_info.json \
        -X POST \
        -H "Authorization: token $TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json" \
        -d "$RELEASE_DATA" \
        "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases")
    
    CREATE_HTTP_CODE=$(tail -n1 <<<"$CREATE_RESPONSE")
    
    if [ "$CREATE_HTTP_CODE" != "200" ] && [ "$CREATE_HTTP_CODE" != "201" ]; then
        echo "创建Release失败: $CREATE_HTTP_CODE"
        cat release_info.json
        exit 1
    fi
    
    RELEASE_ID=$(cat release_info.json | grep -oP '"id":\s*\K\d+')
    UPLOAD_URL=$(cat release_info.json | grep -oP '"upload_url":\s*"\K[^"]+' | cut -d'{' -f1)
    echo "Release创建成功！"
    echo "Release ID: $RELEASE_ID"
    echo "Upload URL: $UPLOAD_URL"
fi

# 上传发布包
if [ -f "dist/syno-videoinfo-plugin-1.4.5.zip" ]; then
    echo "上传发布包..."
    UPLOAD_RESPONSE=$(curl -s -w "%{http_code}" -o upload_response.json \
        -X POST \
        -H "Authorization: token $TOKEN" \
        -H "Content-Type: application/zip" \
        --data-binary "@dist/syno-videoinfo-plugin-1.4.5.zip" \
        "$UPLOAD_URL?name=syno-videoinfo-plugin-1.4.5.zip")
    
    UPLOAD_HTTP_CODE=$(tail -n1 <<<"$UPLOAD_RESPONSE")
    
    if [ "$UPLOAD_HTTP_CODE" == "200" ] || [ "$UPLOAD_HTTP_CODE" == "201" ]; then
        echo "✓ 发布包上传成功！"
    else
        echo "上传失败: $UPLOAD_HTTP_CODE"
        cat upload_response.json
    fi
else
    echo "未找到发布包: dist/syno-videoinfo-plugin-1.4.5.zip"
fi

# 清理
rm -f release_info.json upload_response.json

echo ""
echo "✅ 发布完成！"
echo "访问: https://github.com/$REPO_OWNER/$REPO_NAME/releases/tag/$TAG_NAME"
