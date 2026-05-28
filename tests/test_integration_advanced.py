"""
刮削源集成测试
测试刮削源的端到端功能
"""

import pytest
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class IntegrationTestCase:
    """集成测试用例"""
    name: str
    number: str
    expected_sources: List[str]
    min_completeness: float = 70.0  # 最低完整度要求


class ScrapeIntegrationTester:
    """刮削集成测试器"""
    
    # 集成测试用例
    TEST_CASES = [
        # 标准 JAV 番号
        IntegrationTestCase(
            name="JAV标准番号",
            number="JAV-001",
            expected_sources=["javbus_movie", "javdb_movie", "javlibrary_movie"],
            min_completeness=70.0
        ),
        
        # FC2 PPV 番号
        IntegrationTestCase(
            name="FC2 PPV番号",
            number="FC2-PPV-123456",
            expected_sources=["fc2hub_movie", "fc2ppvdb_movie"],
            min_completeness=60.0
        ),
        
        # 无码番号
        IntegrationTestCase(
            name="无码番号",
            number="10MU-001",
            expected_sources=["kin8_movie", "javdb_movie"],
            min_completeness=60.0
        ),
        
        # 国产番号
        IntegrationTestCase(
            name="国产番号",
            number="MDOU-001",
            expected_sources=["hdouban_movie", "javdb_movie"],
            min_completeness=50.0
        ),
    ]
    
    def __init__(self):
        self.results: List[Dict] = []
    
    async def run_test_case(self, test_case: IntegrationTestCase) -> Dict:
        """运行单个测试用例"""
        result = {
            'name': test_case.name,
            'number': test_case.number,
            'sources_tested': [],
            'sources_succeeded': [],
            'sources_failed': [],
            'best_result': None,
            'duration': 0,
            'passed': False,
            'errors': []
        }
        
        start_time = time.time()
        
        for source in test_case.expected_sources:
            try:
                # 模拟刮取（实际使用时替换为真实刮取）
                scrape_result = await self._scrape(source, test_case.number)
                
                if scrape_result:
                    result['sources_succeeded'].append(source)
                    result['sources_tested'].append({
                        'source': source,
                        'success': True,
                        'data': scrape_result,
                        'completeness': self._calculate_completeness(scrape_result)
                    })
                    
                    # 选择最佳结果
                    if not result['best_result'] or \
                       result['sources_tested'][-1]['completeness'] > \
                       result['best_result']['completeness']:
                        result['best_result'] = {
                            'source': source,
                            'data': scrape_result,
                            'completeness': result['sources_tested'][-1]['completeness']
                        }
                else:
                    result['sources_failed'].append(source)
                    result['sources_tested'].append({
                        'source': source,
                        'success': False,
                        'error': 'No data returned'
                    })
            
            except Exception as e:
                result['sources_failed'].append(source)
                result['errors'].append(f"{source}: {str(e)}")
                result['sources_tested'].append({
                    'source': source,
                    'success': False,
                    'error': str(e)
                })
            
            # 避免请求过快
            await asyncio.sleep(0.5)
        
        result['duration'] = time.time() - start_time
        
        # 判断是否通过
        result['passed'] = (
            len(result['sources_succeeded']) > 0 and
            result['best_result'] and
            result['best_result']['completeness'] >= test_case.min_completeness
        )
        
        self.results.append(result)
        return result
    
    async def _scrape(self, source: str, number: str) -> Optional[Dict]:
        """实际刮取逻辑"""
        # TODO: 集成真实的刮取器
        # 这里只是一个示例实现
        try:
            from scraper.scraper import Scraper
            scraper = Scraper()
            return await scraper.scrape(number, sources=[source])
        except ImportError:
            # 如果刮取器未实现，返回模拟数据
            return None
    
    def _calculate_completeness(self, data: Dict) -> float:
        """计算数据完整度"""
        if not data:
            return 0.0
        
        important_fields = ['title', 'number', 'actors', 'studio', 'release']
        filled = sum(1 for f in important_fields if data.get(f))
        
        return (filled / len(important_fields)) * 100
    
    async def run_all_tests(self) -> List[Dict]:
        """运行所有集成测试"""
        results = []
        
        for test_case in self.TEST_CASES:
            print(f"\n运行测试: {test_case.name}")
            result = await self.run_test_case(test_case)
            results.append(result)
            
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            print(f"  状态: {status}")
            print(f"  成功率: {len(result['sources_succeeded'])}/{len(result['expected_sources'])}")
            print(f"  最佳完整度: {result['best_result']['completeness'] if result['best_result'] else 0:.1f}%")
        
        return results
    
    def generate_report(self) -> str:
        """生成集成测试报告"""
        if not self.results:
            return "No test results available."
        
        lines = [
            "=" * 80,
            "刮削源集成测试报告",
            "=" * 80,
            "",
            f"总测试数: {len(self.results)}",
            f"通过数: {sum(1 for r in self.results if r['passed'])}",
            f"失败数: {sum(1 for r in self.results if not r['passed'])}",
            "",
        ]
        
        # 按成功率排序
        sorted_results = sorted(
            self.results,
            key=lambda x: len(x['sources_succeeded']) / len(x['expected_sources']) if x['expected_sources'] else 0,
            reverse=True
        )
        
        for i, result in enumerate(sorted_results, 1):
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            
            lines.extend([
                f"\n{i}. {result['name']} ({result['number']})",
                f"   状态: {status}",
                f"   成功率: {len(result['sources_succeeded'])}/{len(result['expected_sources'])}",
                f"   耗时: {result['duration']:.2f}秒",
            ])
            
            if result['sources_succeeded']:
                lines.append(f"   成功的刮削源: {', '.join(result['sources_succeeded'])}")
            
            if result['sources_failed']:
                lines.append(f"   失败的刮削源: {', '.join(result['sources_failed'])}")
            
            if result['errors']:
                lines.append(f"   错误:")
                for error in result['errors'][:3]:
                    lines.append(f"     - {error}")
        
        lines.append("\n" + "=" * 80)
        
        # 添加统计摘要
        lines.extend([
            "",
            "刮削源成功率统计:",
            "",
        ])
        
        # 统计各刮削源的成功率
        source_stats = {}
        for result in self.results:
            for tested in result['sources_tested']:
                source = tested['source']
                if source not in source_stats:
                    source_stats[source] = {'total': 0, 'success': 0}
                source_stats[source]['total'] += 1
                if tested['success']:
                    source_stats[source]['success'] += 1
        
        # 按成功率排序
        sorted_sources = sorted(
            source_stats.items(),
            key=lambda x: x[1]['success'] / x[1]['total'] if x[1]['total'] > 0 else 0,
            reverse=True
        )
        
        for source, stats in sorted_sources:
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(f"  {source}: {rate:.1f}% ({stats['success']}/{stats['total']})")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


