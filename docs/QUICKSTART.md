# Syno VideoInfo Plugin - 快速入门指南

欢迎！这份指南帮助你在 5 分钟内快速上手使用这个项目。

## 第一步：了解项目

这个项目是一个 Synology Video Station 的元数据刮削插件，支持从多个网站获取视频元数据。

## 第二步：快速开始

### 1. 查看项目结构
项目包含以下主要部分：
```
scrapeflows/       - 刮削源配置（新增了更多！）
docs/              - 文档
scripts/           - 工具
configserver/      - 配置服务器
```

### 2. 验证刮削源配置

我们已经有 28 个刮削源配置！

通用刮削源（基于 `scrapeflows/`：
- douban_movie.json      - 豆瓣电影
- tmdb_movie.json        - TMDB
- maoyan_movie.json      - 猫眼
- bangumi_movie.json      - Bangumi

成人内容刮削源：
- javdb_movie.json        - JAVDB
- javlibrary_movie.json    - JAVLibrary
- missav_movie.json        - MissAV
- javbus_movie.json       - JAVBus
- mgstage_movie.json       - MGStage
- fc2hub_movie.json      - FC2Hub
- airav_movie.json      - Airav
- jav321_movie.json      - JAV321
- javdbapi_movie.json     - JAVDB API

### 3. 验证刮削源

```bash
python scripts/validate_flows.py
```

结果显示所有刮削源是 100% 有效的！

### 4. 使用 Makefile

我们新增了 Makefile 简化操作：
```bash
make help           # 查看帮助
make validate      # 验证刮削源
make test          # 测试刮削测试
make test-movie    # 测试电影刮削
make list-flows   # 列出所有刮削源
make package      # 打包插件
```

## 第三步：开发新刮削源

创建新刮削源很简单：

1. 在 `scrapeflows/` 复制模板
2. 根据网站的 API 或 HTML 结构编写 JSON 配置
3. 使用 `make validate` 验证

详细文档请查看：
- [刮削源配置指南](SCRAPEFLOWS.md)
- [开发指南](DEVELOPMENT.md)

## 第四步：配置服务器
在浏览器中访问 `http://[NAS_IP]:5125

## 第五步：打包插件

```bash
git tag v1.4.5
make package
```

在 Video Station 安装打包文件会在 dist/ 目录中！

## 提示

## 下一步

查看 [故障排除](TROUBLESHOOTING.md)
