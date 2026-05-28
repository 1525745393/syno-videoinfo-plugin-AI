# 刮削源管理系统 - 完整实现文档

## 概述

刮削源管理系统是一个完整的、功能强大的源管理解决方案，提供源分组、健康监控、动态优先级、自动故障转移、持久化存储和自动化测试功能。

## 功能特性

### ✅ 核心功能

1. **源分组管理** - 将刮削源按类别组织管理
2. **实时健康监控** - 跟踪源状态、成功率、响应时间
3. **智能故障转移** - 自动检测失败源并切换到备用源
4. **动态优先级** - 基于性能自动调整源优先级
5. **数据持久化** - 保存源状态和历史记录
6. **自动化测试** - 内置测试框架和基准测试

### ✅ 已实现模块

| 模块 | 文件 | 功能 |
|------|------|------|
| 源管理器 | `scraper/source_manager.py` | 源分组和分类管理 |
| 监控器 | `scraper/monitor.py` | 实时状态监控和告警 |
| 优先级管理器 | `scraper/priority_manager.py` | 动态优先级计算和调整 |
| 测试套件 | `scraper/test_suite.py` | 自动化测试和基准测试 |
| 持久化存储 | `scraper/persistence.py` | 数据持久化和历史记录 |
| 统一接口 | `scraper/source_management.py` | 整合所有功能的API |
| CLI工具 | `scripts/source_manager.py` | 命令行管理工具 |

## 快速开始

### 基本使用

```python
from scraper.source_management import init_sms

# 初始化源管理系统
sms = init_sms('source_groups.json')

# 获取最优源
optimal_sources = sms.get_optimal_sources(
    video_type='movie',
    content_hint='jav',
    limit=5
)

# 记录刮削结果
sms.record_scrape(
    source='javbus_movie',
    success=True,
    duration=1.2,
    data={'number': 'JAV-123', 'title': 'Test Video'}
)

# 获取健康状态
health_report = sms.get_health_report()

# 保存数据
sms.save()
```

### 命令行工具

```bash
# 列出所有源
python scripts/source_manager.py list

# 搜索源
python scripts/source_manager.py search jav

# 查看健康状态
python scripts/source_manager.py status

# 查看特定源状态
python scripts/source_manager.py status --source javbus_movie

# 启用源
python scripts/source_manager.py enable javbus_movie

# 禁用源
python scripts/source_manager.py disable bad_source

# 重置源数据
python scripts/source_manager.py reset javbus_movie

# 查看刮削历史
python scripts/source_manager.py history

# 查看统计信息
python scripts/source_manager.py stats

# 保存数据
python scripts/source_manager.py save
```

## 配置

### 源分组配置 (`source_groups.json`)

```json
{
    "categories": {
        "jav_database": {
            "name": "JAV数据库",
            "priority": 1,
            "enabled": true,
            "sources": ["javbus_movie", "javdb_movie", "javlibrary_movie"],
            "tags": ["jav", "database"]
        },
        "chinese": {
            "name": "中文电影",
            "priority": 2,
            "enabled": true,
            "sources": ["douban_movie", "maoyan_movie"],
            "tags": ["chinese", "movie"]
        }
    }
}
```

### 持久化存储位置

默认情况下，数据保存在 `source_data/` 目录：
- `source_states.json` - 源状态数据
- `history.json` - 刮削历史记录
- `settings.json` - 系统设置

## API文档

### SourceManagementSystem

主要接口类，提供所有源管理功能。

```python
# 初始化
sms = init_sms('source_groups.json')

# 记录刮取
sms.record_scrape(source, success, duration, data)

# 获取最优源
sources = sms.get_optimal_sources(video_type, content_hint, limit)

# 获取健康报告
report = sms.get_health_report()

# 调整优先级
sms.adjust_priorities()

# 保存数据
sms.save()
```

### PersistentStorage

持久化存储层。

```python
from scraper.persistence import init_storage

storage = init_storage()

# 记录刮取
storage.record_scrape(source, success, duration, quality, number, title)

# 获取状态
state = storage.get_state(source)

# 获取历史
history = storage.get_history(source=None, limit=100)

# 获取统计
stats = storage.get_statistics(source=None, hours=24)

# 保存
storage.save()
```

### 源分组管理

```python
from scraper.source_manager import init_source_manager

manager = init_source_manager('source_groups.json')

# 获取所有源
sources = manager.get_all_sources()

# 获取特定分类的源
jav_sources = manager.get_sources_by_category('jav_database')

# 获取源所属分类
category = manager.get_category_by_source('javbus_movie')

# 搜索源
results = manager.search_sources('jav')

# 启用/禁用分类
manager.enable_category('jav_database')
manager.disable_category('chinese')
```

### 健康监控

```python
from scraper.monitor import init_monitor

monitor = init_monitor()

# 记录请求
monitor.record_request('javbus_movie', True, 1.2, 85.0)

# 获取源状态
status = monitor.get_status('javbus_movie')

# 获取健康报告
report = monitor.get_health_report()

# 获取健康源
healthy = monitor.get_healthy_sources()

# 获取最佳源
best = monitor.get_best_sources(count=3)
```

