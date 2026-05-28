"""
性能优化模块
提供性能监控、缓存、连接池等功能
"""
import time
import hashlib
import asyncio
import functools
from contextlib import contextmanager
from typing import Dict, Any, Optional, Callable, Union
from collections import OrderedDict
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class PerformanceStats:
    """性能统计数据"""
    requests: int = 0
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0

    def update(self, success: bool, elapsed: float):
        """更新统计"""
        self.requests += 1
        self.total_time += elapsed

        if success:
            self.successes += 1
        else:
            self.failures += 1

        if elapsed < self.min_time:
            self.min_time = elapsed
        if elapsed > self.max_time:
            self.max_time = elapsed

        self.avg_time = self.total_time / self.requests if self.requests > 0 else 0.0

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.requests == 0:
            return 0.0
        return self.successes / self.requests


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.source_stats: Dict[str, PerformanceStats] = {}
        self.global_stats = PerformanceStats()
        self._lock = Lock()

    def measure(self, source: str, success: bool, elapsed: float):
        """测量并记录一次操作"""
        with self._lock:
            if source not in self.source_stats:
                self.source_stats[source] = PerformanceStats()

            self.source_stats[source].update(success, elapsed)
            self.global_stats.update(success, elapsed)

    def get_source_stats(self, source: str) -> Optional[PerformanceStats]:
        """获取刮削源统计"""
        return self.source_stats.get(source)

    def get_all_stats(self) -> Dict[str, PerformanceStats]:
        """获取所有统计"""
        return self.source_stats.copy()

    def get_global_stats(self) -> PerformanceStats:
        """获取全局统计"""
        return self.global_stats

    def reset(self):
        """重置统计"""
        with self._lock:
            self.source_stats.clear()
            self.global_stats = PerformanceStats()

    def report(self) -> Dict[str, Any]:
        """生成性能报告"""
        with self._lock:
            report = {
                'global': {
                    'requests': self.global_stats.requests,
                    'success_rate': self.global_stats.get_success_rate(),
                    'avg_time': self.global_stats.avg_time,
                    'min_time': self.global_stats.min_time if self.global_stats.requests > 0 else 0,
                    'max_time': self.global_stats.max_time,
                    'total_time': self.global_stats.total_time
                },
                'sources': {}
            }

            for source, stats in self.source_stats.items():
                report['sources'][source] = {
                    'requests': stats.requests,
                    'success_rate': stats.get_success_rate(),
                    'avg_time': stats.avg_time,
                    'min_time': stats.min_time if stats.requests > 0 else 0,
                    'max_time': stats.max_time,
                    'total_time': stats.total_time
                }

            return report


class LRUCache:
    """LRU缓存实现"""

    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._lock = Lock()

    def _make_key(self, *args, **kwargs) -> str:
        """生成缓存键"""
        key = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self.cache:
                return None

            value, expiry = self.cache[key]
            if time.time() > expiry:
                del self.cache[key]
                return None

            self.cache.move_to_end(key)
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        with self._lock:
            if len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)

            expiry = time.time() + (ttl or self.ttl)
            self.cache[key] = (value, expiry)

    def clear(self):
        """清空缓存"""
        with self._lock:
            self.cache.clear()

    def clear_expired(self):
        """清理过期缓存"""
        with self._lock:
            now = time.time()
            expired_keys = [
                key for key, (_, expiry) in self.cache.items()
                if now > expiry
            ]
            for key in expired_keys:
                del self.cache[key]


def cache_result(cache: LRUCache, ttl: Optional[int] = None):
    """缓存装饰器"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache._make_key(*args, **kwargs)

            cached = cache.get(key)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator


def async_cache_result(cache: LRUCache, ttl: Optional[int] = None):
    """异步缓存装饰器"""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = cache._make_key(*args, **kwargs)

            cached = cache.get(key)
            if cached is not None:
                return cached

            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator


@contextmanager
def measure_time(description: str = "operation", logger=None):
    """测量代码执行时间的上下文管理器"""
    start = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start
        if logger:
            logger.info(f"{description} took {elapsed:.3f}s")
        else:
            print(f"{description} took {elapsed:.3f}s")


class RateLimiter:
    """速率限制器"""

    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self._lock = Lock()

    def acquire(self) -> bool:
        """获取执行权限"""
        with self._lock:
            now = time.time()

            self.calls = [t for t in self.calls if now - t < self.period]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True

            return False

    async def acquire_async(self) -> bool:
        """异步版获取执行权限"""
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.acquire)

    def wait_for_slot(self):
        """等待直到有可用槽位"""
        import time
        while not self.acquire():
            if self.calls:
                wait_time = max(0, self.period - (time.time() - self.calls[0]))
                if wait_time > 0:
                    time.sleep(wait_time)


class ConnectionPool:
    """简单的连接池实现（用于HTTP连接等）"""

    def __init__(self, maxsize: int = 20):
        self.maxsize = maxsize
        self._pool = []
        self._lock = Lock()
        self._semaphore = asyncio.Semaphore(maxsize) if maxsize else None

    def acquire(self):
        """获取连接"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
        return None

    def release(self, conn):
        """释放连接"""
        with self._lock:
            if len(self._pool) < self.maxsize:
                self._pool.append(conn)

    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            self._pool.clear()


# 全局性能监控实例
_performance_monitor: Optional[PerformanceMonitor] = None
_default_cache: Optional[LRUCache] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def get_default_cache() -> LRUCache:
    """获取默认缓存"""
    global _default_cache
    if _default_cache is None:
        _default_cache = LRUCache(maxsize=1000, ttl=3600)
    return _default_cache


def monitor(source: str):
    """性能监控装饰器"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception:
                success = False
                raise
            finally:
                elapsed = time.time() - start
                monitor.measure(source, success, elapsed)

        return wrapper
    return decorator