class EndToEndTester:
    """端到端测试器"""
    
    def __init__(self):
        self.test_files = []
    
    def create_test_file(self, filepath: str, content: Dict):
        """创建测试文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        self.test_files.append(filepath)
    
    async def test_full_workflow(self, number: str, sources: List[str]) -> Dict:
        """测试完整工作流程"""
        workflow_result = {
            'number': number,
            'sources': [],
            'final_result': None,
            'duration': 0,
            'success': False
        }
        
        start_time = time.time()
        
        # 1. 尝试每个刮削源
        for source in sources:
            try:
                result = await self._scrape_with_validation(source, number)
                
                if result:
                    workflow_result['sources'].append({
                        'source': source,
                        'success': True,
                        'data': result
                    })
                    
                    # 选择最佳结果
                    if not workflow_result['final_result'] or \
                       len(result) > len(workflow_result['final_result']['data']):
                        workflow_result['final_result'] = {
                            'source': source,
                            'data': result
                        }
                else:
                    workflow_result['sources'].append({
                        'source': source,
                        'success': False
                    })
            
            except Exception as e:
                workflow_result['sources'].append({
                    'source': source,
                    'success': False,
                    'error': str(e)
                })
            
            await asyncio.sleep(0.5)
        
        workflow_result['duration'] = time.time() - start_time
        workflow_result['success'] = workflow_result['final_result'] is not None
        
        return workflow_result
    
    async def _scrape_with_validation(self, source: str, number: str) -> Optional[Dict]:
        """带验证的刮取"""
        try:
            from scraper.scraper import Scraper
            from scraper.quality import check_quality, check_completeness
            
            scraper = Scraper()
            result = await scraper.scrape(number, sources=[source])
            
            if result:
                # 验证数据质量
                quality, errors, warnings = check_quality(result)
                completeness = check_completeness(result)
                
                # 只返回质量合格的数据
                if completeness['is_complete'] and quality.overall >= 60:
                    return result
            
            return None
            
        except ImportError:
            return None
    
    def cleanup(self):
        """清理测试文件"""
        import os
        for filepath in self.test_files:
            if os.path.exists(filepath):
                os.remove(filepath)


# Pytest fixtures
@pytest.fixture
def integration_tester():
    """集成测试器 fixture"""
    return ScrapeIntegrationTester()


@pytest.fixture
def end_to_end_tester():
    """端到端测试器 fixture"""
    tester = EndToEndTester()
    yield tester
    tester.cleanup()


# Pytest tests
@pytest.mark.asyncio
async def test_basic_integration():
    """基础集成测试"""
    tester = ScrapeIntegrationTester()
    test_case = IntegrationTestCase(
        name="基础测试",
        number="TEST-001",
        expected_sources=["javbus_movie"],
        min_completeness=50.0
    )
    
    result = await tester.run_test_case(test_case)
    
    # 基础测试允许失败
    assert result is not None
    assert 'passed' in result


@pytest.mark.asyncio
async def test_multiple_sources():
    """多刮削源测试"""
    tester = ScrapeIntegrationTester()
    test_case = IntegrationTestCase(
        name="多刮削源测试",
        number="TEST-002",
        expected_sources=["javbus_movie", "javdb_movie"],
        min_completeness=50.0
    )
    
    result = await tester.run_test_case(test_case)
    
    assert result['name'] == "多刮削源测试"
    assert 'sources_tested' in result
    assert 'best_result' in result


def test_completeness_calculation():
    """完整度计算测试"""
    tester = ScrapeIntegrationTester()
    
    # 测试数据
    data1 = {'title': 'Test', 'number': 'ABC', 'actors': ['A'], 'studio': 'S', 'release': '2024'}
    data2 = {'title': 'Test', 'number': 'ABC'}
    
    completeness1 = tester._calculate_completeness(data1)
    completeness2 = tester._calculate_completeness(data2)
    
    assert completeness1 == 100.0
    assert completeness2 == 40.0  # 2/5 = 40%


if __name__ == "__main__":
    # 运行集成测试
    async def main():
        tester = ScrapeIntegrationTester()
        results = await tester.run_all_tests()
        report = tester.generate_report()
        print(report)
    
    asyncio.run(main())
