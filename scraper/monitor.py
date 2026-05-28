"""
刮削源健康监控系统
提供源的实时状态监控、告警和自动故障转移功能
"""
import time
import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging


@dataclass
class SourceStatus:
    """源状态"""
    source: str
    success_rate: float = 0.0
    avg_duration: float = 0.0
    avg_quality: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_check: Optional[float] = None
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    is_healthy: bool = True
    status: str = 'unknown'  # healthy, warning, error, unknown

    def update(self, success: bool, duration: float, quality: float = 0.0):
        """更新状态"""
        self.total_requests += 1
        self.last_check = time.time()
        
        if success:
            self.successful_requests += 1
            self.last_success = time.time()
        else:
            self.failed_requests += 1
            self.last_failure = time.time()
        
        # 计算成功率
        self.success_rate = self.successful_requests / self.total_requests
        
        # 更新平均响应时间
        if self.avg_duration == 0:
            self.avg_duration = duration
        else:
            self.avg_duration = (self.avg_duration * (self.total_requests - 1) + duration) / self.total_requests
        
        # 更新平均质量
        if self.avg_quality == 0:
            self.avg_quality = quality
        else:
            self.avg_quality = (self.avg_quality * (self.total_requests - 1) + quality) / self.total_requests
        
        # 更新健康状态
        self._update_health_status()
    
    def _update_health_status(self):
        """更新健康状态"""
        if self.total_requests < 5:
            self.status = 'unknown'
            self.is_healthy = True
        elif self.success_rate >= 0.8 and self.avg_duration <= 5:
            self.status = 'healthy'
            self.is_healthy = True
        elif self.success_rate >= 0.5:
            self.status = 'warning'
            self.is_healthy = True
        else:
            self.status = 'error'
            self.is_healthy = False


@dataclass
class Alert:
    """告警"""
    source: str
    level: str  # info, warning, error, critical
    message: str
    timestamp: float = field(default_factory=time.time)
    acknowledged: bool = False

    def acknowledge(self):
        """确认告警"""
        self.acknowledged = True


