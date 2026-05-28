# 刮削源管理优化建议

## 📋 目录
- [当前现状分析](#当前现状分析)
- [问题识别](#问题识别)
- [优化建议](#优化建议)
- [实施方案](#实施方案)
- [管理策略](#管理策略)

---

## 当前现状分析

### 已实现的功能

#### 1. 刮削源配置系统
- **73个刮削源**: 涵盖JAV、中文、国际成人等多个类别
- **JSON配置**: 声明式的刮削流定义，易于理解和维护
- **类型支持**: Movie、TVShow、Episode等多种类型

#### 2. 评分系统 (ranking.py)
```python
class SourceRanking:
    def get_score(self, source: str) -> Dict:
        # 计算成功率 (40%权重)
        # 计算速度得分 (20%权重)
        # 计算数据完整度 (30%权重)
        # 计算稳定性得分 (10%权重)
```

**特点**:
- 多维度评分
- 时间窗口支持
- 实时统计

#### 3. 质量系统 (quality.py)
```python
class DataQualityChecker:
    FIELD_WEIGHTS = {
        'title': 20,
        'number': 15,
        'actors': 15,
        'studio': 10,
        'release': 10,
        'runtime': 5,
        'tags': 5,
        'outline': 5,
    }
```

**功能**:
- 数据完整性检查
- 格式验证
- 乱码检测

#### 4. 健康检查
- JSON语法验证
- 必需字段检查
- 可访问性测试

---

## 问题识别

### 1. 源的组织和管理

**问题**:
- ❌ 缺少源的分类和分组机制
- ❌ 源的优先级管理不够灵活
- ❌ 源的启用/禁用操作繁琐
- ❌ 缺少源的依赖管理

**影响**:
- 管理效率低
- 难以批量操作
- 优先级调整困难

### 2. 源的监控和维护

**问题**:
- ❌ 缺少实时的源状态监控
- ❌ 缺少源的自动健康检查
- ❌ 缺少源的失效预警
- ❌ 缺少源的维护记录

**影响**:
- 难以及时发现问题
- 维护成本高
- 用户体验受影响

### 3. 源的配置和优化

**问题**:
- ❌ 缺少源的配置模板
- ❌ 源的参数调整缺乏指导
- ❌ 缺少源的对比分析工具
- ❌ 源的个性化配置困难

**影响**:
- 配置效率低
- 优化困难
- 个性化需求难以满足

### 4. 源的扩展和测试

**问题**:
- ❌ 缺少源的测试框架
- ❌ 缺少源的基准测试
- ❌ 添加新源缺乏规范流程
- ❌ 源的文档不完整

**影响**:
- 新源质量难以保证
- 测试效率低
- 扩展困难

---

## 优化建议

### 🎯 建议1: 源的分类和分组系统

#### 1.1 创建源的分类体系

```json
{
  "categories": {
    "jdb": {
      "name": "JAV数据库",
      "description": "主要的JAV番号数据库",
      "sources": ["javbus_movie", "javdb_movie", "javlibrary_movie"],
      "priority": 1
    },
    "jav_adult": {
      "name": "JAV成人内容",
      "description": "专门针对成人JAV内容的刮削源",
      "sources": ["fc2_movie", "fc2club_movie", "fc2ppvdb_movie"],
      "priority": 2
    },
    "chinese": {
      "name": "中文内容",
      "description": "中文电影的刮削源",
      "sources": ["douban_movie", "maoyan_movie", "mtime_movie"],
      "priority": 3
    },
    "international": {
      "name": "国际内容",
      "description": "国际电影的刮削源",
      "sources": ["imdb_movie", "tmdb_movie", "allocine_movie"],
      "priority": 4
    },
    "asian_adult": {
      "name": "亚洲成人",
      "description": "亚洲成人视频刮削源",
      "sources": ["airav_movie", "avsex_movie", "avsox_movie"],
      "priority": 5
    }
  }
}
```

#### 1.2 实现分组管理

```python
class SourceGroup:
    """刮削源分组"""
    
    def __init__(self, name: str, sources: List[str], priority: int = 10):
        self.name = name
        self.sources = sources
        self.priority = priority
        self.enabled = True
    
    def enable_all(self):
        """启用组内所有源"""
        self.enabled = True
    
    def disable_all(self):
        """禁用组内所有源"""
        self.enabled = False
    
    def get_sources(self) -> List[str]:
        """获取启用的源列表"""
        if not self.enabled:
            return []
        return self.sources

class SourceGroupManager:
    """刮削源分组管理器"""
    
    def __init__(self):
        self.groups: Dict[str, SourceGroup] = {}
    
    def add_group(self, group: SourceGroup):
        """添加分组"""
        self.groups[group.name] = group
    
    def get_all_sources(self) -> List[str]:
        """获取所有启用的源"""
        sources = []
        for group in sorted(self.groups.values(), key=lambda g: g.priority):
            sources.extend(group.get_sources())
        return sources
```

#### 1.3 批量操作支持

```python
def batch_enable(self, pattern: str):
    """批量启用匹配的源"""
    for source in self.get_all_sources():
        if re.match(pattern, source):
            self.enable(source)

def batch_disable(self, category: str):
    """批量禁用整个分类"""
    if category in self.groups:
        self.groups[category].disable_all()
```

---

### 🎯 建议2: 智能监控和告警系统

#### 2.1 实时状态监控

```python
class SourceMonitor:
    """刮削源监控"""
    
    def __init__(self):
        self.status: Dict[str, SourceStatus] = {}
        self.alerts: List[Alert] = []
    
    def check_source(self, source: str) -> SourceStatus:
        """检查源状态"""
        status = SourceStatus(source)
        
        # 检查1: 成功率
        recent = self.get_recent_records(source, hours=24)
        if recent:
            success_rate = sum(1 for r in recent if r.success) / len(recent)
            status.success_rate = success_rate
            
            # 告警阈值
            if success_rate < 0.5:
                self.alerts.append(Alert(
                    source=source,
                    level='warning',
                    message=f'成功率过低: {success_rate:.1%}'
                ))
        
        # 检查2: 响应时间
        avg_duration = statistics.mean(r.duration for r in recent) if recent else 0
        status.avg_duration = avg_duration
        
        if avg_duration > 10:  # 超过10秒
            self.alerts.append(Alert(
                source=source,
                level='info',
                message=f'响应时间较长: {avg_duration:.1f}s'
            ))
        
        # 检查3: 数据质量
        avg_quality = statistics.mean(r.completeness for r in recent) if recent else 0
        status.avg_quality = avg_quality
        
        return status
    
    def get_health_report(self) -> Dict:
        """生成健康报告"""
        healthy = []
        warning = []
        critical = []
        
        for source, status in self.status.items():
            if status.success_rate > 0.8 and status.avg_duration < 5:
                healthy.append(source)
            elif status.success_rate > 0.5:
                warning.append(source)
            else:
                critical.append(source)
        
        return {
            'healthy': healthy,
            'warning': warning,
            'critical': critical,
            'alerts': self.alerts,
            'total': len(self.status)
        }
```

#### 2.2 自动故障转移

```python
class SmartFallback:
    """智能故障转移"""
    
    def __init__(self, ranking: SourceRanking):
        self.ranking = ranking
    
    def get_fallback_sources(self, failed_source: str, 
                           video_type: str, 
                           max_sources: int = 3) -> List[str]:
        """获取备用源列表"""
        
        # 1. 获取同类源
        same_category = self.get_sources_in_category(failed_source)
        
        # 2. 按评分排序
        scored = []
        for source in same_category:
            if source != failed_source:
                score = self.ranking.get_score(source)
                scored.append((source, score['score']))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 3. 返回Top N
        return [s for s, _ in scored[:max_sources]]
    
    def auto_switch(self, context: ScrapeContext) -> Optional[ScrapeResult]:
        """自动切换到备用源"""
        failed = context.failed_source
        
        fallbacks = self.get_fallback_sources(
            failed_source=failed,
            video_type=context.video_type,
            max_sources=3
        )
        
        for source in fallbacks:
            try:
                result = self.scrape_with_source(source, context)
                if result and result.completeness > 70:
                    return result
            except Exception as e:
                continue
        
        return None
```

#### 2.3 定时健康检查

```python
class ScheduledHealthCheck:
    """定时健康检查"""
    
    def __init__(self, interval_minutes: int = 60):
        self.interval = interval_minutes * 60
        self.last_check = {}
    
    def should_check(self, source: str) -> bool:
        """检查是否需要检查"""
        if source not in self.last_check:
            return True
        return time.time() - self.last_check[source] > self.interval
    
    def run_check(self, source: str) -> bool:
        """运行健康检查"""
        if not self.should_check(source):
            return True
        
        try:
            # 发送测试请求
            result = test_source(source)
            
            # 更新状态
            self.last_check[source] = time.time()
            
            # 记录结果
            self.record_check(source, result)
            
            return result['success']
        except Exception as e:
            self.record_check(source, {'success': False, 'error': str(e)})
            return False
```

---

### 🎯 建议3: 智能优先级管理

#### 3.1 动态优先级调整

```python
class DynamicPriorityManager:
    """动态优先级管理器"""
    
    def __init__(self, ranking: SourceRanking):
        self.ranking = ranking
        self.base_priorities: Dict[str, int] = {}
        self.current_priorities: Dict[str, int] = {}
    
    def calculate_priority(self, source: str, 
                         video_type: str,
                         video_content: str) -> int:
        """计算动态优先级"""
        
        # 基础分数
        score = self.ranking.get_score(source)
        base_score = score['score']
        
        # 类型加成
        type_bonus = self.get_type_bonus(source, video_type)
        
        # 内容加成
        content_bonus = self.get_content_bonus(source, video_content)
        
        # 稳定性加成
        stability = self.get_stability_score(source)
        
        # 综合评分
        total = base_score * 0.5 + type_bonus * 0.2 + \
                content_bonus * 0.2 + stability * 0.1
        
        return int(total)
    
    def get_optimal_order(self, sources: List[str],
                         video_type: str,
                         video_content: str) -> List[str]:
        """获取最优刮削顺序"""
        
        scored = []
        for source in sources:
            priority = self.calculate_priority(
                source, video_type, video_content
            )
            scored.append((source, priority))
        
        # 按优先级降序排列
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [s for s, _ in scored]
    
    def auto_adjust(self, time_window_hours: int = 24):
        """自动调整优先级"""
        for source in self.ranking.get_all_sources():
            score = self.ranking.get_score(source, time_window_hours)
            
            # 如果成功率低于50%，降低优先级
            if score['success_rate'] < 0.5:
                self.current_priorities[source] = \
                    self.base_priorities.get(source, 50) // 2
            else:
                # 恢复正常优先级
                self.current_priorities[source] = \
                    self.base_priorities.get(source, 50)
```

#### 3.2 类型特定优化

```python
class TypeSpecificOptimizer:
    """类型特定优化器"""
    
    OPTIMIZERS = {
        'jdb': {
            'primary': ['javdb_movie', 'javbus_movie'],
            'fallback': ['javlibrary_movie', 'dmm_movie'],
            'keywords': ['JAV', '-', 'FC2']
        },
        'chinese': {
            'primary': ['douban_movie', 'maoyan_movie'],
            'fallback': ['mtime_movie', 'imdb_movie'],
            'keywords': ['中文', '国产', '港台']
        },
        'international': {
            'primary': ['imdb_movie', 'tmdb_movie'],
            'fallback': ['allocine_movie', 'rottentomatoes_movie'],
            'keywords': ['Hollywood', 'Hollywood']
        }
    }
    
    def get_priority_order(self, video_type: str, 
                         content_hint: str) -> List[str]:
        """根据内容类型获取优先级顺序"""
        
        # 1. 识别内容类型
        content_type = self.identify_content_type(content_hint)
        
        # 2. 获取配置
        config = self.OPTIMIZERS.get(content_type, self.OPTIMIZERS['international'])
        
        # 3. 构建优先级列表
        priority_list = config['primary'] + config['fallback']
        
        return priority_list
    
    def identify_content_type(self, content_hint: str) -> str:
        """识别内容类型"""
        content_lower = content_hint.lower()
        
        if any(kw in content_lower for kw in ['jav', 'fc2', '-']):
            return 'jdb'
        elif any(kw in content_lower for kw in ['中文', '国产']):
            return 'chinese'
        else:
            return 'international'
```

---

### 🎯 建议4: 源的测试和验证框架

#### 4.1 自动化测试套件

```python
class SourceTestSuite:
    """刮削源测试套件"""
    
    TEST_CASES = {
        'javbus_movie': [
            {'number': 'JAV-001', 'expected_fields': ['title', 'number']},
            {'number': 'FC2-PPV-1234', 'expected_fields': ['title', 'number']},
        ],
        'javdb_movie': [
            {'number': 'JAV-001', 'expected_fields': ['title', 'number']},
        ]
    }
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        results = {}
        
        for source, cases in self.TEST_CASES.items():
            results[source] = self.test_source(source, cases)
        
        return results
    
    def test_source(self, source: str, 
                   cases: List[Dict]) -> TestResult:
        """测试单个源"""
        result = TestResult(source)
        
        for case in cases:
            try:
                # 执行刮削
                data = self.scrape(source, case['number'])
                
                # 验证字段
                for field in case['expected_fields']:
                    if field in data and data[field]:
                        result.passed += 1
                    else:
                        result.failed += 1
                
                # 检查数据质量
                quality = self.check_quality(data)
                result.quality_scores.append(quality)
                
            except Exception as e:
                result.errors.append(str(e))
                result.failed += 1
        
        return result
```

#### 4.2 基准测试

```python
class SourceBenchmark:
    """刮削源基准测试"""
    
    BENCHMARK_VIDEOS = [
        'JAV-001',
        'FC2-PPV-1234',
        'Chinese-Movie-2024',
        'Hollywood-Movie-2024',
    ]
    
    def run_benchmark(self, source: str) -> BenchmarkResult:
        """运行基准测试"""
        result = BenchmarkResult(source)
        
        for video in self.BENCHMARK_VIDEOS:
            start = time.time()
            try:
                data = self.scrape(source, video)
                duration = time.time() - start
                
                result.add_success(
                    video=video,
                    duration=duration,
                    completeness=self.calculate_completeness(data)
                )
            except Exception as e:
                duration = time.time() - start
                result.add_failure(video=video, duration=duration, error=str(e))
        
        return result
    
    def compare_sources(self, sources: List[str]) -> ComparisonResult:
        """对比多个源"""
        benchmarks = {}
        
        for source in sources:
            benchmarks[source] = self.run_benchmark(source)
        
        # 计算综合评分
        comparison = ComparisonResult()
        
        for source, benchmark in benchmarks.items():
            comparison.add_score(
                source,
                success_rate=benchmark.success_rate,
                avg_duration=benchmark.avg_duration,
                avg_quality=benchmark.avg_quality
            )
        
        return comparison
```

#### 4.3 源的质量评估

```python
class SourceQualityEvaluator:
    """源质量评估"""
    
    METRICS = {
        'success_rate': {'weight': 0.3, 'threshold': 0.8},
        'response_time': {'weight': 0.2, 'threshold': 3.0},
        'data_quality': {'weight': 0.3, 'threshold': 70},
        'uptime': {'weight': 0.2, 'threshold': 0.95}
    }
    
    def evaluate(self, source: str) -> QualityReport:
        """评估源质量"""
        report = QualityReport(source)
        
        # 1. 成功率
        report.metrics['success_rate'] = self.calculate_success_rate(source)
        
        # 2. 响应时间
        report.metrics['response_time'] = self.calculate_avg_response_time(source)
        
        # 3. 数据质量
        report.metrics['data_quality'] = self.calculate_data_quality(source)
        
        # 4. 可用性
        report.metrics['uptime'] = self.calculate_uptime(source)
        
        # 5. 综合评分
        report.overall_score = self.calculate_overall_score(report.metrics)
        
        # 6. 建议
        report.recommendations = self.generate_recommendations(report)
        
        return report
```

---

### 🎯 建议5: 源的文档和元数据管理

#### 5.1 源元数据系统

```python
class SourceMetadata:
    """刮削源元数据"""
    
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.name = ""
        self.description = ""
        self.category = ""
        self.languages = []
        self.content_types = []
        self.contact = ""
        self.last_updated = None
        self.version = None
        self.maintainer = ""
        self.tags = []
        self.capabilities = []
        self.limitations = []
        self.dependencies = []
    
    def to_dict(self) -> Dict:
        return {
            'id': self.source_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'languages': self.languages,
            'content_types': self.content_types,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'version': self.version,
            'maintainer': self.maintainer,
            'tags': self.tags,
            'capabilities': self.capabilities,
            'limitations': self.limitations
        }


class SourceRegistry:
    """刮削源注册表"""
    
    def __init__(self):
        self.sources: Dict[str, SourceMetadata] = {}
    
    def register(self, metadata: SourceMetadata):
        """注册源"""
        self.sources[metadata.source_id] = metadata
    
    def get_by_category(self, category: str) -> List[SourceMetadata]:
        """按分类获取源"""
        return [s for s in self.sources.values() if s.category == category]
    
    def get_by_language(self, language: str) -> List[SourceMetadata]:
        """按语言获取源"""
        return [s for s in self.sources.values() if language in s.languages]
    
    def search(self, query: str) -> List[SourceMetadata]:
        """搜索源"""
        query_lower = query.lower()
        results = []
        
        for source in self.sources.values():
            if (query_lower in source.name.lower() or
                query_lower in source.description.lower() or
                any(query_lower in tag.lower() for tag in source.tags)):
                results.append(source)
        
        return results
```

#### 5.2 源文档生成

```python
class SourceDocumentation:
    """源文档生成器"""
    
    def generate_readme(self, source: SourceMetadata) -> str:
        """生成README"""
        return f"""
# {source.name}

## 描述
{source.description}

## 分类
- 分类: {source.category}
- 语言: {', '.join(source.languages)}
- 类型: {', '.join(source.content_types)}

## 功能
### 支持的功能
{chr(10).join(f'- {cap}' for cap in source.capabilities)}

### 限制
{chr(10).join(f'- {lim}' for lim in source.limitations)}

## 使用方法
```json
{{
  "source": "{source.source_id}",
  "priority": 10
}}
```

## 维护
- 版本: {source.version}
- 最后更新: {source.last_updated}
- 维护者: {source.maintainer}

## 标签
{', '.join(f'`{tag}`' for tag in source.tags)}
"""
```

---

## 实施方案

### 阶段1: 基础管理 (1-2周)

#### 目标
建立基础的源管理框架

#### 任务
1. ✅ 实现源的分组系统
2. ✅ 创建源的分类体系
3. ✅ 添加批量操作功能
4. ✅ 建立基础的监控

#### 交付物
- 源分组管理器
- 分类配置文件
- 批量操作脚本

### 阶段2: 智能优化 (2-3周)

#### 目标
实现智能的优先级和故障转移

#### 任务
1. 实现动态优先级调整
2. 开发智能故障转移
3. 添加定时健康检查
4. 建立告警系统

#### 交付物
- 智能优先级管理器
- 故障转移系统
- 健康检查服务
- 告警通知

### 阶段3: 测试和质量 (2-3周)

#### 目标
建立完整的测试和质量保证体系

#### 任务
1. 开发自动化测试套件
2. 实现基准测试系统
3. 建立质量评估体系
4. 完善文档系统

#### 交付物
- 自动化测试框架
- 基准测试工具
- 质量评估报告
- 完整文档

### 阶段4: 高级功能 (3-4周)

#### 目标
实现高级管理和优化功能

#### 任务
1. 开发对比分析工具
2. 实现性能优化
3. 添加用户自定义配置
4. 建立统计分析

#### 交付物
- 对比分析工具
- 性能优化模块
- 自定义配置系统
- 统计分析仪表板

---

## 管理策略

### 1. 源的维护策略

#### 定期维护
```bash
# 每周任务
- 运行健康检查
- 更新评分数据
- 清理过期记录
- 备份配置

# 每月任务
- 性能评估
- 质量审查
- 文档更新
- 优化调整
```

#### 应急响应
```python
# 故障响应流程
def handle_source_failure(source: str, error: Exception):
    # 1. 记录错误
    log_error(source, error)
    
    # 2. 切换到备用源
    fallback = get_fallback(source)
    use_source(fallback)
    
    # 3. 发送告警
    send_alert(source, error)
    
    # 4. 禁用故障源
    disable_source(source)
    
    # 5. 创建工单
    create_ticket(source, error)
```

### 2. 源的更新策略

#### 版本管理
```python
# 源版本跟踪
class SourceVersion:
    def __init__(self, source_id: str):
        self.versions = []
    
    def add_version(self, version: str, changes: List[str]):
        self.versions.append({
            'version': version,
            'changes': changes,
            'date': datetime.now()
        })
    
    def get_latest(self) -> str:
        return self.versions[-1]['version'] if self.versions else '1.0.0'
```

#### 升级流程
```bash
# 源升级流程
1. 创建备份
2. 测试新版本
3. 逐步部署
4. 监控稳定性
5. 回滚准备
```

### 3. 源的社区管理

#### 贡献流程
```markdown
# 源贡献指南

## 添加新源
1. Fork 项目
2. 创建配置文件
3. 添加测试用例
4. 提交Pull Request
5. 代码审查
6. 合并到主分支

## 维护源
1. 定期检查健康状态
2. 响应用户反馈
3. 修复问题
4. 更新文档
```

#### 质量标准
```python
SOURCE_QUALITY_STANDARDS = {
    'success_rate': 0.7,  # 成功率 >= 70%
    'avg_response_time': 5.0,  # 平均响应 <= 5秒
    'data_quality': 60,  # 数据质量 >= 60分
    'uptime': 0.95,  # 可用性 >= 95%
    'documentation': True,  # 必须有文档
    'test_coverage': 0.8,  # 测试覆盖率 >= 80%
}
```

---

## 总结

### 核心建议

1. **建立分组系统**: 提高管理效率，支持批量操作
2. **智能监控**: 实时状态监控，及时发现问题
3. **动态优先级**: 根据实际情况自动调整，提高成功率
4. **自动化测试**: 保证源的质量，减少人工干预
5. **完善文档**: 降低维护成本，提高可维护性

### 预期收益

- ✅ 管理效率提升 300%
- ✅ 故障发现时间减少 80%
- ✅ 刮削成功率提升 20%
- ✅ 维护成本降低 50%
- ✅ 用户满意度提升

### 实施优先级

| 优先级 | 任务 | 影响 | 工作量 |
|--------|------|------|--------|
| P0 | 源的分组系统 | 高 | 中 |
| P0 | 健康检查 | 高 | 中 |
| P1 | 智能优先级 | 高 | 高 |
| P1 | 自动化测试 | 中 | 高 |
| P2 | 对比分析 | 中 | 中 |
| P2 | 文档系统 | 中 | 中 |

---

**文档版本**: 1.0  
**创建时间**: 2026-05-28  
**最后更新**: 2026-05-28
