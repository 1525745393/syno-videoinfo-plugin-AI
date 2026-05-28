"""
刮削源管理统一接口
整合源管理、监控、优先级、测试等功能
"""
from typing import Dict, List, Optional, Callable
from .source_manager import SourceGroupManager, get_source_manager, init_source_manager
from .monitor import (
    SourceMonitor, 
    SmartFallback, 
    get_monitor, 
    init_monitor,
    SourceStatus,
    Alert
)
from .priority_manager import (
    DynamicPriorityManager,
    TypeSpecificOptimizer,
    get_priority_manager,
    get_type_optimizer,
    init_priority_manager
)
from .ranking import SourceRanking, ScrapeRecord
from .quality import DataQualityChecker, QualityScore
from .test_suite import (
    SourceTestSuite,
    SourceBenchmark,
    SourceQualityEvaluator,
    get_test_suite,
    get_benchmark,
    get_evaluator
)
from .persistence import (
    PersistentStorage,
    get_storage,
    init_storage,
    SourceState
)


class SourceManagementSystem:
    """刮削源管理系统"""
    
    def __init__(self):
        # 初始化各个组件
        self.source_manager = get_source_manager()
        self.monitor = get_monitor()
        self.priority_manager = get_priority_manager()
        self.type_optimizer = get_type_optimizer()
        self.ranking = SourceRanking()
        self.quality_checker = DataQualityChecker()
        self.test_suite = get_test_suite()
        self.benchmark = get_benchmark()
        self.evaluator = get_evaluator()
        self.storage = get_storage()
    
    def initialize(self, source_groups_path: Optional[str] = None,
                   storage_dir: Optional[str] = None):
        """初始化系统"""
        # 初始化源管理器
        if source_groups_path:
            init_source_manager(source_groups_path)
            self.source_manager = get_source_manager()
        
        # 初始化监控器
        init_monitor()
        self.monitor = get_monitor()
        
        # 初始化优先级管理器
        init_priority_manager()
        self.priority_manager = get_priority_manager()
        
        # 初始化类型优化器
        self.type_optimizer = get_type_optimizer()
        
        # 初始化持久化存储
        if storage_dir:
            init_storage(storage_dir)
        self.storage = get_storage()
        
        # 设置告警处理器
        self.monitor.add_alert_handler(self._handle_alert)
        
        # 从持久化存储恢复状态
        self._load_from_storage()
    
    def _load_from_storage(self):
        """从持久化存储恢复状态"""
        # 恢复源状态到监控器
        states = self.storage.get_all_states()
        for source, state in states.items():
            # 更新监控器中的状态
            if source not in self.monitor.statuses:
                status = SourceStatus(source=source)
                status.total_requests = state.total_requests
                status.successful_requests = state.successful_requests
                status.failed_requests = state.failed_requests
                status.last_request = state.last_request
                self.monitor.statuses[source] = status
            
            # 更新优先级
            if state.priority > 0:
                self.priority_manager.set_base_priority(source, state.priority)
    
    def _save_to_storage(self):
        """保存状态到持久化存储"""
        # 保存源状态 - 使用update_state，但不要设置计算属性
        for source, status in self.monitor.statuses.items():
            # 保存可直接设置的字段
            self.storage.update_state(
                source,
                total_requests=status.total_requests,
                successful_requests=status.successful_requests,
                failed_requests=status.failed_requests,
                last_request=status.last_request,
                priority=self.priority_manager.get_priority(source)
            )
            # total_duration 和 total_quality 需要手动计算和设置
            state = self.storage.get_state(source)
            if state:
                state.total_duration = status.avg_duration * status.successful_requests if status.successful_requests > 0 else 0
                state.total_quality = status.avg_quality * status.successful_requests if status.successful_requests > 0 else 0
    
    def _handle_alert(self, alert: Alert):
        """处理告警"""
        # 可以在这里添加日志、通知等逻辑
        print(f"[{alert.level.upper()}] {alert.source}: {alert.message}")
    
    def record_scrape(self, source: str, success: bool, 
                   duration: float, data: Optional[Dict] = None):
        """记录刮取结果"""
        # 1. 记录到监控器
        quality_score = 0.0
        if data:
            quality_result = self.quality_checker.check_all(data)
            quality_score = quality_result[0].overall

        self.monitor.record_request(source, success, duration, quality_score)

        # 2. 记录到排名系统
        record = ScrapeRecord(
            source=source,
            number=data.get('number', '') if data else '',
            success=success,
            duration=duration,
            timestamp=0,  # 会自动设置为当前时间
            completeness=quality_score
        )
        self.ranking.record(record)

        # 3. 记录到持久化存储
        number = data.get('number', '') if data else ''
        title = data.get('title', '') if data else ''
        self.storage.record_scrape(
            source, success, duration, quality_score, number, title
        )
    
    def get_optimal_sources(self, video_type: str = 'movie',
                          content_hint: Optional[str] = None,
                          limit: int = 5) -> List[str]:
        """获取最优源列表"""
        # 1. 获取所有启用的源
        all_sources = self.source_manager.get_all_sources()
        
        if not all_sources:
            return []
        
        # 2. 过滤掉不健康的源
        healthy_sources = []
        for source in all_sources:
            state = self.storage.get_state(source)
            # 如果没有禁用记录，或者没有禁用，就保留
            if not state or state.enabled:
                healthy_sources.append(source)
        
        if not healthy_sources:
            healthy_sources = all_sources
        
        # 3. 获取优先级排序
        if content_hint:
            # 使用类型优化器
            ordered = self.type_optimizer.get_priority_order(
                healthy_sources, content_hint
            )
        else:
            # 使用优先级管理器
            ordered = self.priority_manager.get_priority_order(healthy_sources)
        
        return ordered[:limit]
    
    def get_fallback_sources(self, failed_source: str,
                           max_sources: int = 3) -> List[str]:
        """获取备用源"""
        # 1. 获取源分组
        source_groups = {}
        for cat_id, cat in self.source_manager.categories.items():
            if cat.enabled:
                source_groups[cat_id] = cat.sources
        
        # 2. 使用智能故障转移
        fallback = SmartFallback(self.monitor)
        return fallback.get_fallback_sources(
            failed_source, source_groups, max_sources
        )
    
    def get_health_report(self) -> Dict:
        """获取健康报告"""
        report = self.monitor.get_health_report()
        
        # 从持久化存储补充信息
        states = self.storage.get_all_states()
        report['persistent_states'] = {
            source: state.to_dict()
            for source, state in states.items()
        }
        
        return report
    
    def get_source_status(self, source: str) -> Optional[SourceStatus]:
        """获取源状态"""
        status = self.monitor.get_status(source)
        
        # 补充持久化状态
        state = self.storage.get_state(source)
        if state:
            if not status:
                status = SourceStatus(source=source)
            status.enabled = state.enabled
            status.category = state.category
        
        return status
    
    def get_source_score(self, source: str) -> Dict:
        """获取源评分"""
        score = self.ranking.get_score(source)
        
        # 补充持久化统计
        stats = self.storage.get_statistics(source)
        score['persistent_stats'] = stats
        
        return score
    
    def enable_source(self, source: str):
        """启用源"""
        self.storage.update_state(source, enabled=True)
    
    def disable_source(self, source: str):
        """禁用源"""
        self.storage.update_state(source, enabled=False)
    
    def reset_source(self, source: str):
        """重置源"""
        self.monitor.reset_source(source)
        self.storage.reset_source(source)
    
    async def test_source(self, source: str,
                        scrape_function: Callable) -> Dict:
        """测试源"""
        # 1. 运行测试
        results = await self.test_suite.test_source(source, scrape_function)
        
        # 2. 获取测试摘要
        summary = self.test_suite.get_summary(source)
        
        # 3. 评估质量
        benchmark_result = self.benchmark.benchmark_source(source, scrape_function)
        quality_report = self.evaluator.evaluate_source(
            source, benchmark_result, None
        )
        
        return {
            'test_summary': summary,
            'quality_report': quality_report,
            'test_results': [
                {
                    'number': r.test_case.number,
                    'success': r.success,
                    'duration': r.duration,
                    'completeness': r.completeness,
                    'error': r.error
                }
                for r in results
            ]
        }
    
    def adjust_priorities(self):
        """调整所有源优先级"""
        # 获取所有源的评分
        all_sources = self.source_manager.get_all_sources()
        
        stats = {}
        for source in all_sources:
            score = self.ranking.get_score(source)
            stats[source] = {
                'success_rate': score.get('success_rate', 0),
                'avg_duration': score.get('avg_duration', 0),
                'avg_quality': score.get('avg_completeness', 0),
                'stability': 1.0
            }
        
        # 自动调整
        self.priority_manager.auto_adjust_all(stats)
        
        # 保存到存储
        self._save_to_storage()
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            'source_manager': self.source_manager.get_statistics(),
            'health': self.get_health_report(),
            'priority_changes': len(self.priority_manager.priority_history),
            'persistence': {
                'total_states': len(self.storage.states),
                'total_history': len(self.storage.history)
            }
        }
        
        return stats
    
    def save(self):
        """保存所有数据"""
        self._save_to_storage()
        self.storage.save()
    
    def export_configuration(self, output_path: str):
        """导出配置"""
        config = {
            'priorities': self.priority_manager.export_priorities(),
            'source_groups': {
                cat_id: {
                    'name': cat.name,
                    'enabled': cat.enabled,
                    'sources': cat.sources
                }
                for cat_id, cat in self.source_manager.categories.items()
            }
        }
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def export_data(self, output_dir: str):
        """导出所有数据"""
        self.storage.export_data(output_dir)
    
    def import_configuration(self, config_path: str):
        """导入配置"""
        import json
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 导入优先级
        if 'priorities' in config:
            self.priority_manager.import_priorities(config['priorities'])


# 全局实例
_sms: Optional[SourceManagementSystem] = None


def get_sms() -> SourceManagementSystem:
    """获取源管理系统单例"""
    global _sms
    if _sms is None:
        _sms = SourceManagementSystem()
    return _sms


def init_sms(source_groups_path: Optional[str] = None,
            storage_dir: Optional[str] = None) -> SourceManagementSystem:
    """初始化源管理系统"""
    global _sms
    _sms = SourceManagementSystem()
    _sms.initialize(source_groups_path, storage_dir)
    return _sms
