"""
刮削源评分系统
根据成功率、响应速度、数据完整性等指标对刮削源进行评分
"""

import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from datetime import datetime, timedelta


@dataclass
class ScrapeRecord:
    """刮取记录"""
    source: str
    number: str  # 视频番号
    success: bool
    duration: float  # 耗时（秒）
    timestamp: float
    error_type: Optional[str] = None
    completeness: float = 0.0  # 数据完整度 (0-100)
    fields_filled: int = 0  # 填充的字段数
    fields_total: int = 0  # 总字段数
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SourceRanking:
    """刮削源评分系统"""
    
    def __init__(self):
        self.records: List[ScrapeRecord] = []
        self.success_count: Dict[str, int] = defaultdict(int)
        self.fail_count: Dict[str, int] = defaultdict(int)
        self.total_duration: Dict[str, float] = defaultdict(float)
        self.field_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.last_update: Dict[str, float] = {}
    
    def record(self, record: ScrapeRecord):
        """记录一次刮取"""
        self.records.append(record)
        self.last_update[record.source] = time.time()
        
        if record.success:
            self.success_count[record.source] += 1
            self.total_duration[record.source] += record.duration
        else:
            self.fail_count[record.source] += 1
    
    def get_score(self, source: str, time_window_hours: int = 24) -> Dict:
        """获取刮削源评分详情
        
        Args:
            source: 刮削源名称
            time_window_hours: 时间窗口（小时），只统计最近这段时间的数据
        
        Returns:
            包含各项评分指标的字典
        """
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # 筛选时间窗口内的记录
        recent_records = [r for r in self.records 
                        if r.source == source and r.timestamp >= cutoff_time]
        
        if not recent_records:
            return {
                'source': source,
                'score': 50.0,  # 默认分数
                'status': 'no_data',
                'total_requests': 0,
                'success_rate': 0.0,
                'avg_duration': 0.0,
                'avg_completeness': 0.0,
                'field_coverage': {},
                'last_updated': None
            }
        
        success_records = [r for r in recent_records if r.success]
        fail_records = [r for r in recent_records if not r.success]
        
        total = len(recent_records)
        success_num = len(success_records)
        fail_num = len(fail_records)
        
        # 1. 成功率得分 (40%权重)
        success_rate = (success_num / total) * 100 if total > 0 else 0
        success_score = success_rate * 0.4
        
        # 2. 速度得分 (20%权重)
        if success_records:
            avg_duration = sum(r.duration for r in success_records) / success_num
            # 速度评分：越快越好，10秒内100分，30秒以上0分
            speed_score = max(0, (30 - avg_duration) / 30 * 100) * 0.2
        else:
            avg_duration = 0
            speed_score = 0
        
        # 3. 数据完整度得分 (30%权重)
        if success_records:
            avg_completeness = sum(r.completeness for r in success_records) / success_num
            completeness_score = avg_completeness * 0.3
        else:
            avg_completeness = 0
            completeness_score = 0
        
        # 4. 稳定性得分 (10%权重)
        # 失败率越高，稳定性越低
        fail_rate = (fail_num / total) * 100 if total > 0 else 0
        stability_score = max(0, (100 - fail_rate)) * 0.1
        
        # 总分
        total_score = success_score + speed_score + completeness_score + stability_score
        
        # 字段覆盖率
        field_coverage = {}
        all_fields = set()
        for r in success_records:
            all_fields.update(self.field_stats[source].keys())
        
        for field_name in all_fields:
            filled_count = sum(1 for r in success_records 
                             if self.field_stats[source][field_name] > 0)
            coverage = (filled_count / success_num * 100) if success_num > 0 else 0
            field_coverage[field_name] = round(coverage, 1)
        
        # 状态判断
        if success_rate >= 80:
            status = 'excellent'
        elif success_rate >= 60:
            status = 'good'
        elif success_rate >= 40:
            status = 'fair'
        elif success_rate >= 20:
            status = 'poor'
        else:
            status = 'critical'
        
        return {
            'source': source,
            'score': round(total_score, 2),
            'status': status,
            'total_requests': total,
            'success_count': success_num,
            'fail_count': fail_num,
            'success_rate': round(success_rate, 1),
            'avg_duration': round(avg_duration, 2),
            'avg_completeness': round(avg_completeness, 1),
            'stability': round(100 - fail_rate, 1),
            'field_coverage': field_coverage,
            'last_updated': datetime.fromtimestamp(max(r.timestamp for r in recent_records)).isoformat()
        }
    
    def get_all_scores(self, time_window_hours: int = 24) -> List[Dict]:
        """获取所有刮削源的评分"""
        sources = set(r.source for r in self.records)
        scores = []
        
        for source in sources:
            score_data = self.get_score(source, time_window_hours)
            scores.append(score_data)
        
        # 按分数排序
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores
    
    def get_recommendation(self, number: str = None, count: int = 3) -> List[str]:
        """获取推荐的刮削源
        
        Args:
            number: 视频番号（可选，用于特定番号优化）
            count: 返回数量
        
        Returns:
            推荐刮削源列表（按优先级排序）
        """
        scores = self.get_all_scores()
        
        # 根据番号类型调整权重
        if number:
            prefix = number.split('-')[0].upper() if '-' in number else ''
            
            # 针对特定番号类型提升相关刮削源的分数
            for score in scores:
                source = score['source']
                
                # FC2 番号优先使用 FC2 专用刮削源
                if 'FC2' in prefix.upper():
                    if 'fc2' in source.lower():
                        score['score'] *= 1.2
                
                # 无码番号优先使用 kin8 等
                elif prefix in ['KIN', '10MU']:
                    if 'kin8' in source.lower():
                        score['score'] *= 1.2
                
                # 国产番号优先使用国产刮削源
                elif prefix in ['MDOU', 'GUO']:
                    if 'hdouban' in source.lower() or 'madou' in source.lower():
                        score['score'] *= 1.2
        
        # 重新排序
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # 只返回刮削源名称
        return [s['source'] for s in scores[:count] if s['status'] != 'no_data']
    
    def update_field_stats(self, source: str, fields: Dict[str, any]):
        """更新字段统计"""
        for field_name, value in fields.items():
            if value:  # 只统计有值的字段
                self.field_stats[source][field_name] += 1
    
    def get_source_health(self, source: str) -> Dict:
        """获取刮削源健康状态"""
        recent_records = [r for r in self.records if r.source == source][-10:]
        
        if not recent_records:
            return {'health': 'unknown', 'message': '暂无数据'}
        
        recent_success_rate = sum(1 for r in recent_records if r.success) / len(recent_records)
        
        # 错误类型统计
        error_types = defaultdict(int)
        for r in recent_records:
            if not r.success and r.error_type:
                error_types[r.error_type] += 1
        
        if recent_success_rate >= 0.9:
            health = 'healthy'
            message = '运行良好'
        elif recent_success_rate >= 0.7:
            health = 'degraded'
            message = '性能下降'
        elif recent_success_rate >= 0.5:
            health = 'unhealthy'
            message = '需要关注'
        else:
            health = 'critical'
            message = '可能存在严重问题'
        
        return {
            'health': health,
            'message': message,
            'recent_success_rate': round(recent_success_rate * 100, 1),
            'recent_requests': len(recent_records),
            'error_types': dict(error_types)
        }


