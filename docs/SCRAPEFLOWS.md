# 刮削源开发指南

本文档介绍如何为 Syno VideoInfo Plugin 创建新的刮削源。

## 目录

- [刮削源配置格式](#刮削源配置格式)
- [数据提取语法](#数据提取语法)
- [函数说明](#函数说明)
- [完整示例](#完整示例)
- [常见问题](#常见问题)

## 刮削源配置格式

一个刮削源配置是一个 JSON 文件，包含以下结构：

```json
{
  "type": "movie",
  "site": "example.com",
  "doh_enabled": true,
  "lang": ["chs", "cht", "en"],
  "config": {
    "apikey": {
      "icon": "key",
      "name": "API Key"
    }
  },
  "steps": [
    {
      "http": { /* HTTP 请求 */ },
      "collect": { /* 数据收集 */ },
      "loop": { /* 循环处理 */ },
      "retval": { /* 返回结果 */ }
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | string | ✅ | 类型，可为 "movie"、"tvshow"、"tvshow_episode" |
| `site` | string | ✅ | 站点标识名称 |
| `doh_enabled` | boolean | ❌ | 是否启用 DNS over HTTPS，默认 false |
| `lang` | array | ❌ | 支持的语言列表 |
| `config` | object | ❌ | 用户可配置的选项 |
| `steps` | array | ✅ | 刮削流程步骤 |

## 数据提取语法

### 1. XPath 提取

```json
["xp_text", "XPath表达式"]           // 提取单个文本
["xp_texts", "XPath表达式"]          // 提取多个文本
["xp_attr_src", "XPath表达式"]       // 提取 src 属性
["xp_attr_href", "XPath表达式"]      // 提取 href 属性
["xp_attr_content", "XPath表达式"]   // 提取 content 属性
["xp_elem", "XPath表达式"]           // 提取元素
```

### 2. 正则表达式提取

```json
["re_match", "正则表达式"]            // 提取第一个匹配
["re_matches", "正则表达式"]          // 提取所有匹配
```

### 3. JSON 路径提取

```json
["get", "字段名"]                     // 从字典获取字段
["get", "路径/到/字段"]              // 多级路径
```

### 4. 数据修改器

```json
// 前缀
["xp_text", "./path", "prefix", "https://example.com"]

// 类型转换
["xp_text", "./path", "int"]         // 转整数
["xp_text", "./path", "float"]       // 转浮点数

// 字符串处理
["xp_text", "./path", "split", ","]  // 分割字符串
["xp_text", "./path", "re_sub", "pattern", "replacement"]  // 正则替换
["xp_text", "./path", "reformat", "%Y%m%d", "%Y-%m-%d"]    // 日期格式化
```

## 函数说明

### `doh` - DNS over HTTPS

配置 DNS 服务器：

```json
{
  "doh": {
    "host": "api.example.com"
  }
}
```

### `http` - HTTP 请求

发送 HTTP 请求：

```json
{
  "http": {
    "url": "https://example.com/search?q={title}",
    "method": "GET",
    "headers": {
      "User-Agent": "Mozilla/5.0 ...",
      "Cookie": "{cookie}"
    },
    "params": { "key": "value" },
    "body": { "data": "value" },
    "timeout": 15,
    "result": "search_result"
  }
}
```

参数说明：
- `url` - 请求地址
- `method` - HTTP 方法 (GET/POST)
- `headers` - 请求头
- `params` - URL 参数
- `body` - 请求体
- `timeout` - 超时时间（秒）
- `result` - 结果存储的键名

### `collect` - 数据收集

从 HTTP 响应中提取数据：

```json
{
  "collect": {
    "source": "search_result",
    "into": {
      "title": ["xp_text", "//h1"],
      "ids": ["re_matches", "id=(\\d+)"]
    }
  }
}
```

### `loop` - 循环处理

遍历列表处理：

```json
{
  "loop": {
    "source": "ids",
    "item": "id",
    "iferr": "continue",
    "steps": [
      {
        "http": { "url": "https://example.com/detail/{id}" }
      },
      {
        "retval": { "source": "movie" }
      }
    ]
  }
}
```

### `retval` - 返回结果

返回刮削结果或条件判断：

```json
// 返回结果
{
  "retval": {
    "source": "movie"
  }
}

// 条件判断
{
  "retval": {
    "ifempty": "apikey"
  }
}
```

## 可用的上下文变量

| 变量 | 说明 |
|------|------|
| `{title}` | 视频标题 |
| `{year}` | 发行年份 |
| `{season}` | 季数（电视剧） |
| `{episode}` | 集数（电视剧） |
| `{lang}` | 语言 |
| `{limit}` | 结果数量限制 |
| `{apikey}` | 配置的 API Key（用户配置） |
| `{cookie}` | 配置的 Cookie（用户配置） |
| `{$parent[变量名]}` | 父级上下文变量 |

## 输出结果格式

刮削结果应包含以下字段：

```json
{
  "title": "标题",
  "original_available": "2023-01-01",
  "summary": "简介",
  "runtime": 120,
  "genre": ["类型1", "类型2"],
  "actor": ["演员1", "演员2"],
  "director": ["导演1"],
  "writer": ["编剧1"],
  "tagline": "标语",
  "certificate": "分级",
  "extra": {
    "plugin-id": {
      "poster": "海报 URL",
      "backdrop": "背景图 URL",
      "rating": 8.5,
      "reference": {
        "site-name": "id"
      }
    }
  }
}
```

## 完整示例

### 示例 1: 简单的 API 刮削源

```json
{
  "type": "movie",
  "site": "api.example.com",
  "doh_enabled": false,
  "steps": [
    {
      "http": {
        "url": "https://api.example.com/search?q={title}",
        "method": "GET",
        "headers": {
          "Accept": "application/json"
        },
        "result": "search"
      }
    },
    {
      "collect": {
        "source": "search",
        "into": {
          "movie_ids": ["get", "results"]
        }
      }
    },
    {
      "loop": {
        "source": "movie_ids",
        "item": "movie",
        "steps": [
          {
            "collect": {
              "source": "movie",
              "into": {
                "result": {
                  "title": ["get", "title"],
                  "original_available": ["get", "release_date"],
                  "summary": ["get", "overview"],
                  "genre": ["get", "genres"],
                  "extra": {
                    "[plugin_id]": {
                      "poster": ["get", "poster_path"],
                      "rating": ["get", "vote_average"]
                    }
                  }
                }
              }
            }
          },
          {
            "retval": {
              "source": "result"
            }
          }
        ]
      }
    }
  ]
}
```

### 示例 2: 需要 Cookie 的网站

```json
{
  "type": "movie",
  "site": "protected-site.com",
  "doh_enabled": true,
  "lang": ["chs", "en"],
  "config": {
    "cookie": {
      "icon": "key",
      "name": "Cookie"
    }
  },
  "steps": [
    {
      "http": {
        "url": "https://protected-site.com/search/{title}",
        "method": "GET",
        "headers": {
          "User-Agent": "Mozilla/5.0 ...",
          "Cookie": "{cookie}"
        },
        "timeout": 15,
        "result": "search_result"
      }
    },
    {
      "collect": {
        "source": "search_result",
        "into": {
          "urls": ["re_matches", "/movie/([a-z0-9]+)"]
        }
      }
    },
    {
      "loop": {
        "source": "urls",
        "item": "url",
        "iferr": "continue",
        "steps": [
          {
            "http": {
              "url": "https://protected-site.com{url}",
              "headers": {
                "Cookie": "{cookie}"
              },
              "result": "detail"
            }
          },
          {
            "collect": {
              "source": "detail",
              "into": {
                "movie": {
                  "title": ["xp_text", "//h1[@class='title']"],
                  "original_available": ["re_match", "发布时间：(\\d{4}-\\d{2}-\\d{2})"],
                  "summary": ["xp_text", "//div[@class='desc']"],
                  "genre": ["xp_texts", "//div[@class='tags']/a"],
                  "extra": {
                    "[plugin_id]": {
                      "poster": ["xp_attr_src", "//img[@class='poster']/@src"]
                    }
                  }
                }
              }
            }
          },
          {
            "retval": {
              "source": "movie"
            }
          }
        ]
      }
    }
  ]
}
```

## 测试刮削源

创建完刮削源后，使用以下命令测试：

```bash
# 语法验证
python scripts/validate_flows.py

# 实际测试
python main.py --type movie --input "{\"title\":\"测试电影\"}" --limit 1 --loglevel debug
```

## 常见问题

### Q: 如何处理动态加载的内容？
A: 当前项目不支持 JavaScript 渲染的内容，仅支持静态 HTML 或 API 响应。

### Q: 如何处理分页？
A: 可以在 `loop` 步骤中增加页码变量，多次请求。

### Q: 如何调试刮削源？
A: 使用 `--loglevel debug` 参数，可以查看详细的请求和响应。

### Q: 刮削源应该放在哪里？
A: 放在 `scrapeflows/` 目录下，文件名格式为 `sitename_type.json`。

### Q: 如何设置刮削源优先级？
A: 在配置页面（http://NAS_IP:5125）中设置刮削源优先级。

## 参考资源

- 查看现有刮削源示例：`scrapeflows/` 目录
- 项目主页：https://github.com/C5H12O5/syno-videoinfo-plugin
- Video Station 文档：https://kb.synology.com/en-id/DSM/help/VideoStation/metadata
