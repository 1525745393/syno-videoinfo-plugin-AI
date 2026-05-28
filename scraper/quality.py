"""
数据质量评估模块
用于评估刮取数据的质量和完整性
"""

import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QualityScore:
    """质量评分结果"""
    overall: float  # 总分 (0-100)
    title: float  # 标题得分
    number: float  # 番号得分
    actors: float  # 演员得分
    studio: float  # 片商得分
    release: float  # 发售日期得分
    runtime: float  # 时长得分
    tags: float  # 标签得分
    outline: float  # 简介得分
    thumb: bool  # 封面是否存在
    poster: bool  # 海报是否存在
    trailer: bool  # 预告片是否存在
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'overall': self.overall,
            'title': self.title,
            'number': self.number,
            'actors': self.actors,
            'studio': self.studio,
            'release': self.release,
            'runtime': self.runtime,
            'tags': self.tags,
            'outline': self.outline,
            'thumb': self.thumb,
            'poster': self.poster,
            'trailer': self.trailer,
        }


class DataQualityChecker:
    """数据质量检查器"""
    
    # 字段权重配置
    FIELD_WEIGHTS = {
        'title': 20,
        'number': 15,
        'actors': 15,
        'studio': 10,
        'release': 10,
        'runtime': 5,
        'tags': 5,
        'outline': 5,
        'director': 5,
        'series': 5,
        'publisher': 5,
    }
    
    # 番号格式正则
    NUMBER_PATTERNS = [
        r'^[A-Z]{2,10}-\d{3,6}$',  # 标准番号: ABC-123
        r'^FC2-PPV-\d+$',  # FC2 PPV: FC2-PPV-123456
        r'^\d{4}-\d{2}-\d{2}$',  # 日期格式
        r'^[A-Z]+-\d+$',  # 字母+数字
    ]
    
    # 日期格式
    DATE_PATTERNS = [
        r'^\d{4}-\d{2}-\d{2}$',  # 2024-01-01
        r'^\d{4}/\d{2}/\d{2}$',  # 2024/01/01
        r'^\d{4}年\d{1,2}月\d{1,2}日$',  # 2024年1月1日
    ]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_all(self, data: Dict) -> Tuple[QualityScore, List[str], List[str]]:
        """检查所有字段的质量
        
        Args:
            data: 刮取的数据字典
        
        Returns:
            (质量评分, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []
        
        # 检查各个字段
        title_score = self._check_title(data.get('title'))
        number_score = self._check_number(data.get('number'))
        actors_score = self._check_actors(data.get('actors'))
        studio_score = self._check_studio(data.get('studio'))
        release_score = self._check_release(data.get('release'))
        runtime_score = self._check_runtime(data.get('runtime'))
        tags_score = self._check_tags(data.get('tags'))
        outline_score = self._check_outline(data.get('outline'))
        
        # 计算总分
        total_weight = sum(self.FIELD_WEIGHTS.values())
        total_score = (
            title_score * self.FIELD_WEIGHTS['title'] +
            number_score * self.FIELD_WEIGHTS['number'] +
            actors_score * self.FIELD_WEIGHTS['actors'] +
            studio_score * self.FIELD_WEIGHTS['studio'] +
            release_score * self.FIELD_WEIGHTS['release'] +
            runtime_score * self.FIELD_WEIGHTS['runtime'] +
            tags_score * self.FIELD_WEIGHTS['tags'] +
            outline_score * self.FIELD_WEIGHTS['outline']
        ) / total_weight * 100
        
        score = QualityScore(
            overall=round(total_score, 2),
            title=title_score,
            number=number_score,
            actors=actors_score,
            studio=studio_score,
            release=release_score,
            runtime=runtime_score,
            tags=tags_score,
            outline=outline_score,
            thumb=bool(data.get('thumb')),
            poster=bool(data.get('poster')),
            trailer=bool(data.get('trailer')),
        )
        
        return score, self.errors, self.warnings
    
    def _check_title(self, title: Any) -> float:
        """检查标题"""
        if not title:
            self.errors.append("标题缺失")
            return 0
        
        title_str = str(title).strip()
        
        if len(title_str) < 2:
            self.errors.append("标题过短")
            return 20
        
        if len(title_str) > 200:
            self.warnings.append("标题过长")
            return 80
        
        # 检查是否包含乱码
        if self._has_garbled_text(title_str):
            self.warnings.append("标题可能包含乱码")
            return 70
        
        return 100
    
    def _check_number(self, number: Any) -> float:
        """检查番号"""
        if not number:
            self.errors.append("番号缺失")
            return 0
        
        number_str = str(number).strip()
        
        # 检查格式
        valid_format = any(re.match(pattern, number_str) for pattern in self.NUMBER_PATTERNS)
        
        if not valid_format:
            self.warnings.append(f"番号格式可能不正确: {number_str}")
            return 70
        
        return 100
    
    def _check_actors(self, actors: Any) -> float:
        """检查演员"""
        if not actors:
            self.warnings.append("演员信息缺失")
            return 0
        
        # 支持字符串和列表
        if isinstance(actors, str):
            actor_list = [a.strip() for a in actors.split(',') if a.strip()]
        elif isinstance(actors, list):
            actor_list = [a for a in actors if a]
        else:
            actor_list = []
        
        if not actor_list:
            self.warnings.append("演员列表为空")
            return 0
        
        # 检查演员名称长度
        for actor in actor_list:
            if len(actor) < 2:
                self.warnings.append(f"演员名称可能不正确: {actor}")
        
        return 100
    
    def _check_studio(self, studio: Any) -> float:
        """检查片商"""
        if not studio:
            self.warnings.append("片商信息缺失")
            return 0
        
        studio_str = str(studio).strip()
        
        if len(studio_str) < 2:
            self.warnings.append("片商名称过短")
            return 50
        
        return 100
    
    def _check_release(self, release: Any) -> float:
        """检查发售日期"""
        if not release:
            self.warnings.append("发售日期缺失")
            return 0
        
        release_str = str(release).strip()
        
        # 检查格式
        valid_format = any(re.search(pattern, release_str) for pattern in self.DATE_PATTERNS)
        
        if not valid_format:
            self.warnings.append(f"日期格式可能不正确: {release_str}")
            return 70
        
        # 尝试解析日期
        try:
            if '-' in release_str:
                date = datetime.strptime(release_str[:10], '%Y-%m-%d')
            elif '/' in release_str:
                date = datetime.strptime(release_str[:10], '%Y/%m/%d')
            else:
                return 100
            
            # 检查日期是否合理（1900-2100之间）
            if date.year < 1900 or date.year > 2100:
                self.warnings.append(f"日期可能不正确: {release_str}")
                return 70
        except ValueError:
            self.warnings.append(f"日期解析失败: {release_str}")
            return 50
        
        return 100
    
    def _check_runtime(self, runtime: Any) -> float:
        """检查时长"""
        if not runtime:
            return 50  # 时长可选
        
        runtime_str = str(runtime).strip()
        
        # 提取数字
        match = re.search(r'\d+', runtime_str)
        if not match:
            self.warnings.append(f"时长格式不正确: {runtime_str}")
            return 50
        
        minutes = int(match.group())
        
        # 检查时长是否合理（1分钟-24小时）
        if minutes < 1 or minutes > 1440:
            self.warnings.append(f"时长可能不正确: {runtime_str}")
            return 70
        
        return 100
    
    def _check_tags(self, tags: Any) -> float:
        """检查标签"""
        if not tags:
            return 50  # 标签可选
        
        # 支持字符串和列表
        if isinstance(tags, str):
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        elif isinstance(tags, list):
            tag_list = [t for t in tags if t]
        else:
            tag_list = []
        
        if not tag_list:
            return 50
        
        return 100
    
    def _check_outline(self, outline: Any) -> float:
        """检查简介"""
        if not outline:
            return 50  # 简介可选
        
        outline_str = str(outline).strip()
        
        if len(outline_str) < 10:
            self.warnings.append("简介过短")
            return 30
        
        if len(outline_str) > 5000:
            self.warnings.append("简介过长")
            return 80
        
        # 检查是否包含乱码
        if self._has_garbled_text(outline_str):
            self.warnings.append("简介可能包含乱码")
            return 60
        
        return 100
    
    def _has_garbled_text(self, text: str) -> bool:
        """检查是否包含乱码"""
        # 检查是否包含常见的乱码字符
        garbled_patterns = [
            r'[\u0000-\u001F]',  # 控制字符
            r'�',  # 替换字符
            r'□',  # 方块字符
        ]
        
        for pattern in garbled_patterns:
            if re.search(pattern, text):
                return True
        
        return False


class DataCompletenessChecker:
    """数据完整性检查器"""
    
    # 必需字段
    REQUIRED_FIELDS = ['title', 'number']
    
    # 重要字段
    IMPORTANT_FIELDS = ['actors', 'studio', 'release']
    
    # 可选字段
    OPTIONAL_FIELDS = ['tags', 'outline', 'runtime', 'director', 'series', 'publisher']
    
    # 媒体字段
    MEDIA_FIELDS = ['thumb', 'poster', 'trailer', 'extrafanart']
    
    def check_completeness(self, data: Dict) -> Dict:
        """检查数据完整性
        
        Returns:
            包含完整性报告的字典
        """
        all_fields = self.REQUIRED_FIELDS + self.IMPORTANT_FIELDS + self.OPTIONAL_FIELDS + self.MEDIA_FIELDS
        
        filled_fields = {field: bool(data.get(field)) for field in all_fields}
        
        # 计算各类型的完整度
        required_filled = sum(1 for f in self.REQUIRED_FIELDS if filled_fields[f])
        important_filled = sum(1 for f in self.IMPORTANT_FIELDS if filled_fields[f])
        optional_filled = sum(1 for f in self.OPTIONAL_FIELDS if filled_fields[f])
        media_filled = sum(1 for f in self.MEDIA_FIELDS if filled_fields[f])
        
        return {
            'is_complete': required_filled == len(self.REQUIRED_FIELDS),
            'required_score': required_filled / len(self.REQUIRED_FIELDS) * 100,
            'important_score': important_filled / len(self.IMPORTANT_FIELDS) * 100,
            'optional_score': optional_filled / len(self.OPTIONAL_FIELDS) * 100 if self.OPTIONAL_FIELDS else 100,
            'media_score': media_filled / len(self.MEDIA_FIELDS) * 100,
            'overall_score': (
                required_filled / len(self.REQUIRED_FIELDS) * 40 +
                important_filled / len(self.IMPORTANT_FIELDS) * 30 +
                optional_filled / len(self.OPTIONAL_FIELDS) * 20 if self.OPTIONAL_FIELDS else 0 +
                media_filled / len(self.MEDIA_FIELDS) * 10
            ),
            'filled_fields': [f for f, filled in filled_fields.items() if filled],
            'missing_fields': [f for f, filled in filled_fields.items() if not filled],
            'field_details': filled_fields,
        }


# 便捷函数
def check_quality(data: Dict) -> Tuple[QualityScore, List[str], List[str]]:
    """检查数据质量"""
    checker = DataQualityChecker()
    return checker.check_all(data)


def check_completeness(data: Dict) -> Dict:
    """检查数据完整性"""
    checker = DataCompletenessChecker()
    return checker.check_completeness(data)


def generate_quality_report(data: Dict) -> str:
    """生成质量报告"""
    quality_score, errors, warnings = check_quality(data)
    completeness = check_completeness(data)
    
    lines = [
        "=" * 60,
        "数据质量报告",
        "=" * 60,
        "",
        f"总分: {quality_score.overall}/100",
        "",
        "质量评分:",
        f"  标题: {quality_score.title}/100",
        f"  番号: {quality_score.number}/100",
        f"  演员: {quality_score.actors}/100",
        f"  片商: {quality_score.studio}/100",
        f"  日期: {quality_score.release}/100",
        f"  时长: {quality_score.runtime}/100",
        f"  标签: {quality_score.tags}/100",
        f"  简介: {quality_score.outline}/100",
        "",
        "媒体文件:",
        f"  封面: {'✓' if quality_score.thumb else '✗'}",
        f"  海报: {'✓' if quality_score.poster else '✗'}",
        f"  预告片: {'✓' if quality_score.trailer else '✗'}",
        "",
        "完整性:",
        f"  必需字段: {completeness['required_score']:.0f}%",
        f"  重要字段: {completeness['important_score']:.0f}%",
        f"  可选字段: {completeness['optional_score']:.0f}%",
        "",
    ]
    
    if errors:
        lines.extend([
            "错误:",
            *[f"  - {e}" for e in errors],
        ])
    
    if warnings:
        lines.extend([
            "警告:",
            *[f"  - {w}" for w in warnings],
        ])
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


# 测试代码
if __name__ == "__main__":
    # 测试数据
    test_data = {
        'title': 'Test Movie Title',
        'number': 'ABC-123',
        'actors': ['Actor 1', 'Actor 2'],
        'studio': 'Test Studio',
        'release': '2024-01-01',
        'runtime': '120',
        'tags': ['tag1', 'tag2'],
        'outline': 'This is a test outline.',
        'thumb': 'http://example.com/thumb.jpg',
        'poster': 'http://example.com/poster.jpg',
    }
    
    report = generate_quality_report(test_data)
    print(report)
