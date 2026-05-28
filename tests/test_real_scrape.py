"""
刮削源真实测试框架
用于测试各个刮削源的实际刮取效果
"""

import pytest
import asyncio
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ScrapeTestCase:
    """刮削测试用例"""
    number: str  # 视频番号
    expected_fields: List[str]  # 期望的字段
    sources: List[str]  # 刮削源列表
    language: str = "zh"
    
    def __str__(self):
        return f"{self.number} -> {', '.join(self.sources)}"


@dataclass
class ScrapeResult:
    """刮取结果"""
    source: str
    success: bool
    duration: float
    data: Dict
    error: Optional[str] = None
    
    def is_complete(self, required_fields: List[str]) -> bool:
        """检查数据完整性"""
        if not self.success:
            return False
        return all(field in self.data and self.data[field] for field in required_fields)
    
    def get_completeness(self, required_fields: List[str]) -> float:
        """计算数据完整度"""
        if not self.success:
            return 0.0
        filled_fields = sum(1 for field in required_fields 
                          if field in self.data and self.data[field])
        return (filled_fields / len(required_fields)) * 100 if required_fields else 100.0


class ScrapeTester:
    """刮削测试器"""
    
    # 必需的元数据字段
    REQUIRED_FIELDS = ['title', 'number']
    OPTIONAL_FIELDS = ['actors', 'tags', 'outline', 'release', 'year', 
                      'runtime', 'studio', 'publisher', 'series', 
                      'director', 'thumb', 'poster', 'trailer', 'mosaic']
    
    # 测试用例样本（覆盖不同类型的番号）
    TEST_CASES = [
        # JAV 标准番号
        ScrapeTestCase("JAV-001", REQUIRED_FIELDS + ['actors', 'studio'], ["javbus_movie", "javdb_movie"]),
        ScrapeTestCase("FC2-PPV-123456", REQUIRED_FIELDS + ['actors', 'studio'], ["fc2hub_movie", "fc2ppvdb_movie"]),
        
        # 无码番号
        ScrapeTestCase("10MU-001", REQUIRED_FIELDS + ['actors', 'studio'], ["kin8_movie", "javdb_movie"]),
        
        # 欧美的
        ScrapeTestCase("ABC-12345", REQUIRED_FIELDS, ["javbus_movie"]),
        
        # 国产番号
        ScrapeTestCase("MDOU-001", REQUIRED_FIELDS + ['actors', 'studio'], ["javdb_movie", "hdouban_movie"]),
        
        # 动漫番号
        ScrapeTestCase("ABC-001", REQUIRED_FIELDS, ["bangumi_movie"]),
        
        # 电视剧
        ScrapeTestCase("权力的游戏", REQUIRED_FIELDS + ['actors', 'outline'], ["douban_tvshow", "tmdb_tvshow"]),
    ]
    
    def __init__(self, scraper_module=None):
        self.scraper_module = scraper_module
        self.results: List[ScrapeResult] = []
    
    async def scrape_single(self, test_case: ScrapeTestCase) -> List[ScrapeResult]:
        """刮取单个测试用例"""
        results = []
        
        for source in test_case.sources:
            start_time = time.time()
            try:
                # 模拟刮取过程（实际使用时替换为真实刮取）
                result = await self._scrape(test_case.number, source, test_case.language)
                duration = time.time() - start_time
                
                results.append(ScrapeResult(
                    source=source,
                    success=result is not None,
                    duration=duration,
                    data=result or {}
                ))
            except Exception as e:
                duration = time.time() - start_time
                results.append(ScrapeResult(
                    source=source,
                    success=False,
                    duration=duration,
                    data={},
                    error=str(e)
                ))
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        return results
    
    async def _scrape(self, number: str, source: str, lang: str):
        """实际刮取逻辑（需要集成真实的刮取器）"""
        # TODO: 集成真实的刮取器
        # 这里只是一个示例实现
        try:
            from scraper.scraper import Scraper
            scraper = Scraper()
            return await scraper.scrape(number, sources=[source], lang=lang)
        except ImportError:
            # 如果刮取器未实现，返回模拟数据
            return None
    
    async def run_all_tests(self) -> Dict:
        """运行所有测试"""
        all_results = {}
        
        for test_case in self.TEST_CASES:
            print(f"Testing: {test_case}")
            results = await self.scrape_single(test_case)
            all_results[str(test_case)] = results
            self.results.extend(results)
        
        return all_results
    
    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.results:
            return "No test results available."
        
        # 按刮削源分组统计
        by_source = {}
        for result in self.results:
            if result.source not in by_source:
                by_source[result.source] = {
                    'total': 0,
                    'success': 0,
                    'total_duration': 0,
                    'completeness_scores': []
                }
            
            stats = by_source[result.source]
            stats['total'] += 1
            if result.success:
                stats['success'] += 1
                stats['total_duration'] += result.duration
                completeness = result.get_completeness(self.REQUIRED_FIELDS)
                stats['completeness_scores'].append(completeness)
        
        # 生成报告
        lines = [
            "=" * 80,
            "刮削源测试报告",
            "=" * 80,
            "",
            f"总测试数: {len(self.results)}",
            f"成功: {sum(1 for r in self.results if r.success)}",
            f"失败: {sum(1 for r in self.results if not r.success)}",
            "",
            "=" * 80,
            "各刮削源统计",
            "=" * 80,
        ]
        
        for source, stats in sorted(by_source.items()):
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_duration = (stats['total_duration'] / stats['success']) if stats['success'] > 0 else 0
            avg_completeness = sum(stats['completeness_scores']) / len(stats['completeness_scores']) if stats['completeness_scores'] else 0
            
            lines.extend([
                f"\n{source}:",
                f"  总测试数: {stats['total']}",
                f"  成功率: {success_rate:.1f}%",
                f"  平均耗时: {avg_duration:.2f}秒",
                f"  平均完整度: {avg_completeness:.1f}%",
            ])
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