class SourceMonitor:
    """刮削源监控"""
    
    def __init__(self):
        self.statuses: Dict[str, SourceStatus] = defaultdict(
            lambda: SourceStatus(source='')
        )
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []
        self.logger = logging.getLogger(__name__)
        
        # 告警阈值
        self.thresholds = {
            'success_rate': 0.5,  # 成功率低于50%告警
            'response_time': 10.0,  # 响应时间超过10秒告警
            'data_quality': 50.0,  # 数据质量低于50告警
            'failure_count': 3  # 连续失败3次告警
        }
    
    def record_request(self, source: str, success: bool, 
                     duration: float, quality: float = 0.0):
        """记录一次请求"""
        if source not in self.statuses:
            self.statuses[source] = SourceStatus(source=source)
        
        status = self.statuses[source]
        old_health = status.is_healthy
        old_status = status.status
        
        status.update(success, duration, quality)
        
        # 检查是否需要告警
        self._check_alerts(source, status, old_status)
    
    def _check_alerts(self, source: str, status: SourceStatus, old_status: str):
        """检查是否触发告警"""
        # 成功率过低
        if status.success_rate < self.thresholds['success_rate'] and \
           status.total_requests >= 10:
            self._add_alert(source, 'warning',
                          f'成功率过低: {status.success_rate:.1%}')
        
        # 响应时间过长
        if status.avg_duration > self.thresholds['response_time']:
            self._add_alert(source, 'info',
                          f'响应时间较长: {status.avg_duration:.1f}s')
        
        # 数据质量过低
        if status.avg_quality > 0 and \
           status.avg_quality < self.thresholds['data_quality']:
            self._add_alert(source, 'warning',
                          f'数据质量较低: {status.avg_quality:.1f}')
        
        # 状态变化告警
        if old_status != status.status and status.status == 'error':
            self._add_alert(source, 'error',
                          f'源状态变为错误，成功率: {status.success_rate:.1%}')
        
        # 恢复告警
        if old_status == 'error' and status.status == 'healthy':
            self._add_alert(source, 'info',
                          f'源已恢复正常，成功率: {status.success_rate:.1%}')
    
    def _add_alert(self, source: str, level: str, message: str):
        """添加告警"""
        # 检查是否已有相同的未确认告警
        for alert in self.alerts:
            if alert.source == source and \
               alert.level == level and \
               alert.message == message and \
               not alert.acknowledged:
                # 更新告警时间
                alert.timestamp = time.time()
                return
        
        # 创建新告警
        alert = Alert(source=source, level=level, message=message)
        self.alerts.append(alert)
        
        # 调用告警处理器
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"告警处理器错误: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """添加告警处理器"""
        self.alert_handlers.append(handler)
    
    def get_status(self, source: str) -> Optional[SourceStatus]:
        """获取源状态"""
        return self.statuses.get(source)
    
    def get_all_statuses(self) -> Dict[str, SourceStatus]:
        """获取所有源状态"""
        return dict(self.statuses)
    
    def get_health_report(self) -> Dict:
        """生成健康报告"""
        healthy = []
        warning = []
        error = []
        unknown = []
        
        for source, status in self.statuses.items():
            if status.status == 'healthy':
                healthy.append(source)
            elif status.status == 'warning':
                warning.append(source)
            elif status.status == 'error':
                error.append(source)
            else:
                unknown.append(source)
        
        # 获取未确认的告警
        unacknowledged_alerts = [a for a in self.alerts if not a.acknowledged]
        
        return {
            'healthy': healthy,
            'warning': warning,
            'error': error,
            'unknown': unknown,
            'alerts': [
                {
                    'source': a.source,
                    'level': a.level,
                    'message': a.message,
                    'timestamp': a.timestamp,
                    'acknowledged': a.acknowledged
                }
                for a in unacknowledged_alerts[-10:]  # 最近10条
            ],
            'total_sources': len(self.statuses),
            'healthy_count': len(healthy),
            'warning_count': len(warning),
            'error_count': len(error),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_healthy_sources(self) -> List[str]:
        """获取健康的源列表"""
        return [
            source for source, status in self.statuses.items()
            if status.is_healthy and status.status != 'unknown'
        ]
    
    def get_best_sources(self, count: int = 5) -> List[str]:
        """获取最佳的源列表"""
        scored = []
        for source, status in self.statuses.items():
            if status.total_requests >= 5:  # 至少5次请求
                # 计算综合评分
                score = (
                    status.success_rate * 0.5 +
                    max(0, 1 - status.avg_duration / 10) * 0.3 +
                    status.avg_quality / 100 * 0.2
                )
                scored.append((source, score))
        
        # 按评分排序
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [s for s, _ in scored[:count]]
    
    def reset_source(self, source: str):
        """重置源状态"""
        if source in self.statuses:
            self.statuses[source] = SourceStatus(source=source)
    
    def clear_alerts(self, source: Optional[str] = None):
        """清除告警"""
        if source:
            self.alerts = [a for a in self.alerts if a.source != source]
        else:
            self.alerts.clear()
    
    def acknowledge_alert(self, source: str, level: str, message: str):
        """确认告警"""
        for alert in self.alerts:
            if alert.source == source and \
               alert.level == level and \
               alert.message == message:
                alert.acknowledge()


class SmartFallback:
    """智能故障转移"""
    
    def __init__(self, monitor: SourceMonitor):
        self.monitor = monitor
        self.fallback_cache: Dict[str, List[str]] = {}
        self.logger = logging.getLogger(__name__)
    
    def get_fallback_sources(self, failed_source: str,
                           source_groups: Dict[str, List[str]],
                           max_sources: int = 3) -> List[str]:
        """获取备用源列表"""
        cache_key = f"{failed_source}_{max_sources}"
        
        if cache_key in self.fallback_cache:
            return self.fallback_cache[cache_key]
        
        # 1. 找到失败源所在的组
        source_category = None
        for cat_id, sources in source_groups.items():
            if failed_source in sources:
                source_category = cat_id
                break
        
        if not source_category:
            self.logger.warning(f"找不到源 {failed_source} 的分类")
            return []
        
        # 2. 获取同类源的备用源
        fallbacks = []
        for cat_id, sources in source_groups.items():
            if cat_id == source_category:
                # 同一分类，排除失败的源
                fallbacks.extend([s for s in sources if s != failed_source])
            else:
                # 其他分类作为备选
                fallbacks.extend(sources)
        
        # 3. 按健康状态和评分排序
        scored_fallbacks = []
        for source in fallbacks:
            status = self.monitor.get_status(source)
            if status and status.is_healthy:
                score = (
                    status.success_rate * 0.5 +
                    max(0, 1 - status.avg_duration / 10) * 0.3 +
                    status.avg_quality / 100 * 0.2
                )
                scored_fallbacks.append((source, score))
        
        scored_fallbacks.sort(key=lambda x: x[1], reverse=True)
        
        result = [s for s, _ in scored_fallbacks[:max_sources]]
        
        # 缓存结果
        self.fallback_cache[cache_key] = result
        
        return result
    
    def should_fallback(self, source: str) -> bool:
        """判断是否应该切换到备用源"""
        status = self.monitor.get_status(source)
        
        if not status:
            return True
        
        # 连续失败超过阈值
        if status.failed_requests >= 3 and \
           status.success_rate < 0.3:
            return True
        
        return False


class ScheduledHealthCheck:
    """定时健康检查"""
    
    def __init__(self, monitor: SourceMonitor, interval_minutes: int = 60):
        self.monitor = monitor
        self.interval = interval_minutes * 60
        self.last_check: Dict[str, float] = {}
        self.running = False
        self.logger = logging.getLogger(__name__)
    
    async def check_source(self, source: str, 
                         test_function: Optional[Callable] = None) -> bool:
        """检查单个源"""
        if not self.should_check(source):
            return True
        
        try:
            if test_function:
                success = await test_function(source)
            else:
                # 默认检查：只是更新时间
                success = True
            
            self.last_check[source] = time.time()
            
            # 记录到监控
            self.monitor.record_request(
                source=source,
                success=success,
                duration=0.0,
                quality=0.0
            )
            
            return success
        except Exception as e:
            self.logger.error(f"健康检查失败 {source}: {e}")
            self.monitor.record_request(
                source=source,
                success=False,
                duration=0.0,
                quality=0.0
            )
            return False
    
    def should_check(self, source: str) -> bool:
        """检查是否需要检查"""
        if source not in self.last_check:
            return True
        
        return time.time() - self.last_check[source] > self.interval
    
    async def check_all(self, sources: List[str],
                      test_function: Optional[Callable] = None):
        """检查所有源"""
        tasks = []
        for source in sources:
            if self.should_check(source):
                tasks.append(self.check_source(source, test_function))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def run_periodically(self, sources: List[str],
                            test_function: Optional[Callable] = None):
        """定期运行检查"""
        self.running = True
        while self.running:
            await self.check_all(sources, test_function)
            await asyncio.sleep(self.interval)
    
    def stop(self):
        """停止检查"""
        self.running = False


# 全局实例
_monitor: Optional[SourceMonitor] = None


def get_monitor() -> SourceMonitor:
    """获取监控器单例"""
    global _monitor
    if _monitor is None:
        _monitor = SourceMonitor()
    return _monitor


def init_monitor() -> SourceMonitor:
    """初始化监控器"""
    global _monitor
    _monitor = SourceMonitor()
    return _monitor
