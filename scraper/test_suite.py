"""
刮削源自动化测试套件
提供源的基准测试、质量评估和对比分析功能
"""
import time
import asyncio
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import statistics
import json


@dataclass
class TestCase:
    """测试用例"""
    number: str
    name: str
    content_type: str = 'movie'
    expected_fields: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class TestResult:
    """测试结果"""
    source: str
    test_case: TestCase
    success: bool
    duration: float
    completeness: float = 0.0
    error: Optional[str] = None
    data: Optional[Dict] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    source: str
    total_tests: int = 0
    successful_tests: int = 0
    failed_tests: int = 0
    total_duration: float = 0.0
    avg_duration: float = 0.0
    min_duration: float = 0.0
    max_duration: float = 0.0
    avg_completeness: float = 0.0
    success_rate: float = 0.0
    test_results: List[TestResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def add_result(self, result: TestResult):
        """添加测试结果"""
        self.test_results.append(result)
        self.total_tests += 1
        self.total_duration += result.duration
        
        if result.success:
            self.successful_tests += 1
            self.avg_completeness = (
                (self.avg_completeness * (self.successful_tests - 1) +
                 result.completeness) / self.successful_tests
            )
        else:
            self.failed_tests += 1
            if result.error:
                self.errors.append(result.error)
        
        if self.total_tests > 0:
            self.avg_duration = self.total_duration / self.total_tests
        
        if self.successful_tests > 0:
            durations = [r.duration for r in self.test_results if r.success]
            if durations:
                self.min_duration = min(durations)
                self.max_duration = max(durations)
        
        self.success_rate = self.successful_tests / self.total_tests


class SourceTestSuite:
    """刮削源测试套件"""
    
    # 默认测试用例
    DEFAULT_TEST_CASES = [
        TestCase(
            number='JAV-001',
            name='标准JAV番号',
            content_type='movie',
            expected_fields=['title', 'number']
        ),
        TestCase(
            number='FC2-PPV-1234',
            name='FC2番号',
            content_type='movie',
            expected_fields=['title', 'number']
        ),
        TestCase(
            number='Chinese-Movie-2024',
            name='中文电影',
            content_type='movie',
            expected_fields=['title', 'number']
        ),
    ]
    
    def __init__(self):
        self.test_cases: List[TestCase] = self.DEFAULT_TEST_CASES.copy()
        self.test_results: Dict[str, List[TestResult]] = {}
    
    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)
    
    def load_test_cases_from_file(self, filepath: str):
        """从文件加载测试用例"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for item in data.get('test_cases', []):
            test_case = TestCase(
                number=item['number'],
                name=item.get('name', ''),
                content_type=item.get('content_type', 'movie'),
                expected_fields=item.get('expected_fields', []),
                metadata=item.get('metadata', {})
            )
            self.test_cases.append(test_case)
    
    async def test_source(self, source: str,
                        scrape_function: Callable,
                        test_cases: Optional[List[TestCase]] = None) -> List[TestResult]:
        """测试单个源"""
        if test_cases is None:
            test_cases = self.test_cases
        
        results = []
        
        for test_case in test_cases:
            start_time = time.time()
            try:
                # 调用刮削函数
                data = await scrape_function(source, test_case.number)
                
                # 计算完整度
                completeness = self._calculate_completeness(data, test_case.expected_fields)
                
                result = TestResult(
                    source=source,
                    test_case=test_case,
                    success=True,
                    duration=time.time() - start_time,
                    completeness=completeness,
                    data=data
                )
            except Exception as e:
                result = TestResult(
                    source=source,
                    test_case=test_case,
                    success=False,
                    duration=time.time() - start_time,
                    error=str(e)
                )
            
            results.append(result)
        
        # 保存结果
        self.test_results[source] = results
        
        return results
    
    def _calculate_completeness(self, data: Dict, 
                               expected_fields: List[str]) -> float:
        """计算数据完整度"""
        if not expected_fields:
            return 100.0
        
        filled = 0
        for field in expected_fields:
            if field in data and data[field]:
                filled += 1
        
        return (filled / len(expected_fields)) * 100
    
    def run_all_tests(self, scrape_function: Callable,
                     sources: List[str]) -> Dict[str, List[TestResult]]:
        """运行所有测试"""
        all_results = {}
        
        for source in sources:
            results = asyncio.run(self.test_source(source, scrape_function))
            all_results[source] = results
        
        return all_results
    
    def get_summary(self, source: str) -> Dict:
        """获取测试摘要"""
        results = self.test_results.get(source, [])
        
        if not results:
            return {
                'source': source,
                'total': 0,
                'success': 0,
                'failed': 0,
                'success_rate': 0.0
            }
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        return {
            'source': source,
            'total': len(results),
            'success': successful,
            'failed': failed,
            'success_rate': successful / len(results) if results else 0.0,
            'avg_completeness': statistics.mean(
                [r.completeness for r in results if r.success]
            ) if successful > 0 else 0.0,
            'avg_duration': statistics.mean([r.duration for r in results])
        }


class SourceBenchmark:
    """刮削源基准测试"""
    
    # 基准测试视频
    BENCHMARK_VIDEOS = [
        ('JAV-001', 'movie', '标准JAV番号'),
        ('FC2-PPV-999', 'movie', 'FC2番号'),
        ('Chinese-2024-001', 'movie', '中文电影'),
    ]
    
    def __init__(self):
        self.benchmark_results: Dict[str, BenchmarkResult] = {}
    
    async def benchmark_source(self, source: str,
                            scrape_function: Callable,
                            timeout: int = 30) -> BenchmarkResult:
        """基准测试单个源"""
        result = BenchmarkResult(source=source)
        
        for video_number, video_type, description in self.BENCHMARK_VIDEOS:
            start_time = time.time()
            try:
                # 带超时的测试
                data = await asyncio.wait_for(
                    scrape_function(source, video_number),
                    timeout=timeout
                )
                
                duration = time.time() - start_time
                
                # 计算完整度
                completeness = self._calculate_basic_completeness(data)
                
                test_result = TestResult(
                    source=source,
                    test_case=TestCase(
                        number=video_number,
                        name=description,
                        content_type=video_type
                    ),
                    success=True,
                    duration=duration,
                    completeness=completeness,
                    data=data
                )
            except asyncio.TimeoutError:
                test_result = TestResult(
                    source=source,
                    test_case=TestCase(
                        number=video_number,
                        name=description,
                        content_type=video_type
                    ),
                    success=False,
                    duration=timeout,
                    error='Timeout'
                )
            except Exception as e:
                test_result = TestResult(
                    source=source,
                    test_case=TestCase(
                        number=video_number,
                        name=description,
                        content_type=video_type
                    ),
                    success=False,
                    duration=time.time() - start_time,
                    error=str(e)
                )
            
            result.add_result(test_result)
        
        self.benchmark_results[source] = result
        return result
    
    def _calculate_basic_completeness(self, data: Dict) -> float:
        """计算基本完整度"""
        basic_fields = ['title', 'number', 'release', 'studio']
        if not data:
            return 0.0
        
        filled = sum(1 for f in basic_fields if data.get(f))
        return (filled / len(basic_fields)) * 100
    
    async def benchmark_all(self, sources: List[str],
                          scrape_function: Callable) -> Dict[str, BenchmarkResult]:
        """基准测试所有源"""
        tasks = [
            self.benchmark_source(source, scrape_function)
            for source in sources
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        benchmark_results = {}
        for source, result in zip(sources, results):
            if isinstance(result, Exception):
                # 处理异常
                benchmark_results[source] = BenchmarkResult(source=source)
                benchmark_results[source].errors.append(str(result))
            else:
                benchmark_results[source] = result
        
        return benchmark_results
    
    def compare_sources(self, sources: Optional[List[str]] = None) -> Dict:
        """对比多个源"""
        if sources is None:
            sources = list(self.benchmark_results.keys())
        
        # 收集所有源的结果
        comparison = {
            'sources': [],
            'ranking': {
                'by_success_rate': [],
                'by_speed': [],
                'by_quality': [],
                'overall': []
            }
        }
        
        for source in sources:
            result = self.benchmark_results.get(source)
            if not result:
                continue
            
            source_data = {
                'source': source,
                'success_rate': result.success_rate,
                'avg_duration': result.avg_duration,
                'avg_completeness': result.avg_completeness,
                'total_tests': result.total_tests
            }
            comparison['sources'].append(source_data)
        
        # 按各项指标排序
        sources_data = comparison['sources']
        
        comparison['ranking']['by_success_rate'] = sorted(
            sources_data,
            key=lambda x: x['success_rate'],
            reverse=True
        )
        
        comparison['ranking']['by_speed'] = sorted(
            sources_data,
            key=lambda x: x['avg_duration']
        )
        
        comparison['ranking']['by_quality'] = sorted(
            sources_data,
            key=lambda x: x['avg_completeness'],
            reverse=True
        )
        
        # 计算综合评分
        for source_data in sources_data:
            overall_score = (
                source_data['success_rate'] * 0.4 +
                max(0, 1 - source_data['avg_duration'] / 10) * 0.3 +
                source_data['avg_completeness'] / 100 * 0.3
            )
            source_data['overall_score'] = overall_score
        
        comparison['ranking']['overall'] = sorted(
            sources_data,
            key=lambda x: x['overall_score'],
            reverse=True
        )
        
        return comparison
    
    def get_best_source(self, sources: Optional[List[str]] = None) -> Optional[str]:
        """获取最佳源"""
        comparison = self.compare_sources(sources)
        
        overall_ranking = comparison['ranking']['overall']
        if overall_ranking:
            return overall_ranking[0]['source']
        
        return None
    
    def export_results(self, filepath: str):
        """导出结果"""
        results = {}
        
        for source, result in self.benchmark_results.items():
            results[source] = {
                'total_tests': result.total_tests,
                'successful_tests': result.successful_tests,
                'failed_tests': result.failed_tests,
                'success_rate': result.success_rate,
                'avg_duration': result.avg_duration,
                'min_duration': result.min_duration,
                'max_duration': result.max_duration,
                'avg_completeness': result.avg_completeness,
                'errors': result.errors,
                'timestamp': datetime.now().isoformat()
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


class SourceQualityEvaluator:
    """源质量评估"""
    
    # 质量标准
    QUALITY_THRESHOLDS = {
        'success_rate': 0.8,
        'response_time': 3.0,
        'data_quality': 70.0,
        'uptime': 0.95
    }
    
    def __init__(self):
        self.quality_reports: Dict[str, Dict] = {}
    
    def evaluate_source(self, source: str,
                      benchmark_result: BenchmarkResult,
                      monitor_data: Optional[Dict] = None) -> Dict:
        """评估源质量"""
        report = {
            'source': source,
            'metrics': {},
            'overall_score': 0.0,
            'grade': 'N/A',
            'recommendations': [],
            'issues': []
        }
        
        # 1. 成功率
        report['metrics']['success_rate'] = {
            'value': benchmark_result.success_rate,
            'threshold': self.QUALITY_THRESHOLDS['success_rate'],
            'passed': benchmark_result.success_rate >= self.QUALITY_THRESHOLDS['success_rate'],
            'weight': 0.3
        }
        
        # 2. 响应时间
        report['metrics']['response_time'] = {
            'value': benchmark_result.avg_duration,
            'threshold': self.QUALITY_THRESHOLDS['response_time'],
            'passed': benchmark_result.avg_duration <= self.QUALITY_THRESHOLDS['response_time'],
            'weight': 0.2
        }
        
        # 3. 数据质量
        report['metrics']['data_quality'] = {
            'value': benchmark_result.avg_completeness,
            'threshold': self.QUALITY_THRESHOLDS['data_quality'],
            'passed': benchmark_result.avg_completeness >= self.QUALITY_THRESHOLDS['data_quality'],
            'weight': 0.3
        }
        
        # 4. 监控数据（如有）
        if monitor_data and source in monitor_data:
            uptime = monitor_data[source].get('uptime', 1.0)
        else:
            uptime = 1.0 if benchmark_result.success_rate >= 0.9 else 0.5
        
        report['metrics']['uptime'] = {
            'value': uptime,
            'threshold': self.QUALITY_THRESHOLDS['uptime'],
            'passed': uptime >= self.QUALITY_THRESHOLDS['uptime'],
            'weight': 0.2
        }
        
        # 计算综合评分
        total_score = 0.0
        for metric_name, metric_data in report['metrics'].items():
            # 归一化到0-100
            if metric_name == 'response_time':
                normalized = max(0, 100 - metric_data['value'] * 10)
            else:
                normalized = metric_data['value'] * 100
            
            weighted = normalized * metric_data['weight']
            total_score += weighted
        
        report['overall_score'] = total_score
        
        # 评级
        if total_score >= 90:
            report['grade'] = 'A'
        elif total_score >= 80:
            report['grade'] = 'B'
        elif total_score >= 70:
            report['grade'] = 'C'
        elif total_score >= 60:
            report['grade'] = 'D'
        else:
            report['grade'] = 'F'
        
        # 生成建议
        self._generate_recommendations(report)
        
        # 识别问题
        self._identify_issues(report)
        
        self.quality_reports[source] = report
        
        return report
    
    def _generate_recommendations(self, report: Dict):
        """生成改进建议"""
        recommendations = []
        
        for metric_name, metric_data in report['metrics'].items():
            if not metric_data['passed']:
                if metric_name == 'success_rate':
                    recommendations.append(
                        f"提高成功率：当前 {metric_data['value']:.1%}，"
                        f"目标 {metric_data['threshold']:.1%}"
                    )
                elif metric_name == 'response_time':
                    recommendations.append(
                        f"优化响应时间：当前 {metric_data['value']:.1f}s，"
                        f"目标 ≤{metric_data['threshold']:.1f}s"
                    )
                elif metric_name == 'data_quality':
                    recommendations.append(
                        f"提升数据质量：当前 {metric_data['value']:.1f}，"
                        f"目标 ≥{metric_data['threshold']:.1f}"
                    )
                elif metric_name == 'uptime':
                    recommendations.append(
                        f"提高可用性：当前 {metric_data['value']:.1%}，"
                        f"目标 {metric_data['threshold']:.1%}"
                    )
        
        report['recommendations'] = recommendations
    
    def _identify_issues(self, report: Dict):
        """识别问题"""
        issues = []
        
        for metric_name, metric_data in report['metrics'].items():
            if not metric_data['passed']:
                gap = abs(metric_data['value'] - metric_data['threshold'])
                if gap > 0.2:  # 差距超过20%
                    issues.append(f"{metric_name}: 差距较大，需要重点优化")
        
        report['issues'] = issues
    
    def get_all_reports(self) -> Dict[str, Dict]:
        """获取所有评估报告"""
        return self.quality_reports
    
    def get_top_sources(self, count: int = 5) -> List[str]:
        """获取最佳源列表"""
        sorted_reports = sorted(
            self.quality_reports.items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        )
        
        return [source for source, _ in sorted_reports[:count]]
    
    def export_report(self, filepath: str):
        """导出评估报告"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.quality_reports, f, ensure_ascii=False, indent=2)


# 全局实例
_test_suite: Optional[SourceTestSuite] = None
_benchmark: Optional[SourceBenchmark] = None
_evaluator: Optional[SourceQualityEvaluator] = None


def get_test_suite() -> SourceTestSuite:
    """获取测试套件单例"""
    global _test_suite
    if _test_suite is None:
        _test_suite = SourceTestSuite()
    return _test_suite


def get_benchmark() -> SourceBenchmark:
    """获取基准测试单例"""
    global _benchmark
    if _benchmark is None:
        _benchmark = SourceBenchmark()
    return _benchmark


def get_evaluator() -> SourceQualityEvaluator:
    """获取质量评估器单例"""
    global _evaluator
    if _evaluator is None:
        _evaluator = SourceQualityEvaluator()
    return _evaluator
