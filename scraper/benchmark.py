"""
刮削源性能基准测试
用于测试各刮削源的性能表现
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import statistics


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    source: str
    number: str  # 测试用的番号
    start_time: float
    end_time: float = 0
    duration: float = 0  # 总耗时（秒）
    http_requests: int = 0  # HTTP 请求次数
    response_size: int = 0  # 响应大小（字节）
    success: bool = False
    error_message: Optional[str] = None
    
    # 性能指标
    avg_response_time: float = 0  # 平均响应时间
    min_response_time: float = 0  # 最小响应时间
    max_response_time: float = 0  # 最大响应时间
    
    # 数据指标
    data_size: int = 0  # 数据大小
    fields_extracted: int = 0  # 提取的字段数
    
    def calculate(self):
        """计算性能指标"""
        if self.http_requests > 0:
            self.avg_response_time = self.duration / self.http_requests
            self.min_response_time = min(0, self.min_response_time)  # 简化
            self.max_response_time = self.duration
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.http_times: Dict[str, List[float]] = {}  # 按刮削源记录HTTP响应时间
    
    async def benchmark_source(self, source: str, test_numbers: List[str],
                              timeout: int = 30) -> Dict:
        """测试单个刮削源的性能
        
        Args:
            source: 刮削源名称
            test_numbers: 测试用的番号列表
            timeout: 超时时间（秒）
        
        Returns:
            性能统计结果
        """
        durations = []
        successes = 0
        failures = 0
        errors = []
        
        for number in test_numbers:
            result = BenchmarkResult(
                source=source,
                number=number,
                start_time=time.time()
            )
            
            try:
                # 模拟刮取过程（实际使用时替换为真实刮取）
                duration = await self._scrape_with_timing(source, number, timeout)
                
                result.end_time = time.time()
                result.duration = duration
                result.success = True
                successes += 1
                durations.append(duration)
                
            except asyncio.TimeoutError:
                result.success = False
                result.error_message = "Timeout"
                failures += 1
                errors.append(f"{number}: Timeout")
                
            except Exception as e:
                result.success = False
                result.error_message = str(e)
                failures += 1
                errors.append(f"{number}: {str(e)}")
            
            self.results.append(result)
            await asyncio.sleep(0.5)  # 避免请求过快
        
        if source not in self.http_times:
            self.http_times[source] = []
        self.http_times[source].extend(durations)
        
        return {
            'source': source,
            'total_tests': len(test_numbers),
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / len(test_numbers) * 100) if test_numbers else 0,
            'avg_duration': statistics.mean(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0,
            'median_duration': statistics.median(durations) if durations else 0,
            'std_deviation': statistics.stdev(durations) if len(durations) > 1 else 0,
            'errors': errors[:5],  # 最多显示5个错误
        }
    
    async def _scrape_with_timing(self, source: str, number: str, timeout: int) -> float:
        """带计时的刮取"""
        start = time.time()
        
        # 模拟HTTP请求时间
        # 实际使用时替换为真实的刮取逻辑
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        # 模拟随机失败（10%概率）
        import random
        if random.random() < 0.1:
            raise Exception("Simulated error")
        
        return time.time() - start
    
    async def benchmark_all_sources(self, sources: List[str],
                                   test_numbers: List[str],
                                   timeout: int = 30) -> Dict[str, Dict]:
        """测试所有刮削源的性能
        
        Args:
            sources: 刮削源列表
            test_numbers: 测试用的番号列表
            timeout: 超时时间
        
        Returns:
            所有刮削源的性能统计结果
        """
        all_results = {}
        
        for source in sources:
            print(f"Benchmarking {source}...")
            result = await self.benchmark_source(source, test_numbers, timeout)
            all_results[source] = result
        
        return all_results
    
    def get_performance_summary(self) -> Dict:
        """获取性能摘要"""
        if not self.results:
            return {}
        
        summary = {}
        
        for result in self.results:
            if result.source not in summary:
                summary[result.source] = {
                    'total': 0,
                    'success': 0,
                    'fail': 0,
                    'total_duration': 0,
                    'durations': []
                }
            
            s = summary[result.source]
            s['total'] += 1
            s['total_duration'] += result.duration
            
            if result.success:
                s['success'] += 1
                s['durations'].append(result.duration)
            else:
                s['fail'] += 1
        
        # 计算统计信息
        for source, stats in summary.items():
            if stats['durations']:
                stats['avg_duration'] = statistics.mean(stats['durations'])
                stats['min_duration'] = min(stats['durations'])
                stats['max_duration'] = max(stats['durations'])
                stats['median_duration'] = statistics.median(stats['durations'])
                stats['success_rate'] = (stats['success'] / stats['total'] * 100)
            else:
                stats['avg_duration'] = 0
                stats['success_rate'] = 0
            
            # 计算性能评分（基于速度和成功率）
            # 速度权重40%，成功率权重60%
            if stats['avg_duration'] > 0:
                speed_score = max(0, 100 - (stats['avg_duration'] * 10))
            else:
                speed_score = 0
            performance_score = stats['success_rate'] * 0.6 + speed_score * 0.4
            
            stats['performance_score'] = round(performance_score, 2)
            stats['durations'] = []  # 清空详细数据以节省内存
        
        return summary
    
    def compare_sources(self, source1: str, source2: str) -> Dict:
        """比较两个刮削源的性能"""
        results1 = [r for r in self.results if r.source == source1]
        results2 = [r for r in self.results if r.source == source2]
        
        if not results1 or not results2:
            return {'error': 'One or both sources have no results'}
        
        success1 = sum(1 for r in results1 if r.success) / len(results1) * 100
        success2 = sum(1 for r in results2 if r.success) / len(results2) * 100
        
        durations1 = [r.duration for r in results1 if r.success]
        durations2 = [r.duration for r in results2 if r.success]
        
        avg1 = statistics.mean(durations1) if durations1 else 0
        avg2 = statistics.mean(durations2) if durations2 else 0
        
        return {
            'source1': source1,
            'source2': source2,
            'source1_success_rate': round(success1, 2),
            'source2_success_rate': round(success2, 2),
            'source1_avg_duration': round(avg1, 3),
            'source2_avg_duration': round(avg2, 3),
            'faster_source': source1 if avg1 < avg2 else source2,
            'more_reliable_source': source1 if success1 > success2 else source2,
        }
    
    def export_results(self, filename: str):
        """导出测试结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_performance_summary(),
                'results': [r.to_dict() for r in self.results]
            }, f, indent=2, ensure_ascii=False)


