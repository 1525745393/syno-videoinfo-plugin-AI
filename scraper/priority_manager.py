"""
刮削源动态优先级管理器
根据成功率、响应时间、数据质量等指标动态调整源优先级
"""
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class PriorityConfig:
    """优先级配置"""
    base_priority: int = 50
    min_priority: int = 10
    max_priority: int = 100
    adjustment_interval: int = 3600  # 调整间隔（秒）

    # 权重配置
    success_rate_weight: float = 0.4
    response_time_weight: float = 0.2
    data_quality_weight: float = 0.3
    stability_weight: float = 0.1
    
    # 阈值配置
    success_rate_threshold: float = 0.8
    response_time_threshold: float = 3.0
    data_quality_threshold: float = 70.0


class DynamicPriorityManager:
    """动态优先级管理器"""
    
    def __init__(self, config: Optional[PriorityConfig] = None):
        self.config = config or PriorityConfig()
        
        # 基础优先级（用户设置的静态优先级）
        self.base_priorities: Dict[str, int] = {}
        
        # 当前动态优先级
        self.current_priorities: Dict[str, int] = {}
        
        # 最后调整时间
        self.last_adjustment: Dict[str, float] = {}
        
        # 优先级历史
        self.priority_history: Dict[str, List[Tuple[float, int]]] = defaultdict(list)
    
    def set_base_priority(self, source: str, priority: int):
        """设置源的基础优先级"""
        priority = max(self.config.min_priority, 
                      min(self.config.max_priority, priority))
        self.base_priorities[source] = priority
        
        # 如果还没有当前优先级，初始化为基础优先级
        if source not in self.current_priorities:
            self.current_priorities[source] = priority
    
    def get_priority(self, source: str) -> int:
        """获取源的当前优先级"""
        return self.current_priorities.get(
            source, 
            self.base_priorities.get(source, self.config.base_priority)
        )
    
    def calculate_dynamic_priority(self, source: str,
                                success_rate: float,
                                avg_duration: float,
                                data_quality: float,
                                stability: float = 1.0) -> int:
        """计算动态优先级"""
        
        # 1. 成功率得分 (0-100)
        success_score = success_rate * 100
        
        # 2. 响应时间得分 (0-100，越快越高)
        if avg_duration <= 0:
            time_score = 50
        else:
            time_score = max(0, min(100, (1 - avg_duration / 10) * 100))
        
        # 3. 数据质量得分 (0-100)
        quality_score = data_quality
        
        # 4. 稳定性得分 (0-100)
        stability_score = stability * 100
        
        # 5. 综合评分
        total_score = (
            success_score * self.config.success_rate_weight +
            time_score * self.config.response_time_weight +
            quality_score * self.config.data_quality_weight +
            stability_score * self.config.stability_weight
        )
        
        # 6. 结合基础优先级
        base = self.get_priority(source)
        dynamic_adjustment = (total_score - 50) * 0.5  # 调整幅度为中心±25
        
        new_priority = int(base + dynamic_adjustment)
        new_priority = max(self.config.min_priority, 
                          min(self.config.max_priority, new_priority))
        
        return new_priority
    
    def adjust_priority(self, source: str,
                      success_rate: float,
                      avg_duration: float,
                      data_quality: float,
                      stability: float = 1.0):
        """调整源的优先级"""
        # 检查是否需要调整
        if not self.should_adjust(source):
            return
        
        # 计算新优先级
        new_priority = self.calculate_dynamic_priority(
            source, success_rate, avg_duration, data_quality, stability
        )
        
        old_priority = self.get_priority(source)
        
        # 记录历史
        self.priority_history[source].append((time.time(), new_priority))
        
        # 只保留最近100条历史
        if len(self.priority_history[source]) > 100:
            self.priority_history[source] = self.priority_history[source][-100:]
        
        # 更新优先级
        self.current_priorities[source] = new_priority
        self.last_adjustment[source] = time.time()
        
        return old_priority, new_priority
    
    def should_adjust(self, source: str) -> bool:
        """检查是否应该调整优先级"""
        if source not in self.last_adjustment:
            return True
        
        return time.time() - self.last_adjustment[source] > \
               self.config.adjustment_interval
    
    def auto_adjust_all(self, stats: Dict[str, Dict]):
        """自动调整所有源的优先级"""
        adjusted = []
        
        for source, stat in stats.items():
            result = self.adjust_priority(
                source=source,
                success_rate=stat.get('success_rate', 0),
                avg_duration=stat.get('avg_duration', 0),
                data_quality=stat.get('avg_quality', 0),
                stability=stat.get('stability', 1.0)
            )
            
            if result:
                adjusted.append((source, result[0], result[1]))
        
        return adjusted
    
    def get_priority_order(self, sources: List[str]) -> List[str]:
        """获取按优先级排序的源列表"""
        scored = [(s, self.get_priority(s)) for s in sources]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in scored]
    
    def get_optimal_order(self, sources: List[str],
                        video_type: Optional[str] = None,
                        content_hint: Optional[str] = None) -> List[str]:
        """获取最优刮削顺序"""
        # 获取排序后的源
        ordered = self.get_priority_order(sources)
        
        # 如果有内容提示，可以进一步优化顺序
        if content_hint:
            ordered = self._optimize_for_content(ordered, content_hint)
        
        return ordered
    
    def _optimize_for_content(self, sources: List[str],
                            content_hint: str) -> List[str]:
        """根据内容优化顺序"""
        content_lower = content_hint.lower()
        
        # 类型特定优先级
        type_boost = {
            'jav': ['javbus_movie', 'javdb_movie', 'javlibrary_movie'],
            'fc2': ['fc2_movie', 'fc2hub_movie', 'fc2club_movie'],
            'chinese': ['douban_movie', 'maoyan_movie', 'mtime_movie'],
            'imdb': ['imdb_movie', 'tmdb_movie']
        }
        
        # 找出匹配的源并提升优先级
        boosted = []
        remaining = []
        
        for source in sources:
            is_boosted = False
            for keyword, preferred in type_boost.items():
                if keyword in content_lower:
                    if source in preferred:
                        boosted.append((source, 0))  # 高优先级
                        is_boosted = True
                        break
            
            if not is_boosted:
                remaining.append((source, 1))  # 普通优先级
        
        # 合并结果
        boosted.extend(remaining)
        boosted.sort(key=lambda x: x[1])
        
        return [s for s, _ in boosted]
    
    def reset_priority(self, source: str):
        """重置源的优先级为默认值"""
        if source in self.base_priorities:
            self.current_priorities[source] = self.base_priorities[source]
        else:
            self.current_priorities[source] = self.config.base_priority
    
    def reset_all_priorities(self):
        """重置所有优先级"""
        for source in self.base_priorities:
            self.current_priorities[source] = self.base_priorities[source]
    
    def get_priority_changes(self, source: str, 
                           hours: int = 24) -> List[Tuple[float, int]]:
        """获取源的优先级变化历史"""
        if source not in self.priority_history:
            return []
        
        cutoff = time.time() - hours * 3600
        return [(t, p) for t, p in self.priority_history[source] if t >= cutoff]
    
    def export_priorities(self) -> Dict[str, int]:
        """导出所有优先级"""
        return dict(self.current_priorities)
    
    def import_priorities(self, priorities: Dict[str, int]):
        """导入优先级"""
        for source, priority in priorities.items():
            self.set_base_priority(source, priority)


