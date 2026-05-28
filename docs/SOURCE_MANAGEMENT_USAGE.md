# 刮削源管理系统使用指南

## 📋 概述

刮削源管理系统是一个完整的解决方案，提供源的分组管理、健康监控、智能优先级、自动故障转移、自动化测试和质量评估功能。

## 🎯 快速开始

### 1. 初始化系统

```python
from scraper.source_management import init_sms

# 初始化源管理系统
sms = init_sms('source_groups.json')
```

### 2. 获取最优源

```python
# 获取最优刮削源
optimal_sources = sms.get_optimal_sources(
    video_type='movie',
    content_hint='JAV-001',
    limit=5
)
print(f"最优源: {optimal_sources}")
```

### 3. 记录刮取结果

```python
# 记录刮取结果
sms.record_scrape(
    source='javbus_movie',
    success=True,
    duration=1.5,
    data={'title': 'Test Movie', 'number': 'JAV-001'}
)
```

### 4. 获取备用源

```python
# 获取备用源
fallbacks = sms.get_fallback_sources('javbus_movie', max_sources=3)
print(f"备用源: {fallbacks}")
```

### 5. 查看健康报告

```python
# 获取健康报告
report = sms.get_health_report()
print(f"健康源: {len(report['healthy'])}")
print(f"警告: {len(report['warning'])}")
print(f"错误: {len(report['error'])}")
```

---

## 📚 核心功能

### 1. 源分组管理

#### 加载和管理分组

```python
from scraper.source_manager import init_source_manager

# 初始化
manager = init_source_manager('source_groups.json')

# 获取统计
stats = manager.get_statistics()
print(f"总源数: {stats['total_sources']}")
print(f"总分类数: {stats['total_categories']}")

# 按分类获取源
jav_sources = manager.get_sources_by_category('jav_database')
print(f"JAV数据库源: {jav_sources}")

# 启用/禁用分类
manager.enable_category('jav_database')
manager.disable_category('asian_adult')
```

#### 搜索源

```python
# 搜索源
results = manager.search_sources('jav')
print(f"搜索结果: {results}")
```

#### 获取备用源

```python
# 获取备用源
fallbacks = manager.get_fallback_sources('javbus_movie')
print(f"备用源: {fallbacks}")
```

### 2. 健康监控

#### 基本监控

```python
from scraper.monitor import init_monitor

# 初始化监控器
monitor = init_monitor()

# 记录请求
monitor.record_request('javbus_movie', True, 1.2, 85.0)
monitor.record_request('javbus_movie', True, 1.5, 90.0)
monitor.record_request('javdb_movie', False, 2.0, 0.0)

# 获取源状态
status = monitor.get_status('javbus_movie')
print(f"状态: {status.status}")
print(f"成功率: {status.success_rate:.1%}")
print(f"平均响应时间: {status.avg_duration:.2f}s")
```

#### 健康报告

```python
# 获取健康报告
report = monitor.get_health_report()
print(f"健康源: {report['healthy']}")
print(f"警告源: {report['warning']}")
print(f"错误源: {report['error']}")
print(f"告警: {report['alerts']}")
```

#### 告警处理器

```python
def custom_alert_handler(alert):
    print(f"[{alert.level}] {alert.source}: {alert.message}")
    # 发送邮件、Slack通知等

monitor.add_alert_handler(custom_alert_handler)
```

### 3. 动态优先级

#### 基本优先级

```python
from scraper.priority_manager import init_priority_manager, PriorityConfig

# 自定义配置
config = PriorityConfig(
    base_priority=50,
    min_priority=10,
    max_priority=100,
    success_rate_weight=0.4,
    response_time_weight=0.2,
    data_quality_weight=0.3,
    stability_weight=0.1
)

# 初始化
pm = init_priority_manager(config)

# 设置基础优先级
pm.set_base_priority('javbus_movie', 90)
pm.set_base_priority('javdb_movie', 85)

# 获取优先级
priority = pm.get_priority('javbus_movie')
print(f"javbus_movie 优先级: {priority}")
```

#### 动态调整

```python
# 调整优先级
old_priority, new_priority = pm.adjust_priority(
    source='javbus_movie',
    success_rate=0.95,
    avg_duration=1.0,
    data_quality=85.0,
    stability=0.9
)
print(f"优先级调整: {old_priority} -> {new_priority}")

# 自动调整所有源
adjusted = pm.auto_adjust_all(stats)
for source, old, new in adjusted:
    print(f"{source}: {old} -> {new}")
```

#### 类型优化

```python
from scraper.priority_manager import get_type_optimizer

# 获取类型优化器
optimizer = get_type_optimizer()

# 识别内容类型
content_type = optimizer.identify_content_type('JAV-001')
print(f"内容类型: {content_type}")  # 输出: jav

# 获取优化的优先级顺序
optimized = optimizer.get_priority_order(
    sources=['javbus_movie', 'javdb_movie', 'douban_movie'],
    content_hint='JAV-001'
)
print(f"优化顺序: {optimized}")
```