class LoadTester:
    """负载测试器"""
    
    def __init__(self):
        self.concurrent_tests = 0
        self.max_concurrent = 10
        self.queue = asyncio.Queue()
    
    async def load_test(self, source: str, numbers: List[str],
                       concurrent: int = 5, total: int = 100) -> Dict:
        """负载测试
        
        Args:
            source: 刮削源名称
            numbers: 番号列表
            concurrent: 并发数
            total: 总请求数
        
        Returns:
            负载测试结果
        """
        start_time = time.time()
        
        # 创建并发任务
        tasks = []
        for i in range(total):
            number = numbers[i % len(numbers)]
            task = asyncio.create_task(self._scrape_task(source, number))
            tasks.append(task)
            
            # 控制并发数
            if len(tasks) >= concurrent:
                await asyncio.gather(*tasks)
                tasks = []
        
        # 处理剩余任务
        if tasks:
            await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        return {
            'source': source,
            'total_requests': total,
            'concurrent': concurrent,
            'total_duration': round(total_duration, 2),
            'requests_per_second': round(total / total_duration, 2),
            'avg_latency': round(total_duration / total, 3),
        }
    
    async def _scrape_task(self, source: str, number: str):
        """执行刮取任务"""
        # 模拟刮取
        await asyncio.sleep(0.1)


# 生成基准测试报告
def generate_benchmark_report(benchmark: PerformanceBenchmark) -> str:
    """生成基准测试报告"""
    summary = benchmark.get_performance_summary()
    
    lines = [
        "=" * 80,
        "刮削源性能基准测试报告",
        "=" * 80,
        f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"总测试数: {len(benchmark.results)}",
        "",
        "=" * 80,
        "性能排名",
        "=" * 80,
        "",
    ]
    
    # 按性能评分排序
    sorted_sources = sorted(
        summary.items(),
        key=lambda x: x[1].get('performance_score', 0),
        reverse=True
    )
    
    for rank, (source, stats) in enumerate(sorted_sources, 1):
        lines.extend([
            f"\n{rank}. {source}",
            f"   性能评分: {stats.get('performance_score', 0)}/100",
            f"   成功率: {stats.get('success_rate', 0):.1f}%",
            f"   平均耗时: {stats.get('avg_duration', 0):.3f}秒",
            f"   最短耗时: {stats.get('min_duration', 0):.3f}秒",
            f"   最长耗时: {stats.get('max_duration', 0):.3f}秒",
        ])
    
    lines.append("\n" + "=" * 80)
    
    return "\n".join(lines)


# 测试代码
if __name__ == "__main__":
    async def main():
        benchmark = PerformanceBenchmark()
        
        # 测试用例
        test_sources = ['javbus_movie', 'javdb_movie', 'javlibrary_movie']
        test_numbers = ['ABC-123', 'DEF-456', 'GHI-789']
        
        # 运行基准测试
        results = await benchmark.benchmark_all_sources(test_sources, test_numbers)
        
        # 生成报告
        report = generate_benchmark_report(benchmark)
        print(report)
        
        # 导出结果
        benchmark.export_results('benchmark_results.json')
        print("\n结果已导出到 benchmark_results.json")
    
    asyncio.run(main())
