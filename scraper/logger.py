"""
日志配置模块
提供灵活的日志配置和管理功能
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class LogManager:
    """日志管理器"""

    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[35m',
        'RESET': '\033[0m'
    }

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.root_logger = logging.getLogger()
        self._setup_default_logger()

    def _setup_default_logger(self):
        """设置默认日志"""
        log_level = self.config.get('scraper', {}).get('log_level', 'INFO')
        level = getattr(logging, log_level, logging.INFO)

        self.root_logger.setLevel(level)

        if not self.root_logger.handlers:
            self.add_console_handler()

    def add_console_handler(self, level: Optional[str] = None,
                           formatter: Optional[str] = None):
        """添加控制台日志处理器"""
        handler = logging.StreamHandler()

        if sys.stdout.isatty():
            formatter_cls = ColoredFormatter
        else:
            formatter_cls = logging.Formatter

        fmt = formatter or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        handler.setFormatter(formatter_cls(fmt))

        if level:
            handler.setLevel(getattr(logging, level, logging.INFO))

        self.root_logger.addHandler(handler)
        return handler

    def add_file_handler(self, filename: str,
                        level: Optional[str] = None,
                        max_bytes: int = 10 * 1024 * 1024,
                        backup_count: int = 5,
                        encoding: str = 'utf-8'):
        """添加文件日志处理器（支持滚动）"""
        handler = logging.handlers.RotatingFileHandler(
            filename,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)

        if level:
            handler.setLevel(getattr(logging, level, logging.DEBUG))

        self.root_logger.addHandler(handler)
        return handler

    def add_timed_file_handler(self, filename: str,
                              when: str = 'midnight',
                              interval: int = 1,
                              backup_count: int = 7,
                              level: Optional[str] = None,
                              encoding: str = 'utf-8'):
        """添加时间滚动文件日志处理器"""
        handler = logging.handlers.TimedRotatingFileHandler(
            filename,
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding=encoding
        )

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
        )
        handler.setFormatter(formatter)

        if level:
            handler.setLevel(getattr(logging, level, logging.DEBUG))

        self.root_logger.addHandler(handler)
        return handler

    def setup_from_config(self, logging_config: Dict[str, Any]):
        """从配置字典设置日志"""
        try:
            logging.config.dictConfig(logging_config)
        except Exception as e:
            self.root_logger.error(f"Failed to setup logging from config: {e}")
            self._setup_default_logger()

    def set_level(self, level: str):
        """设置日志级别"""
        self.root_logger.setLevel(getattr(logging, level, logging.INFO))

    def get_logger(self, name: str) -> logging.Logger:
        """获取命名日志记录器"""
        return logging.getLogger(name)

    def get_scraper_logger(self) -> logging.Logger:
        """获取刮削器专用日志记录器"""
        return logging.getLogger("scraper")


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    def format(self, record):
        if record.levelname in LogManager.COLORS:
            color = LogManager.COLORS[record.levelname]
            reset = LogManager.COLORS['RESET']

            record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


class LogBuffer:
    """日志缓冲区，用于内存中的日志收集"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.buffer = []

    def add(self, level: str, message: str, extra: Optional[Dict] = None):
        """添加日志条目"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'extra': extra or {}
        }

        self.buffer.append(entry)

        if len(self.buffer) > self.max_size:
            self.buffer.pop(0)

    def get_buffer(self) -> list:
        """获取缓冲区内容"""
        return self.buffer.copy()

    def clear(self):
        """清空缓冲区"""
        self.buffer = []

    def export_to_file(self, filename: str):
        """导出缓冲区到文件"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.buffer, f, indent=2, ensure_ascii=False)


# 全局日志实例
_log_manager: Optional[LogManager] = None


def get_log_manager(config: Optional[Dict] = None) -> LogManager:
    """获取全局日志管理器"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager(config)
    return _log_manager


def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器"""
    if name:
        return logging.getLogger(name)
    return logging.getLogger()


def setup_logging(config: Optional[Dict] = None):
    """设置日志系统"""
    manager = get_log_manager(config)

    if config and 'logging' in config:
        manager.setup_from_config(config['logging'])
    else:
        log_file = config.get('scraper', {}).get('log_file') if config else None
        if log_file:
            manager.add_file_handler(log_file)


def log_exception(logger: logging.Logger, message: str,
                  exc_info: bool = True):
    """记录异常的便捷函数"""
    logger.exception(message)
