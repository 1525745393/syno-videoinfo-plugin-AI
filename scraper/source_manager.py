"""
刮削源管理器
提供源的分组、优先级、监控和管理功能
"""
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SourceCategory:
    """刮削源分类"""
    id: str
    name: str
    name_en: str
    description: str
    priority: int
    enabled: bool
    sources: List[str]
    tags: List[str]

    @classmethod
    def from_dict(cls, category_id: str, data: Dict) -> 'SourceCategory':
        """从字典创建分类"""
        return cls(
            id=category_id,
            name=data.get('name', ''),
            name_en=data.get('name_en', ''),
            description=data.get('description', ''),
            priority=data.get('priority', 10),
            enabled=data.get('enabled', True),
            sources=data.get('sources', []),
            tags=data.get('tags', [])
        )


class SourceGroupManager:
    """刮削源分组管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.categories: Dict[str, SourceCategory] = {}
        self.fallback_rules: Dict[str, Dict] = {}
        self.source_to_category: Dict[str, str] = {}
        
        if config_path:
            self.load_config(config_path)
    
    def load_config(self, config_path: str):
        """加载分组配置"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 加载分类
        for cat_id, cat_data in config.get('categories', {}).items():
            category = SourceCategory.from_dict(cat_id, cat_data)
            self.categories[cat_id] = category
            
            # 建立源到分类的映射
            for source in category.sources:
                self.source_to_category[source] = cat_id
        
        # 加载备用规则
        self.fallback_rules = config.get('fallback_rules', {})
    
    def get_all_sources(self, include_disabled: bool = False) -> List[str]:
        """获取所有源"""
        sources = []
        for category in sorted(self.categories.values(), 
                             key=lambda c: c.priority):
            if include_disabled or category.enabled:
                sources.extend(category.sources)
        return sources
    
    def get_sources_by_category(self, category_id: str) -> List[str]:
        """获取指定分类的源"""
        category = self.categories.get(category_id)
        if not category or not category.enabled:
            return []
        return category.sources
    
    def get_category_by_source(self, source: str) -> Optional[SourceCategory]:
        """根据源获取其分类"""
        cat_id = self.source_to_category.get(source)
        return self.categories.get(cat_id)
    
    def enable_category(self, category_id: str):
        """启用分类"""
        if category_id in self.categories:
            self.categories[category_id].enabled = True
    
    def disable_category(self, category_id: str):
        """禁用分类"""
        if category_id in self.categories:
            self.categories[category_id].enabled = False
    
    def enable_source(self, source: str):
        """启用单个源"""
        category = self.get_category_by_source(source)
        if category:
            category.enabled = True
    
    def disable_source(self, source: str):
        """禁用单个源"""
        category = self.get_category_by_source(source)
        if category:
            # 从分类中移除该源
            category.sources = [s for s in category.sources if s != source]
            # 更新映射
            del self.source_to_category[source]
    
    def get_fallback_sources(self, source: str) -> List[str]:
        """获取源的备用源列表"""
        category = self.get_category_by_source(source)
        if not category:
            return []
        
        # 获取该分类的备用规则
        fallback_config = self.fallback_rules.get(category.id, {})
        fallback_cats = fallback_config.get('fallback_to', [])
        
        # 获取备用分类的源
        fallbacks = []
        for cat_id in fallback_cats:
            if cat_id in self.categories and self.categories[cat_id].enabled:
                fallbacks.extend(self.categories[cat_id].sources)
        
        # 移除当前源本身
        fallbacks = [s for s in fallbacks if s != source]
        
        return fallbacks
    
    def search_sources(self, query: str) -> List[str]:
        """搜索源"""
        query_lower = query.lower()
        results = []
        
        for source in self.get_all_sources():
            category = self.get_category_by_source(source)
            if category:
                # 搜索源名称
                if query_lower in source.lower():
                    results.append(source)
                # 搜索分类名称
                elif query_lower in category.name.lower():
                    results.append(source)
                # 搜索标签
                elif any(query_lower in tag.lower() for tag in category.tags):
                    results.append(source)
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_sources = len(self.get_all_sources())
        enabled_categories = sum(1 for c in self.categories.values() if c.enabled)
        disabled_categories = sum(1 for c in self.categories.values() if not c.enabled)
        
        return {
            'total_sources': total_sources,
            'total_categories': len(self.categories),
            'enabled_categories': enabled_categories,
            'disabled_categories': disabled_categories,
            'categories': {
                cat_id: {
                    'name': cat.name,
                    'source_count': len(cat.sources) if cat.enabled else 0,
                    'enabled': cat.enabled
                }
                for cat_id, cat in self.categories.items()
            }
        }
    
    def export_config(self, output_path: str):
        """导出配置"""
        config = {
            'categories': {
                cat_id: {
                    'name': cat.name,
                    'name_en': cat.name_en,
                    'description': cat.description,
                    'priority': cat.priority,
                    'enabled': cat.enabled,
                    'sources': cat.sources,
                    'tags': cat.tags
                }
                for cat_id, cat in self.categories.items()
            },
            'fallback_rules': self.fallback_rules
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)


# 全局实例
_manager: Optional[SourceGroupManager] = None


def get_source_manager(config_path: Optional[str] = None) -> SourceGroupManager:
    """获取源管理器单例"""
    global _manager
    if _manager is None:
        _manager = SourceGroupManager(config_path)
    return _manager


def init_source_manager(config_path: str = 'source_groups.json'):
    """初始化源管理器"""
    global _manager
    if Path(config_path).exists():
        _manager = SourceGroupManager(config_path)
    else:
        _manager = SourceGroupManager()
    return _manager