class TypeSpecificOptimizer:
    """类型特定优化器"""
    
    # 类型优化配置
    TYPE_CONFIGS = {
        'jav': {
            'primary': ['javdb_movie', 'javbus_movie'],
            'fallback': ['javlibrary_movie', 'dmm_movie', 'mgstage_movie'],
            'keywords': ['jav', '-', 'fc2']
        },
        'fc2': {
            'primary': ['fc2_movie', 'fc2hub_movie', 'fc2club_movie', 'fc2ppvdb_movie'],
            'fallback': ['javbus_movie', 'javdb_movie'],
            'keywords': ['fc2', 'ppv']
        },
        'chinese': {
            'primary': ['douban_movie', 'maoyan_movie'],
            'fallback': ['mtime_movie', 'hdouban_movie', 'imdb_movie'],
            'keywords': ['中文', '国产', '大陆', '港台']
        },
        'anime': {
            'primary': ['bangumi_movie', 'myanimelist_movie'],
            'fallback': ['javdb_movie', 'imdb_movie'],
            'keywords': ['anime', '动漫', '动画']
        },
        'international': {
            'primary': ['imdb_movie', 'tmdb_movie'],
            'fallback': ['allocine_movie', 'rottentomatoes_movie', 'letterboxd_movie'],
            'keywords': ['hollywood', 'usa']
        }
    }
    
    def __init__(self, priority_manager: DynamicPriorityManager):
        self.priority_manager = priority_manager
    
    def identify_content_type(self, content_hint: str) -> str:
        """识别内容类型"""
        content_lower = content_hint.lower()
        
        for content_type, config in self.TYPE_CONFIGS.items():
            if any(keyword.lower() in content_lower for keyword in config['keywords']):
                return content_type
        
        return 'international'  # 默认国际内容
    
    def get_priority_order(self, sources: List[str],
                         content_hint: str) -> List[str]:
        """根据内容类型获取优先级顺序"""
        content_type = self.identify_content_type(content_hint)
        config = self.TYPE_CONFIGS.get(content_type, 
                                       self.TYPE_CONFIGS['international'])
        
        # 构建优先级列表
        priority_list = []
        
        # 1. 主要源
        for source in config['primary']:
            if source in sources:
                priority_list.append(source)
        
        # 2. 备用源
        for source in config['fallback']:
            if source in sources and source not in priority_list:
                priority_list.append(source)
        
        # 3. 其他源
        for source in sources:
            if source not in priority_list:
                priority_list.append(source)
        
        return priority_list
    
    def suggest_fallback_order(self, failed_source: str,
                             sources: List[str]) -> List[str]:
        """建议备用源顺序"""
        content_type = None
        
        # 找出失败源的类型
        for ctype, config in self.TYPE_CONFIGS.items():
            if failed_source in config['primary'] or \
               failed_source in config['fallback']:
                content_type = ctype
                break
        
        if not content_type:
            # 无法识别类型，返回所有源按优先级排序
            return self.priority_manager.get_priority_order(sources)
        
        config = self.TYPE_CONFIGS[content_type]
        
        # 构建备用列表
        fallback_list = []
        
        # 1. 同类型的其他主要源
        for source in config['primary']:
            if source in sources and source != failed_source:
                fallback_list.append(source)
        
        # 2. 同类型的备用源
        for source in config['fallback']:
            if source in sources and source not in fallback_list:
                fallback_list.append(source)
        
        # 3. 其他类型的源
        for source in sources:
            if source not in fallback_list and source != failed_source:
                fallback_list.append(source)
        
        return fallback_list


# 全局实例
_priority_manager: Optional[DynamicPriorityManager] = None
_type_optimizer: Optional[TypeSpecificOptimizer] = None


def get_priority_manager() -> DynamicPriorityManager:
    """获取优先级管理器单例"""
    global _priority_manager
    if _priority_manager is None:
        _priority_manager = DynamicPriorityManager()
    return _priority_manager


def get_type_optimizer() -> TypeSpecificOptimizer:
    """获取类型优化器单例"""
    global _type_optimizer
    if _type_optimizer is None:
        _type_optimizer = TypeSpecificOptimizer(get_priority_manager())
    return _type_optimizer


def init_priority_manager(config: Optional[PriorityConfig] = None) -> DynamicPriorityManager:
    """初始化优先级管理器"""
    global _priority_manager
    _priority_manager = DynamicPriorityManager(config)
    return _priority_manager
