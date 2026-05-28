# 刮削源质量提升指南

本指南介绍如何提升刮削源的质量，包括测试框架、评分系统、质量评估和性能优化。

## 📋 目录

1. [测试框架](#测试框架)
2. [评分系统](#评分系统)
3. [质量评估](#质量评估)
4. [性能优化](#性能优化)
5. [最佳实践](#最佳实践)

## 🧪 测试框架

### 1. 真实刮削测试

使用 `tests/test_real_scrape.py` 进行真实刮削测试：

```python
from tests.test_real_scrape import ScrapeTester, ScrapeTestCase

# 创建测试器
tester = ScrapeTester()

# 定义测试用例
test_case = ScrapeTestCase(
    number="JAV-001",
    expected_fields=['title', 'number'],
    sources=["javbus_movie", "javdb_movie"]
)

# 运行测试
results = await tester.scrape_single(test_case)
```

### 2. 集成测试

使用 `tests/test_integration_advanced.py` 进行端到端测试：

```python
from tests.test_integration_advanced import ScrapeIntegrationTester

tester = ScrapeIntegrationTester()
results = await tester.run_all_tests()

# 生成报告
report = tester.generate_report()
print(report)
```

## ⭐ 评分系统

### 1. 刮削源评分

使用 `scraper/ranking.py` 对刮削源进行评分：

```python
from scraper.ranking import record_scrape, get_source_score, get_recommended_sources

# 记录刮取结果
record_scrape(
    source="javbus_movie",
    number="ABC-123",
    success=True,
    duration=1.5,
    fields={'title': 'Test', 'actors': ['Actor 1']},
    fields_total=10
)

# 获取刮削源评分
score = get_source_score("javbus_movie")
print(f"评分: {score['score']}/100")
print(f"成功率: {score['success_rate']}%")
print(f"平均耗时: {score['avg_duration']}秒")

# 获取推荐刮削源
recommended = get_recommended_sources("ABC-123", count=3)
print(f"推荐: {recommended}")
```

### 2. 评分指标

评分系统基于以下指标：

| 指标 | 权重 | 说明 |
|------|------|------|
| 成功率 | 40% | 成功刮取的比例 |
| 速度 | 20% | 平均响应时间 |
| 完整度 | 30% | 数据字段填充率 |
| 稳定性 | 10% | 失败率 |

### 3. 状态等级

| 状态 | 成功率范围 | 说明 |
|------|----------|------|
| excellent | ≥80% | 优秀 |
| good | 60-80% | 良好 |
| fair | 40-60% | 一般 |
| poor | 20-40% | 较差 |
| critical | <20% | 严重问题 |

## 📊 质量评估

### 1. 数据质量检查

使用 `scraper/quality.py` 检查数据质量：

```python
from scraper.quality import check_quality, check_completeness, generate_quality_report

# 刮取的数据
data = {
    'title': 'Test Movie',
    'number': 'ABC-123',
    'actors': ['Actor 1', 'Actor 2'],
    'studio': 'Test Studio',
    'release': '2024-01-01',
    'runtime': '120',
    'thumb': 'http://example.com/thumb.jpg'
}

# 检查质量
quality_score, errors, warnings = check_quality(data)
print(f"质量总分: {quality_score.overall}/100")

# 检查完整性
completeness = check_completeness(data)
print(f"完整度: {completeness['overall_score']:.1f}%")
print(f"缺失字段: {completeness['missing_fields']}")

# 生成报告
report = generate_quality_report(data)
print(report)
```

### 2. 质量评分详情

| 字段 | 权重 | 说明 |
|------|------|------|
| title | 20 | 标题 |
| number | 15 | 番号 |
| actors | 15 | 演员 |
| studio | 10 | 片商 |
| release | 10 | 发售日期 |
| runtime | 5 | 时长 |
| tags | 5 | 标签 |
| outline | 5 | 简介 |

### 3. 完整性检查

```python
from scraper.quality import DataCompletenessChecker

checker = DataCompletenessChecker()
result = checker.check_completeness(data)

print(f"是否完整: {result['is_complete']}")
print(f"必需字段: {result['required_score']:.0f}%")
print(f"重要字段: {result['important_score']:.0f}%")
```

## ⚡ 性能优化

### 1. 基准测试

使用 `scraper/benchmark.py` 进行性能测试：

```python
from scraper.benchmark import PerformanceBenchmark, generate_benchmark_report
import asyncio

async def run_benchmark():
    benchmark = PerformanceBenchmark()
    
    # 测试刮削源
    sources = ['javbus_movie', 'javdb_movie', 'javlibrary_movie']
    test_numbers = ['ABC-123', 'DEF-456', 'GHI-789']
    
    results = await benchmark.benchmark_all_sources(sources, test_numbers)
    
    # 生成报告
    report = generate_benchmark_report(benchmark)
    print(report)
    
    # 导出结果
    benchmark.export_results('benchmark_results.json')

asyncio.run(run_benchmark())
```

### 2. 性能指标

| 指标 | 说明 |
|------|------|
| success_rate | 成功率 |
| avg_duration | 平均耗时 |
| min_duration | 最短耗时 |
| max_duration | 最长耗时 |
| median_duration | 中位数耗时 |
| std_deviation | 标准差 |

### 3. 性能评分

性能评分基于速度和成功率：

```
性能评分 = 成功率 × 0.6 + 速度得分 × 0.4

速度得分 = max(0, (30 - 平均耗时) / 30 × 100)
```

## 🎯 最佳实践

### 1. 测试驱动开发

```python
# 在添加新的刮削源前，先编写测试
test_case = ScrapeTestCase(
    number="NEW-SOURCE-001",
    expected_fields=['title', 'number', 'actors'],
    sources=["new_source_movie"]
)

# 运行测试验证功能
result = await tester.scrape_single(test_case)
assert result[0].success
```

### 2. 持续监控

```python
# 定期记录刮取结果
record_scrape(source, number, success, duration, fields)

# 检查刮削源健康状态
health = ranking.get_source_health("javbus_movie")
if health['health'] == 'critical':
    # 发送告警
    send_alert("javbus_movie 需要检查")
```

### 3. 智能选择

```python
# 根据番号类型智能选择刮削源
recommended = get_recommended_sources("FC2-PPV-123456", count=3)
# 自动优先选择 FC2 相关刮削源
```

### 4. 质量门槛

```python
# 只接受质量达标的数据
quality_score, errors, warnings = check_quality(data)
completeness = check_completeness(data)

if completeness['overall_score'] < 60:
    # 尝试其他刮削源
    pass
```

## 📈 运行测试

### 运行所有测试

```bash
# 运行单元测试
pytest tests/test_*.py -v

# 运行集成测试
pytest tests/test_integration_advanced.py -v -s

# 运行性能基准测试
python -m scraper.benchmark
```

### 生成测试报告

```bash
# 生成质量报告
python -c "
from scraper.quality import generate_quality_report
from scraper import scraper
# ... 获取数据后生成报告
"
```

## 🔧 配置

### 评分配置

```python
# 自定义评分权重
class SourceRanking:
    def __init__(self):
        self.success_weight = 0.4  # 成功率权重
        self.speed_weight = 0.2      # 速度权重
        self.quality_weight = 0.3    # 质量权重
        self.stability_weight = 0.1  # 稳定性权重
```

### 质量阈值

```python
# 设置质量门槛
MIN_SUCCESS_RATE = 60.0  # 最低成功率
MAX_AVG_DURATION = 30.0  # 最大平均耗时（秒）
MIN_COMPLETENESS = 70.0  # 最低完整度
```

## 📚 更多资源

- [刮削源配置指南](./SCRAPEFLOWS.md)
- [测试框架说明](./TESTING_GUIDE.md)
- [故障排查指南](./TROUBLESHOOTING.md)