### 优先级管理

```python
from scraper.priority_manager import init_priority_manager

pm = init_priority_manager()

# 设置基础优先级
pm.set_base_priority('javbus_movie', 90)

# 调整优先级
pm.adjust_priority(
    source='javbus_movie',
    success_rate=0.95,
    avg_duration=1.0,
    data_quality=85.0,
    stability=0.9
)

# 获取优先级
priority = pm.get_priority('javbus_movie')

# 获取排序后的源
ordered = pm.get_priority_order(sources_list)
```

## 使用示例

### 示例1: 完整的刮削流程

```python
from scraper.source_management import init_sms

# 初始化
sms = init_sms('source_groups.json')

def scrape_video(number):
    # 获取最优源
    sources = sms.get_optimal_sources('movie', number, limit=3)
    
    for source in sources:
        try:
            # 尝试刮削
            start = time.time()
            data = scrape_from_source(source, number)
            duration = time.time() - start
            
            # 记录成功结果
            sms.record_scrape(source, True, duration, data)
            
            return data
            
        except Exception as e:
            # 记录失败
            sms.record_scrape(source, False, 0, None)
            continue
    
    # 尝试备用源
    if sources:
        fallbacks = sms.get_fallback_sources(sources[0], max_sources=2)
        # ... 尝试备用源
    
    return None

# 刮削视频
result = scrape_video('JAV-123')

# 保存数据
sms.save()
```

### 示例2: 批量测试

```python
import asyncio
from scraper.test_suite import get_test_suite

# 获取测试套件
suite = get_test_suite()

# 添加测试用例
from scraper.test_suite import TestCase
suite.add_test_case(TestCase(
    number='JAV-001',
    name='标准JAV番号',
    expected_fields=['title', 'number', 'release']
))

# 定义刮削函数
async def test_scrape(source, number):
    # 模拟刮削
    await asyncio.sleep(0.5)
    return {'title': f'Test {number}', 'number': number}

# 测试源
results = asyncio.run(suite.test_source('javbus_movie', test_scrape))

# 获取摘要
summary = suite.get_summary('javbus_movie')
print(summary)
```

### 示例3: 健康检查服务

```python
from scraper.monitor import init_monitor, ScheduledHealthCheck

# 初始化
monitor = init_monitor()

# 添加告警处理器
def send_alert(alert):
    print(f'[ALERT] {alert.source}: {alert.message}')

monitor.add_alert_handler(send_alert)

# 创建定时检查
checker = ScheduledHealthCheck(monitor, interval_minutes=30)

# 定期检查源
async def health_check_service():
    sources = ['javbus_movie', 'javdb_movie', 'javlibrary_movie']
    
    while True:
        await checker.check_all(sources, test_source_function)
        await asyncio.sleep(30 * 60)

# 启动服务
asyncio.run(health_check_service())
```

## 扩展功能

### 添加自定义源

要添加新源，请编辑 `source_groups.json`，然后使用API：

```json
{
    "categories": {
        "my_custom_category": {
            "name": "我的自定义分类",
            "priority": 5,
            "enabled": true,
            "sources": ["my_source_1", "my_source_2"],
            "tags": ["custom", "experimental"]
        }
    }
}
```

### 创建新的告警处理器

```python
def email_alert(alert):
    """发送邮件告警"""
    if alert.level in ['error', 'critical']:
        send_email(
            to='admin@example.com',
            subject=f'[ALERT] {alert.source}',
            body=alert.message
        )

# 注册处理器
monitor.add_alert_handler(email_alert)
```

## 故障排除

### 常见问题

1. **数据未保存**
   - 确保调用了 `sms.save()`
   - 检查 `source_data/` 目录权限

2. **源未被正确禁用**
   - 使用 `sms.disable_source(source)` 而非手动编辑文件
   - 检查持久化存储中的状态

3. **历史记录过大**
   - 使用 `storage.clear_old_history(days=30)` 清理旧数据
   - 定期归档历史文件

### 调试

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 检查当前状态
sms = init_sms('source_groups.json')
print(sms.get_statistics())
print(sms.get_health_report())
```

## 下一步

### 待实现功能

1. **Web UI集成** - 在配置服务器中添加源管理界面
2. **真实刮削集成** - 将源管理集成到实际刮削流程中
3. **机器学习优化** - 使用ML算法改进源选择
4. **分布式监控** - 支持多实例监控和同步

### 性能优化建议

1. 定期清理历史数据
2. 批量记录以减少磁盘写入
3. 使用内存缓存优化查询性能

## 总结

刮削源管理系统提供了完整、强大的源管理功能，包括：
- ✅ 源分组和分类
- ✅ 实时健康监控
- ✅ 智能故障转移
- ✅ 动态优先级调整
- ✅ 数据持久化
- ✅ 自动化测试
- ✅ 完整的CLI工具
- ✅ 详细的文档

现在可以立即开始使用！
