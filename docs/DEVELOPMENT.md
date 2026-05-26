# 开发指南

欢迎为 Syno VideoInfo Plugin 做出贡献！本文档介绍如何开发和测试这个项目。

## 目录

- [环境设置](#环境设置)
- [项目结构](#项目结构)
- [开发流程](#开发流程)
- [调试技巧](#调试技巧)
- [打包发布](#打包发布)

## 环境设置

### 前置条件

- Python 3.6 或更高版本
- Git
- 文本编辑器或 IDE（推荐 VSCode）

### 克隆项目

```bash
git clone https://github.com/C5H12O5/syno-videoinfo-plugin.git
cd syno-videoinfo-plugin
```

### 安装依赖

本项目不需要外部 Python 依赖，只需要标准库。

## 项目结构

```
syno-videoinfo-plugin/
├── main.py                   # 插件主入口
├── setup.py                  # 打包脚本
├── version.py                # 版本管理
├── run.sh                    # 启动脚本
├── scraper/                  # 刮削核心模块
│   ├── __init__.py
│   ├── scraper.py            # 主要刮削逻辑
│   ├── enums.py              # 枚举定义
│   ├── exceptions.py         # 异常类
│   ├── fake.py               # 模拟数据
│   ├── utils.py              # 工具函数
│   └── functions/            # 刮削函数
│       ├── __init__.py
│       ├── request.py        # HTTP 请求
│       ├── collect.py        # 数据收集
│       ├── loop.py           # 循环处理
│       ├── retval.py         # 返回结果
│       └── doh.py            # DNS over HTTPS
├── scrapeflows/              # 刮削源配置
│   └── *.json                # 各个网站的配置
├── configserver/             # 配置服务器
│   ├── __init__.py
│   ├── server.py             # HTTP 服务器
│   └── templates/            # HTML 模板
├── scripts/                  # 开发脚本
│   └── validate_flows.py     # 刮削源验证
└── docs/                     # 文档
```

## 开发流程

### 1. 创建功能分支

```bash
git checkout -b feature/my-new-feature
```

### 2. 开发新功能

#### 创建新刮削源

在 `scrapeflows/` 目录下创建新的 JSON 配置文件：

```bash
touch scrapeflows/mynewsite_movie.json
```

参考 [SCRAPEFLOWS.md](SCRAPEFLOWS.md) 了解配置格式。

#### 修改核心代码

如果需要修改核心功能，请编辑 `scraper/` 目录下的文件。

### 3. 测试修改

#### 测试刮削功能

```bash
python main.py --type movie --input "{\"title\":\"电影名\"}" --limit 1 --loglevel debug
```

#### 验证刮削源

```bash
python scripts/validate_flows.py
```

#### 测试安装

```bash
python main.py --type movie --input "{\"title\":\"--install\"}" --limit 1
```

#### 测试配置服务器

```bash
python configserver/server.py
```

然后在浏览器打开 http://localhost:5125

## 调试技巧

### 启用调试日志

```bash
python main.py --type movie --input "{\"title\":\"测试\"}" --limit 1 --loglevel debug
```

调试级别：
- `debug` - 最详细的日志
- `info` - 一般信息
- `warning` - 警告
- `error` - 错误
- `critical` - 严重错误（默认）

### 使用断点调试

在代码中插入调试语句：

```python
import logging
logging.debug("变量值: %s", some_variable)
```

### 查看 HTTP 请求

在 `request.py` 中添加日志：

```python
# 可临时修改查看详细请求/响应
print("请求 URL:", url)
print("响应状态:", response.status)
print("响应内容:", content[:500])  # 只打印前500字符
```

## 代码风格

### 遵循现有风格

- 使用 4 空格缩进
- 遵循 PEP 8 规范
- 添加文档字符串

### 检查代码

可以使用以下工具检查代码：

```bash
# 检查 PEP 8 合规性
pip install flake8
flake8 .

# 格式化代码
pip install black
black .
```

## 提交代码

### 提交前检查

- ✅ 测试刮削功能正常
- ✅ 运行刮削源验证
- ✅ 更新相关文档

### 提交信息格式

```
<类型>: <简短描述>

<详细描述>

Closes #<issue号>（如果有关联）
```

类型可选值：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

## 打包发布

### 创建版本标签

```bash
git tag v1.4.5
git push --tags
```

### 打包插件

```bash
python setup.py sdist --formats=zip
```

打包后的文件在 `dist/` 目录。

## 常见问题

### Q: 如何测试在真实 NAS 上运行？

A: 使用 Virtual DSM 或真实硬件安装打包后的 zip 插件。

### Q: 开发时如何快速测试？

A: 使用 `--loglevel debug` 和缩小 `--limit` 来快速验证。

### Q: 如何处理网站结构变化？

A: 更新对应刮削源的 XPath 或正则表达式，然后重新测试。

### Q: 贡献代码有什么要求？

A: 保持现有代码风格，确保测试通过，更新相关文档。

## 更多资源

- [Syno VideoInfo Plugin README](../README.md)
- [刮削源配置指南](SCRAPEFLOWS.md)
- [Synology Video Station 文档](https://kb.synology.com/en-id/DSM/help/VideoStation/metadata)
- [Video Station API](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)