### 4. 智能故障转移

```python
from scraper.monitor import SmartFallback

# 创建故障转移器
fallback = SmartFallback(monitor)

# 获取备用源
source_groups = {
    'jav_database': ['javbus_movie', 'javdb_movie', 'javlibrary_movie'],
    'dmm': ['dmm_movie', 'mgstage_movie']
}

fallbacks = fallback.get_fallback_sources(
    failed_source='javbus_movie',
    source_groups=source_groups,
    max_sources=3
)
print(f"备用源: {fallbacks}")

# 判断是否应该切换
should_switch = fallback.should_fallback('javbus_movie')
print(f"应该切换: {should_switch}")
```

### 5. 自动化测试

#### 基本测试

```python
from scraper.test_suite import get_test_suite
import asyncio

# 获取测试套件
suite = get_test_suite()

# 添加自定义测试用例
from scraper.test_suite import TestCase
suite.add_test_case(TestCase(
    number='JAV-999',
    name='特殊测试',
    expected_fields=['title', 'number', 'release']
))

# 定义刮削函数（示例）
async def mock_scrape(source, number):
    await asyncio.sleep(0.1)
    return {
        'title': f'Test {number}',
        'number': number,
        'release': '2024-01-01'
    }

# 测试单个源
results = asyncio.run(suite.test_source('javbus_movie', mock_scrape))
for result in results:
    print(f"{result.test_case.number}: {'✅' if result.success else '❌'}")
```

#### 基准测试

```python
from scraper.test_suite import get_benchmark

# 获取基准测试器
benchmark = get_benchmark()

# 基准测试
result = asyncio.run(benchmark.benchmark_source('javbus_movie', mock_scrape))
print(f"成功率: {result.success_rate:.1%}")
print(f"平均时间: {result.avg_duration:.2f}s")
print(f"平均质量: {result.avg_completeness:.1f}")

# 对比源
sources = ['javbus_movie', 'javdb_movie']
comparison = benchmark.compare_sources(sources)
print(f"最佳源: {comparison['ranking']['overall'][0]['source']}")
```

### 6. 质量评估

```python
from scraper.test_suite import get_evaluator

# 获取评估器
evaluator = get_evaluator()

# 评估源
quality_report = evaluator.evaluate_source(
    source='javbus_movie',
    benchmark_result=benchmark_result,
    monitor_data={'javbus_movie': {'uptime': 0.98}}
)

print(f"评分: {quality_report['overall_score']:.1f}")
print(f"等级: {quality_report['grade']}")
print(f"建议: {quality_report['recommendations']}")

# 获取最佳源
top_sources = evaluator.get_top_sources(count=5)
print(f"Top 5 源: {top_sources}")
```

---

## 💡 使用示例

### 示例1: 完整的刮取流程

```python
from scraper.source_management import init_sms

# 初始化
sms = init_sms('source_groups.json')

async def scrape_video(video_number: str):
    """刮取视频元数据"""
    
    # 1. 获取最优源
    optimal_sources = sms.get_optimal_sources(
        video_type='movie',
        content_hint=video_number,
        limit=5
    )
    
    # 2. 尝试刮取
    for source in optimal_sources:
        try:
            start_time = time.time()
            data = await scrape_from_source(source, video_number)
            duration = time.time() - start_time
            
            # 3. 记录结果
            sms.record_scrape(source, True, duration, data)
            
            return data
        except Exception as e:
            # 记录失败
            sms.record_scrape(source, False, 0, None)
            continue
    
    # 3. 所有源都失败，尝试备用源
    fallbacks = sms.get_fallback_sources(optimal_sources[0])
    for source in fallbacks:
        try:
            data = await scrape_from_source(source, video_number)
            sms.record_scrape(source, True, 0, data)
            return data
        except:
            sms.record_scrape(source, False, 0, None)
            continue
    
    return None
```

### 示例2: 定期健康检查

```python
import asyncio
from scraper.monitor import ScheduledHealthCheck

# 创建定时检查
health_check = ScheduledHealthCheck(monitor, interval_minutes=60)

async def check_source_health(source):
    """检查源健康状态"""
    try:
        result = await test_source(source)
        return result['success']
    except:
        return False

# 运行定期检查
async def run_health_checks():
    sources = sms.get_all_sources()
    await health_check.check_all(sources, check_source_health)

# 启动后台任务
# asyncio.create_task(run_health_checks())
```

### 示例3: 批量测试和质量评估

