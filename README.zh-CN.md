# Synology Video Info Plugin

[![GitHub Release](https://img.shields.io/github/v/release/C5H12O5/syno-videoinfo-plugin?logo=github&style=flat&color=blue)](https://github.com/C5H12O5/syno-videoinfo-plugin/releases)
![GitHub Stars](https://img.shields.io/github/stars/C5H12O5/syno-videoinfo-plugin?logo=github&style=flat&color=yellow)
![GitHub Downloads](https://img.shields.io/github/downloads/C5H12O5/syno-videoinfo-plugin/total?logo=github&style=flat&color=green)
![Python Support](https://img.shields.io/badge/Python-3.6+-green?logo=python&style=flat&color=steelblue)
[![GitHub License](https://img.shields.io/github/license/C5H12O5/syno-videoinfo-plugin?logo=apache&style=flat&color=lightslategray)](LICENSE)

###### 📖 [English](README.md) / 📖 简体中文

一个强大的群晖 **Video Station** 视频元数据插件，支持从多个数据源获取视频信息，远超默认选项。

## ✨ 功能特性

### 🚀 核心功能
- **零依赖**: 纯 Python 实现，无需外部包
- **73+ 刮削源**: 全面覆盖 JAV 数据库、电影网站等
- **简易配置**: 基于 Web 的配置界面，支持实时预览
- **多语言支持**: 适用于各种语言和内容类型

### 📊 高级功能
- **性能监控**: 实时统计和健康跟踪
- **质量评分**: 多维度数据质量评估
- **智能排序**: 基于成功率和速度的源优先级排序
- **配置管理**: 支持 JSON/YAML 配置和环境变量
- **健康检查**: 刮削源的自动验证

### 🎨 用户界面
- **现代化仪表板**: 可视化性能趋势和统计数据
- **深色/浅色主题**: 可自定义外观，支持持久化偏好
- **源管理**: 搜索、筛选和批量操作
- **实时监控**: 所有源的实时状态指示器
- **快捷操作**: 轻松访问常用功能

### 🛠️ 开发者功能
- **可扩展架构**: 易于添加新的刮削源
- **基于 JSON 的配置**: 声明式刮削流程定义
- **全面测试**: 单元、集成和端到端测试
- **详细文档**: 用户和开发者的完整指南

## 📦 支持的数据源

### 电影源 (73+)
- **JAV 数据库**: javbus, javdb, javlibrary, dmm, mgstage, fc2, fc2hub, fc2club, fc2ppvdb
- **中文**: douban, maoyan, mtime, cnmdb, hdouban, guochan, iqqtv, lulubar
- **国际**: imdb, tmdb, allocine, daum, filmweb, watcha, letterboxd
- **成人内容**: airav, avsex, avsox, cableav, freejavbt, getchu, kin8, madouqu, mdtv, mmtv, mywife, prestige, theporndb
- **更多...**

### 电视剧源
- **中文**: douban, maoyan, mtime
- **国际**: tmdb, tvdb
- **动漫**: bangumi, myanimelist

## 🚀 快速开始

### 安装

1. 从 [GitHub Releases](https://github.com/C5H12O5/syno-videoinfo-plugin/releases) 下载最新版本
2. 打开 **Video Station** → **设置** → **视频信息插件**
3. 点击 **[新增]**，选择下载的 `.spk` 文件，然后点击 **[确定]**

### 配置

1. 在浏览器中打开 `http://[NAS_IP]:5125`
2. 自定义刮削源和优先级
3. 点击 **保存** 按钮 (💾)
4. 返回 Video Station - 更改会自动生效！

### 源管理界面

1. 在浏览器中打开 `http://[NAS_IP]:5125/sourcemgmt`
2. 查看所有刮削源的健康状态和性能统计
3. 启用/禁用源、调整优先级、查看历史记录
4. 使用批量操作快速管理多个源

### 基本使用

```bash
# 测试刮削
python main.py --type movie --input '{"title":"JAV-001"}' --limit 1

# 指定日志级别
python main.py --type movie --input '{"title":"FC2-PPV-1234"}' --limit 5 --loglevel debug

# 电视剧刮削
python main.py --type tvshow --input '{"title":"Breaking Bad"}' --limit 3

# 源管理命令
make source-list     # 列出所有源
make source-status   # 查看健康状态
make source-history  # 查看历史记录
```

## 📚 文档

### 用户指南
- [快速入门](docs/QUICKSTART.md) - 快速上手
- [配置指南](docs/CONFIGURATION.md) - 完整配置参考
- [质量提升](docs/QUALITY_IMPROVEMENT.md) - 优化刮削结果
- [故障排除](docs/TROUBLESHOOTING.md) - 常见问题和解决方案
- [源管理指南](docs/SOURCE_MANAGEMENT_USAGE.md) - 源管理系统使用说明

### 开发者指南
- [开发指南](docs/DEVELOPMENT.md) - 设置开发环境
- [ScrapeFlows 指南](docs/SCRAPEFLOWS.md) - 创建新的刮削源
- [测试指南](docs/TESTING_GUIDE.md) - 测试策略和框架
- [项目概览](docs/PROJECT_OVERVIEW.md) - 架构和设计
- [源管理实现](docs/SOURCE_MANAGEMENT_IMPLEMENTATION.md) - 源管理系统实现细节

### UI 增强
- [UI 优化指南](docs/UI_OPTIMIZATION_GUIDE.md) - 功能建议
- [UI 升级指南](docs/UI_UPGRADE_GUIDE.md) - 新界面文档

## 🔧 配置示例

```json
{
  "scraper": {
    "timeout": 30,
    "max_retries": 3,
    "max_concurrent": 5,
    "doh_enabled": true,
    "source_priorities": {
      "javdb_movie": 100,
      "javbus_movie": 90,
      "dmm_movie": 80
    }
  },
  "logging": {
    "level": "INFO",
    "file": "scraper.log"
  },
  "cache": {
    "enabled": true,
    "ttl": 3600
  },
  "quality": {
    "min_completeness": 70,
    "check_garbled": true
  }
}
```

## 📊 仪表板功能

### 统计数据
- **总源数**: 73+ 可用源
- **成功率**: 实时成功率监控
- **平均响应时间**: 性能跟踪
- **数据质量分数**: 质量评估

### 健康监控
- **源状态**: 健康/警告/错误指示器
- **趋势图表**: 可视化性能随时间变化
- **最近活动**: 活动时间线
- **批量操作**: 批量源管理

## 🧪 测试

### 运行所有测试
```bash
make test              # 所有测试
make test-unit        # 仅单元测试
make test-integration # 集成测试
make test-scrapeflows # 刮削流程验证
```

### 健康检查
```bash
make health-check      # 检查源健康
make benchmark         # 性能基准测试
make quality-report    # 生成质量报告
make source-demo       # 源管理演示
```

### 手动测试
```bash
# 测试特定源
python main.py --type movie --input '{"title":"JAV-001"}' \
  --sources javbus_movie,javdb_movie --loglevel debug
```

## 🏗️ 开发

### 设置
```bash
# 克隆仓库
git clone https://github.com/C5H12O5/syno-videoinfo-plugin.git
cd syno-videoinfo-plugin

# 安装开发依赖
pip install pytest black flake8

# 设置配置
make setup-config

# 运行测试
make test
```

### 构建包
```bash
# 清理构建
make clean

# 创建分发
make build

# 验证包
unzip -l dist/*.zip
```

### 添加新源
1. 在 `scrapeflows/` 目录创建 JSON 文件
2. 使用声明式 JSON 语法定义刮削流程
3. 使用 `python scripts/validate_flows.py` 测试
4. 添加到文档的适当类别中

示例刮削流程：
```json
{
  "site": "example_movie",
  "type": "movie",
  "version": 1,
  "steps": [
    {
      "name": "search",
      "request": {
        "method": "GET",
        "url": "https://example.com/search?q={number}"
      }
    }
  ]
}
```

## 🐛 故障排除

### 常见问题

1. **插件无法安装**
   - 检查 DSM 和 Video Station 版本兼容性
   - 验证包完整性

2. **配置页面无法访问**
   - 确保服务正在运行
   - 检查防火墙设置
   - 尝试重启: 设置 → 视频信息插件 → 测试连接

3. **刮削失败**
   - 检查网络连接
   - 验证源未被阻止
   - 如需启用 DNS-over-HTTPS
   - 检查日志查找具体错误

4. **数据质量差**
   - 启用多个源以实现冗余
   - 调整源优先级
   - 使用质量评分识别问题

### 调试模式
```bash
# 启用调试日志
python main.py --loglevel debug --type movie \
  --input '{"title":"TEST"}' --limit 1
```

### 健康检查
```bash
# 运行全面健康检查
make health-check

# 检查特定源
python scripts/validate_flows.py --source javbus_movie
```

## 📈 性能技巧

1. **优先使用快速源**: 将 javdb, javbus, dmm 设为顶部
2. **启用缓存**: 减少冗余请求
3. **使用 DoH**: 绕过 DNS 污染以获得更好的连接
4. **限制并发请求**: 避免速率限制
5. **监控成功率**: 识别并禁用失败的源

## 🤝 贡献

欢迎贡献！请查看我们的指南：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可

本项目采用 Apache 2.0 许可 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- Synology 的 Video Station 平台
- 所有贡献者和支持者
- [mdcx 项目](https://github.com/Hazard804/mdcx) 提供刮削源灵感

## 📞 支持

- **问题**: [GitHub Issues](https://github.com/C5H12O5/syno-videoinfo-plugin/issues)
- **讨论**: [GitHub Discussions](https://github.com/C5H12O5/syno-videoinfo-plugin/discussions)
- **文档**: [Wiki](https://github.com/C5H12O5/syno-videoinfo-plugin/wiki)

## 🔗 参考

- [Video Station 元数据 API](https://kb.synology.com/en-id/DSM/help/VideoStation/metadata)
- [官方 API 文档](https://download.synology.com/download/Document/Software/DeveloperGuide/Package/VideoStation/All/enu/Synology_Video_Station_API_enu.pdf)

## 📋 文件命名约定

**电影:**
```
电影名称 (发行年份).ext
Avatar (2009).avi
```

**电视剧:**
```
电视剧名称.SXX.EYY.ext
Breaking_Bad.S01.E01.mkv
```

## 🔄 版本历史

- **v1.4.5** (当前): 重大更新，包含 73+ 源、现代化 UI、性能监控、源管理系统
- **v1.4.4**: 之前的稳定版本
- **v1.4.3**: 增强配置
- **v1.0.0**: 初始版本

详见 [CHANGELOG.md](CHANGELOG.md) 了解详细版本历史。

---

**❤️ 为群晖 Video Station 用户制作**