class QualityEvaluator:
    """数据质量评估器"""
    
    def __init__(self):
        self.quality_weights = {
            'title': 20,  # 标题最重要
            'number': 15,  # 番号
            'actors': 15,  # 演员
            'studio': 10,  # 片商
            'release': 10,  # 发售日期
            'runtime': 5,   # 时长
            'director': 5,  # 导演
            'series': 5,   # 系列
            'tags': 5,     # 标签
            'publisher': 5, # 发行商
            'outline': 5,  # 简介
            'thumb': 0,    # 封面（不计入质量分）
            'poster': 0,    # 海报
            'trailer': 0,  # 预告片
        }
    
    def evaluate(self, data: Dict) -> Tuple[float, Dict]:
        """评估数据质量
        
        Args:
            data: 刮取的数据
        
        Returns:
            (质量分数, 详细评分字典)
        """
        total_weight = sum(v for k, v in self.quality_weights.items() if k in data)
        max_weight = sum(self.quality_weights.values())
        
        score = (total_weight / max_weight * 100) if max_weight > 0 else 0
        
        details = {}
        filled_weight = 0
        for field, weight in self.quality_weights.items():
            if field in data and data[field]:
                details[field] = {
                    'filled': True,
                    'weight': weight,
                    'value_preview': str(data[field])[:50] + '...' if len(str(data[field])) > 50 else str(data[field])
                }
                filled_weight += weight
            else:
                details[field] = {
                    'filled': False,
                    'weight': weight,
                    'value_preview': None
                }
        
        return round(score, 2), {
            'total_score': round(score, 2),
            'filled_weight': filled_weight,
            'max_weight': max_weight,
            'field_details': details,
            'recommendations': self._get_recommendations(details)
        }
    
    def _get_recommendations(self, details: Dict) -> List[str]:
        """获取改进建议"""
        recommendations = []
        
        missing_important = []
        for field, info in details.items():
            if not info['filled'] and info['weight'] >= 10:
                missing_important.append(field)
        
        if missing_important:
            recommendations.append(f"建议补充重要字段: {', '.join(missing_important)}")
        
        return recommendations