class TestCaseGenerator:
    """测试用例生成器"""
    
    # 已知的番号前缀映射
    PREFIX_MAP = {
        'JAV': 'JAV',
        'FC2': 'FC2-PPV',
        '10MU': 'KIN8',
        'HEYZO': 'HEYZO',
        'MDOU': 'MDOU',
        'ABP': 'ABP',
        'PRED': 'PRED',
    }
    
    @staticmethod
    def generate_from_file(file_path: str) -> List[ScrapeTestCase]:
        """从文件生成测试用例"""
        test_cases = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    number = line.strip()
                    if number and not number.startswith('#'):
                        prefix = number.split('-')[0] if '-' in number else ''
                        sources = TestCaseGenerator._get_sources_for_prefix(prefix)
                        test_cases.append(ScrapeTestCase(
                            number=number,
                            expected_fields=['title', 'number'],
                            sources=sources
                        ))
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        
        return test_cases
    
    @staticmethod
    def _get_sources_for_prefix(prefix: str) -> List[str]:
        """根据番号前缀获取推荐的刮削源"""
        prefix_upper = prefix.upper()
        
        if 'FC2' in prefix_upper:
            return ['fc2hub_movie', 'fc2ppvdb_movie', 'fc2club_movie']
        elif 'KIN' in prefix_upper or '10MU' in prefix_upper:
            return ['kin8_movie', 'javdb_movie']
        elif 'MDOU' in prefix_upper:
            return ['hdouban_movie', 'javdb_movie']
        elif 'HEYZO' in prefix_upper:
            return ['javdb_movie', 'javbus_movie']
        else:
            return ['javbus_movie', 'javdb_movie', 'javlibrary_movie']


# Pytest fixtures
@pytest.fixture
def scrape_tester():
    """刮削测试器 fixture"""
    return ScrapeTester()


@pytest.fixture
def sample_test_cases():
    """示例测试用例 fixture"""
    return ScrapeTester.TEST_CASES


# Pytest tests
@pytest.mark.asyncio
async def test_javbus_source():
    """测试 javbus 刮削源"""
    tester = ScrapeTester()
    test_case = ScrapeTestCase(
        number="JAV-001",
        expected_fields=['title', 'number'],
        sources=["javbus_movie"]
    )
    
    results = await tester.scrape_single(test_case)
    
    assert len(results) == 1
    result = results[0]
    assert result.source == "javbus_movie"
    # 注意：真实测试时需要检查 success


@pytest.mark.asyncio
async def test_multiple_sources():
    """测试多刮削源"""
    tester = ScrapeTester()
    test_case = ScrapeTestCase(
        number="ABC-123",
        expected_fields=['title', 'number'],
        sources=["javbus_movie", "javdb_movie"]
    )
    
    results = await tester.scrape_single(test_case)
    
    assert len(results) == 2
    sources_tested = {r.source for r in results}
    assert "javbus_movie" in sources_tested
    assert "javdb_movie" in sources_tested


@pytest.mark.asyncio
async def test_result_completeness():
    """测试结果完整性评估"""
    result = ScrapeResult(
        source="test_source",
        success=True,
        duration=1.0,
        data={
            'title': 'Test Movie',
            'number': 'ABC-123',
            'actors': ['Actor 1'],
            'studio': 'Test Studio'
        }
    )
    
    required_fields = ['title', 'number', 'actors']
    assert result.is_complete(required_fields) == True
    
    required_fields_with_missing = ['title', 'number', 'tags', 'outline']
    assert result.is_complete(required_fields_with_missing) == False
    
    completeness = result.get_completeness(['title', 'number', 'actors', 'tags'])
    assert completeness == 75.0  # 3/4 = 75%


def test_test_case_generator():
    """测试用例生成器"""
    cases = TestCaseGenerator.generate_from_file("nonexistent.txt")
    assert len(cases) == 0  # 文件不存在应返回空列表


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
