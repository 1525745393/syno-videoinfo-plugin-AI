"""
配置管理模块
支持从文件、环境变量和默认值读取配置
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ScraperConfig:
    """刮削器配置"""
    # 网络配置
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    max_concurrent: int = 5
    doh_enabled: bool = False

    # 刮削配置
    default_language: str = "chs"
    scrape_timeout: int = 60
    max_results: int = 5

    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600
    cache_dir: str = ".cache"

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # 质量配置
    min_success_rate: float = 0.5
    min_completeness: float = 0.6

    # 刮削源优先级
    source_priorities: Dict[str, int] = field(default_factory=dict)

    # 禁用的刮削源
    disabled_sources: list = field(default_factory=list)


class ConfigManager:
    """配置管理器"""

    DEFAULT_CONFIG = {
        "scraper": {
            "timeout": 30,
            "max_retries": 3,
            "retry_delay": 1.0,
            "max_concurrent": 5,
            "doh_enabled": False,
            "default_language": "chs",
            "scrape_timeout": 60,
            "max_results": 5,
            "cache_enabled": True,
            "cache_ttl": 3600,
            "cache_dir": ".cache",
            "log_level": "INFO",
            "log_file": None,
            "min_success_rate": 0.5,
            "min_completeness": 0.6,
            "source_priorities": {},
            "disabled_sources": []
        },
        "logging": {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "INFO"
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "detailed",
                    "level": "DEBUG",
                    "filename": "scraper.log",
                    "encoding": "utf-8"
                }
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"]
            }
        },
        "quality": {
            "field_weights": {
                "title": 20,
                "number": 15,
                "actors": 15,
                "studio": 10,
                "release": 10,
                "runtime": 5,
                "tags": 5,
                "outline": 5
            },
            "min_quality_score": 60.0,
            "required_fields": ["title", "number"],
            "important_fields": ["actors", "studio", "release"]
        },
        "ranking": {
            "success_weight": 0.4,
            "speed_weight": 0.2,
            "quality_weight": 0.3,
            "stability_weight": 0.1,
            "time_window_hours": 24
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else self._find_config_file()
        self.config = self._load_config()
        self._setup_logging()

    def _find_config_file(self) -> Path:
        """查找配置文件"""
        search_paths = [
            Path.cwd() / "config.json",
            Path.cwd() / "config.yaml",
            Path.cwd() / "config.yml",
            Path.home() / ".syno-videoinfo" / "config.json",
            Path.cwd() / "scraper" / "config.json"
        ]

        for path in search_paths:
            if path.exists():
                return path

        return Path.cwd() / "config.json"

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        config = json.loads(json.dumps(self.DEFAULT_CONFIG))

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    if self.config_path.suffix in ['.yaml', '.yml']:
                        import yaml
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)

                self._merge_config(config, user_config)
            except Exception as e:
                logging.warning(f"Failed to load config file {self.config_path}: {e}")

        config = self._load_env_vars(config)

        return config

    def _merge_config(self, base: Dict, overlay: Dict):
        """合并配置"""
        for key, value in overlay.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _load_env_vars(self, config: Dict) -> Dict:
        """从环境变量加载配置"""
        env_prefix = "SCRAPER_"

        for key in os.environ:
            if key.startswith(env_prefix):
                parts = key[len(env_prefix):].lower().split('__')
                value = os.environ[key]

                if value.lower() in ('true', 'yes', '1'):
                    value = True
                elif value.lower() in ('false', 'no', '0'):
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif '.' in value and value.replace('.', '').isdigit():
                    value = float(value)

                self._set_nested_value(config, parts, value)

        return config

    def _set_nested_value(self, config: Dict, keys: list, value: Any):
        """设置嵌套配置值"""
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        current = self.config

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default

        return current

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        current = self.config

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def get_scraper_config(self) -> ScraperConfig:
        """获取刮削器配置对象"""
        scraper_data = self.config.get('scraper', {})
        return ScraperConfig(**scraper_data)

    def save(self, path: Optional[str] = None):
        """保存配置"""
        save_path = Path(path) if path else self.config_path

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})

        try:
            logging.config.dictConfig(log_config)
        except Exception:
            logging.basicConfig(
                level=getattr(logging, self.get('scraper.log_level', 'INFO')),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )


# 全局配置实例
_config_manager: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """获取全局配置实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def reload_config():
    """重新加载配置"""
    global _config_manager
    _config_manager = None


def create_default_config(path: str = "config.json"):
    """创建默认配置文件"""
    config = ConfigManager.DEFAULT_CONFIG
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return path