# 全局实例
_global_ranking = SourceRanking()


def record_scrape(source: str, number: str, success: bool, duration: float,
                  error_type: str = None, fields: Dict = None, fields_total: int = 0):
    """便捷的记录函数"""
    completeness = 0
    fields_filled = 0
    
    if fields:
        fields_filled = sum(1 for v in fields.values() if v)
        if fields_total > 0:
            completeness = (fields_filled / fields_total) * 100
    
    record = ScrapeRecord(
        source=source,
        number=number,
        success=success,
        duration=duration,
        timestamp=time.time(),
        error_type=error_type,
        completeness=completeness,
        fields_filled=fields_filled,
        fields_total=fields_total
    )
    
    _global_ranking.record(record)
    
    if fields:
        _global_ranking.update_field_stats(source, fields)


def get_source_score(source: str, time_window_hours: int = 24) -> Dict:
    """获取刮削源评分"""
    return _global_ranking.get_score(source, time_window_hours)


def get_all_scores(time_window_hours: int = 24) -> List[Dict]:
    """获取所有刮削源评分"""
    return _global_ranking.get_all_scores(time_window_hours)


def get_recommended_sources(number: str = None, count: int = 3) -> List[str]:
    """获取推荐的刮削源"""
    return _global_ranking.get_recommendation(number, count)


def evaluate_quality(data: Dict) -> Tuple[float, Dict]:
    """评估数据质量"""
    evaluator = QualityEvaluator()
    return evaluator.evaluate(data)


# 测试代码
if __name__ == "__main__":
    # 模拟一些数据
    test_data = {
        'title': 'Test Movie',
        'number': 'ABC-123',
        'actors': ['Actor 1', 'Actor 2'],
        'studio': 'Test Studio',
        'release': '2024-01-01',
        'runtime': '120',
    }
    
    # 评估质量
    evaluator = QualityEvaluator()
    score, details = evaluator.evaluate(test_data)
    
    print("=" * 60)
    print("数据质量评估")
    print("=" * 60)
    print(f"总得分: {score}")
    print("\n字段详情:")
    for field, info in details['field_details'].items():
        status = "✓" if info['filled'] else "✗"
        print(f"  {status} {field}: {info['weight']}分")
    
    print("\n建议:")
    for rec in details['recommendations']:
        print(f"  - {rec}")