```python
async def batch_test_and_evaluate():
    """批量测试和评估"""
    
    sources = ['javbus_movie', 'javdb_movie', 'javlibrary_movie']
    
    # 1. 基准测试
    benchmark_results = await benchmark.benchmark_all(sources, mock_scrape)
    
    # 2. 质量评估
    for source in sources:
        quality_report = evaluator.evaluate_source(
            source, 
            benchmark_results[source],
            None
        )
        
        print(f"\n{source}:")
        print(f"  评分: {quality_report['overall_score']:.1f}")
        print(f"  等级: {quality_report['grade']}")
        
        if quality_report['recommendations']:
            print(f"  建议: {quality_report['recommendations']}")
    
    # 3. 获取Top源
    top_sources = evaluator.get_top_sources()
    print(f"\n最佳源: {top_sources}")
```

---

## 🔧 配置

### 源分组配置

编辑 `source_groups.json`:

```json
{
  "categories": {
    "jav_database": {
      "name": "JAV数据库",
      "priority": 1,
      "enabled": true,
      "sources": ["javbus_movie", "javdb_movie"],
      "tags": ["jav", "database"]
    }
  },
  "fallback_rules": {
    "jav_database": {
      "fallback_to": ["dmm"],
      "auto_switch": true
    }
  },
  "health_check": {
    "enabled": true,
    "interval_minutes": 60,
    "alert_threshold": {
      "success_rate": 0.5,
      "response_time": 10
    }
  }
}
```

### 优先级配置

```python
config = PriorityConfig(
    base_priority=50,           # 基础优先级
    min_priority=10,            # 最小优先级
    max_priority=100,          # 最大优先级
    adjustment_interval=3600,   # 调整间隔（秒）
    
    # 权重配置
    success_rate_weight=0.4,   # 成功率权重
    response_time_weight=0.2,   # 响应时间权重
    data_quality_weight=0.3,   # 数据质量权重
    stability_weight=0.1,      # 稳定性权重
    
    # 阈值配置
    success_rate_threshold=0.8,
    response_time_threshold=3.0,
    data_quality_threshold=70.0
)
```

---

## 📊 统计和报告

### 获取统计

```python
# 获取完整统计
stats = sms.get_statistics()

print(f"源统计: {stats['source_manager']}")
print(f"健康报告: {stats['health']}")
print(f"优先级调整次数: {stats['priority_changes']}")
```

### 导出配置

```python
# 导出配置
sms.export_configuration('source_config.json')

# 导入配置
sms.import_configuration('source_config.json')
```

---

## 🚀 性能优化

### 1. 缓存优先级结果

```python
# 优先级会被缓存，减少重复计算
priority = pm.get_priority('javbus_movie')  # 第一次计算
priority = pm.get_priority('javbus_movie')  # 使用缓存
```

### 2. 批量记录结果

```python
# 批量记录减少开销
for source, result in scrape_results:
    sms.record_scrape(source, result.success, result.duration, result.data)
```

### 3. 异步操作

```python
# 所有IO操作都是异步的
results = await asyncio.gather(
    test_source('javbus_movie', scrape_func),
    test_source('javdb_movie', scrape_func),
    test_source('javlibrary_movie', scrape_func)
)
```

---

## 🐛 故障排除

### 问题1: 源状态显示为unknown

**原因**: 源还没有足够的测试数据

**解决**: 运行多次测试或基准测试

```python
# 运行基准测试
result = await benchmark.benchmark_source('javbus_movie', scrape_func)
```

### 问题2: 优先级调整无效

**原因**: 调整间隔未到

**解决**: 手动调整

```python
# 手动调整优先级
pm.current_priorities['javbus_movie'] = 100
```

### 问题3: 备用源为空

**原因**: 源分组配置不完整

**解决**: 检查 `source_groups.json`

---

## 📝 API 参考

### SourceManagementSystem

| 方法 | 说明 |
|------|------|
| `initialize()` | 初始化系统 |
| `record_scrape()` | 记录刮取结果 |
| `get_optimal_sources()` | 获取最优源 |
| `get_fallback_sources()` | 获取备用源 |
| `get_health_report()` | 获取健康报告 |
| `get_source_status()` | 获取源状态 |
| `get_source_score()` | 获取源评分 |
| `adjust_priorities()` | 调整优先级 |
| `get_statistics()` | 获取统计 |

### SourceMonitor

| 方法 | 说明 |
|------|------|
| `record_request()` | 记录请求 |
| `get_status()` | 获取状态 |
| `get_health_report()` | 获取健康报告 |
| `get_healthy_sources()` | 获取健康源 |
| `get_best_sources()` | 获取最佳源 |

### DynamicPriorityManager

| 方法 | 说明 |
|------|------|
| `set_base_priority()` | 设置基础优先级 |
| `get_priority()` | 获取优先级 |
| `adjust_priority()` | 调整优先级 |
| `get_priority_order()` | 获取优先级顺序 |
| `auto_adjust_all()` | 自动调整所有 |

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**文档版本**: 1.0  
**最后更新**: 2026-05-28
