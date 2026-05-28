# 配置指南

本指南介绍如何配置 Syno VideoInfo 插件，包括配置文件、环境变量、日志和性能调优。

## 目录

- [快速开始](#快速开始)
- [配置文件](#配置文件)
- [环境变量](#环境变量)
- [配置选项详解](#配置选项详解)
- [日志配置](#日志配置)
- [性能调优](#性能调优)
- [刮削源优先级](#刮削源优先级)
- [高级配置](#高级配置)

## 快速开始

### 1. 创建默认配置

```bash
make setup-config
```

这会创建以下文件：
- `config.json` - 主配置文件
- `.env` - 环境变量文件

### 2. 基本配置

编辑 `config.json` 中的主要配置：

```json
{
  "scraper": {
    "timeout": 30,
    "max_retries": 3,
    "log_level": "INFO",
    "default_language": "chs"
  }
}
```

### 3. 验证配置

```bash
make validate
```

## 配置文件

### config.json

主配置文件，支持完整的自定义设置。位置优先级：
1. 项目根目录的 `config.json`
2. 用户目录 `~/.syno-videoinfo/config.json`
3. `scraper/` 目录的 `config.json`

### config.example.json

示例配置文件，包含所有可用选项和说明，作为参考使用。

### .env

环境变量配置文件，主要用于覆盖特定配置项。

## 环境变量

### 基本配置

```bash
# 超时设置（秒）
SCRAPER_TIMEOUT=30

# 最大重试次数
SCRAPER_MAX_RETRIES=3

# 重试延迟（秒）
SCRAPER_RETRY_DELAY=1.0

# 最大并发数
SCRAPER_MAX_CONCURRENT=5

# 启用 DNS over HTTPS
SCRAPER_DOH_ENABLED=false

# 默认语言
SCRAPER_DEFAULT_LANGUAGE=chs
```

### 缓存配置

```bash
# 启用缓存
SCRAPER_CACHE_ENABLED=true

# 缓存 TTL（秒）
SCRAPER_CACHE_TTL=3600

# 缓存目录
SCRAPER_CACHE_DIR=.cache
```

### 日志配置

```bash
# 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
SCRAPER_LOG_LEVEL=INFO

# 日志文件路径
SCRAPER_LOG_FILE=scraper.log
```

### 质量配置

```bash
# 最低成功率
SCRAPER_MIN_SUCCESS_RATE=0.5

# 最低完整度
SCRAPER_MIN_COMPLETENESS=0.6

# 禁用的刮削源（逗号分隔）
SCRAPER_DISABLED_SOURCES=
```

## 配置选项详解

### scraper 配置

```json
{
  "scraper": {
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0,
    "max_concurrent": 5,
    "doh_enabled": false,
    "default_language": "chs",
    "scrape_timeout": 60,
    "max_results": 5,
    "cache_enabled": true,
    "cache_ttl": 3600,
    "cache_dir": ".cache",
    "log_level": "INFO",
    "log_file": "scraper.log",
    "min_success_rate": 0.5,
    "min_completeness": 0.6,
    "source_priorities": {
      "javdb_movie": 100,
      "javbus_movie": 90
    },
    "disabled_sources": []
  }
}
```

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `timeout` | int | 30 | 单个请求的超时时间（秒） |
| `max_retries` | int | 3 | 最大重试次数 |
| `retry_delay` | float | 1.0 | 重试间隔（秒） |
| `max_concurrent` | int | 5 | 最大并发请求数 |
| `doh_enabled` | bool | false | 是否启用 DNS over HTTPS |
| `default_language` | string | "chs" | 默认语言 |
| `scrape_timeout` | int | 60 | 刮削总超时时间（秒） |
| `max_results` | int | 5 | 最多返回结果数 |
| `cache_enabled` | bool | true | 是否启用缓存 |
| `cache_ttl` | int | 3600 | 缓存存活时间（秒） |
| `cache_dir` | string | ".cache" | 缓存目录路径 |
| `log_level` | string | "INFO" | 日志级别 |
| `log_file` | string\|null | null | 日志文件路径 |
| `min_success_rate` | float | 0.5 | 最小成功率（0-1） |
| `min_completeness` | float | 0.6 | 最小完整度（0-1） |
| `source_priorities` | object | {} | 刮削源优先级 |
| `disabled_sources` | array | [] | 禁用的刮削源列表 |

### logging 配置

```json
{
  "logging": {
    "version": 1,
    "disable_existing_loggers": false,
    "formatters": {
      "default": {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
      },
      "detailed": {
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
      }
    },
    "handlers": {
      "console": {
        "class": "logging.StreamHandler",
        "formatter": "default",
        "level": "INFO"
      },
      "file": {
        "class": "logging.FileHandler",
        "formatter": "detailed",
        "level": "DEBUG",
        "filename": "scraper.log",
        "encoding": "utf-8"
      }
    },
    "root": {
      "level": "INFO",
      "handlers": ["console"]
    }
  }
}
```

### quality 配置

```json
{
  "quality": {
    "field_weights": {
      "title": 20,
      "number": 15,
      "actors": 15,
      "studio": 10,
      "release": 10,
      "runtime": 5,
      "tags": 5,
      "outline": 5
    },
    "min_quality_score": 60.0,
    "required_fields": ["title", "number"],
    "important_fields": ["actors", "studio", "release"]
  }
}
```

### ranking 配置

```json
{
  "ranking": {
    "success_weight": 0.4,
    "speed_weight": 0.2,
    "quality_weight": 0.3,
    "stability_weight": 0.1,
    "time_window_hours": 24
  }
}
```

## 日志配置

### 日志级别

- `DEBUG` - 详细的调试信息
- `INFO` - 一般信息（默认）
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误

### 日志格式化

可用的占位符：

| 占位符 | 说明 |
|--------|------|
| `%(asctime)s` | 时间戳 |
| `%(name)s` | 日志记录器名称 |
| `%(levelname)s` | 日志级别 |
| `%(message)s` | 日志消息 |
| `%(module)s` | 模块名称 |
| `%(lineno)d` | 行号 |
| `%(funcName)s` | 函数名称 |

### 控制台彩色日志

在终端中运行时，日志会自动使用彩色输出：
- 绿色: INFO
- 青色: DEBUG
- 黄色: WARNING
- 红色: ERROR
- 紫色: CRITICAL

### 文件日志

启用文件日志记录：

```json
{
  "scraper": {
    "log_file": "scraper.log"
  }
}
```

或使用 logging 配置：

```json
{
  "logging": {
    "handlers": {
      "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "formatter": "detailed",
        "level": "DEBUG",
        "filename": "scraper.log",
        "maxBytes": 10485760,
        "backupCount": 5,
        "encoding": "utf-8"
      }
    },
    "root": {
      "level": "DEBUG",
      "handlers": ["console", "file"]
    }
  }
}
```

## 性能调优

### 并发设置

```json
{
  "scraper": {
    "max_concurrent": 10,
    "timeout": 60
  }
}
```

- 网络较慢时，增加 `timeout` 和 `max_concurrent`
- 网络较快时，减少 `max_concurrent` 避免资源浪费

### 缓存优化

```json
{
  "scraper": {
    "cache_enabled": true,
    "cache_ttl": 86400,
    "cache_dir": "/tmp/videoinfo-cache"
  }
}
```

- 对于频繁请求，增加 `cache_ttl`（最长可到 86400 即 24 小时）
- 使用 SSD 上的目录作为 `cache_dir`

### performance 配置

```json
{
  "performance": {
    "enable_async": true,
    "enable_connection_pool": true,
    "pool_maxsize": 20,
    "pool_maxconnect": 100,
    "request_timeout": 30,
    "retry_on_connection_error": true,
    "backoff_factor": 0.5,
    "backoff_max": 10.0
  }
}
```

| 配置项 | 说明 |
|--------|------|
| `enable_async` | 启用异步请求 |
| `enable_connection_pool` | 启用连接池 |
| `pool_maxsize` | 连接池大小 |
| `pool_maxconnect` | 最大连接数 |
| `request_timeout` | 单个请求超时 |
| `retry_on_connection_error` | 连接错误自动重试 |
| `backoff_factor` | 退避因子 |
| `backoff_max` | 最大退避时间 |

## 刮削源优先级

### 设置优先级

```json
{
  "scraper": {
    "source_priorities": {
      "javdb_movie": 100,
      "javbus_movie": 90,
      "dmm_movie": 80,
      "missav_movie": 70,
      "theporndb_movie": 60
    }
  }
}
```

数值越高，优先级越高。

### 禁用刮削源

```json
{
  "scraper": {
    "disabled_sources": [
      "javlibrary_movie",
      "jav321_movie"
    ]
  }
}
```

或使用环境变量：

```bash
SCRAPER_DISABLED_SOURCES=javlibrary_movie,jav321_movie
```

## 高级配置

### 网络配置

```json
{
  "advanced": {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "custom_headers": {},
    "proxy": "http://127.0.0.1:8080",
    "verify_ssl": true,
    "enable_cache": true,
    "cache_max_size": 1000
  }
}
```

### 使用代理

```json
{
  "advanced": {
    "proxy": "http://proxy.example.com:8080"
  }
}
```

或使用环境变量：

```bash
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

### 自定义 User-Agent

```json
{
  "advanced": {
    "user_agent": "My Custom User Agent 1.0"
  }
}
```

### 禁用 SSL 验证（仅用于开发！）

```json
{
  "advanced": {
    "verify_ssl": false
  }
}
```

## 在代码中使用配置

### 基本使用

```python
from scraper.config import get_config

config = get_config()

# 获取配置值
timeout = config.get('scraper.timeout', 30)

# 设置配置值
config.set('scraper.log_level', 'DEBUG')
```

### 获取刮削器配置对象

```python
from scraper.config import get_config

config = get_config()
scraper_config = config.get_scraper_config()

print(f"Timeout: {scraper_config.timeout}")
print(f"Log Level: {scraper_config.log_level}")
```

### 保存配置

```python
config.save('config.json')
```

## 配置验证

使用 Makefile 验证配置：

```bash
make validate
```

检查所有刮削源配置是否有效。

## 故障排除

### 配置不生效？

1. 检查配置文件位置
2. 检查环境变量是否冲突
3. 重启相关程序

### 日志文件没有输出？

1. 检查 `log_file` 配置
2. 检查文件权限
3. 查看控制台输出

### 性能问题？

1. 启用缓存
2. 调整 `max_concurrent`
3. 检查网络连接
4. 查看性能报告

## 相关文档

- [质量提升指南](./QUALITY_IMPROVEMENT.md)
- [刮削源开发](./SCRAPEFLOWS.md)
- [测试指南](./TESTING_GUIDE.md)
- [故障排除](./TROUBLESHOOTING.md)
