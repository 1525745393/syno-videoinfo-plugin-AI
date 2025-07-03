"""优化版HTTP请求模块 - 性能提升版本"""
import json
import logging
import hashlib
import time
import urllib
import urllib.parse
import urllib.request
import pickle
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any, Dict, Optional
from functools import lru_cache
import threading

from scraper.exceptions import RequestSendError
from scraper.functions import Args, Func

_logger = logging.getLogger(__name__)

# 优化的缓存配置
_basedir = Path(__file__).resolve().parent
_cache_expire = 86400  # 24小时
_memory_cache_size = 1000

class OptimizedCacheManager:
    """优化的两级缓存管理器"""
    
    def __init__(self, cache_dir: Path, memory_size: int = _memory_cache_size):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache: Dict[str, tuple] = {}
        self._memory_size = memory_size
        self._lock = threading.RLock()
        self._access_times: Dict[str, float] = {}
    
    def _get_cache_key(self, url: str, body: Optional[str] = None) -> str:
        """生成安全的缓存键"""
        content = f"{url}:{body or ''}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cleanup_memory_cache(self):
        """清理内存缓存中的过期项"""
        if len(self._memory_cache) >= self._memory_size:
            # 删除最旧的20%的条目
            sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
            to_remove = sorted_items[:len(sorted_items) // 5]
            for key, _ in to_remove:
                self._memory_cache.pop(key, None)
                self._access_times.pop(key, None)
    
    def get(self, url: str, body: Optional[str] = None) -> Optional[str]:
        """获取缓存数据"""
        cache_key = self._get_cache_key(url, body)
        current_time = time.time()
        
        with self._lock:
            # 检查内存缓存
            if cache_key in self._memory_cache:
                data, timestamp = self._memory_cache[cache_key]
                if current_time - timestamp < _cache_expire:
                    self._access_times[cache_key] = current_time
                    _logger.debug(f"Cache hit (memory): {url}")
                    return data
                else:
                    # 过期，删除
                    del self._memory_cache[cache_key]
                    self._access_times.pop(cache_key, None)
            
            # 检查磁盘缓存
            cache_file = self.cache_dir / f"{cache_key}.cache"
            if cache_file.exists():
                try:
                    file_time = cache_file.stat().st_mtime
                    if current_time - file_time < _cache_expire:
                        with open(cache_file, 'rb') as f:
                            data = pickle.load(f)
                        
                        # 更新内存缓存
                        self._cleanup_memory_cache()
                        self._memory_cache[cache_key] = (data, current_time)
                        self._access_times[cache_key] = current_time
                        
                        _logger.debug(f"Cache hit (disk): {url}")
                        return data
                    else:
                        # 删除过期文件
                        cache_file.unlink(missing_ok=True)
                except Exception as e:
                    _logger.warning(f"Cache file error: {e}")
                    cache_file.unlink(missing_ok=True)
        
        return None
    
    def set(self, url: str, data: str, body: Optional[str] = None):
        """设置缓存数据"""
        cache_key = self._get_cache_key(url, body)
        current_time = time.time()
        
        with self._lock:
            # 更新内存缓存
            self._cleanup_memory_cache()
            self._memory_cache[cache_key] = (data, current_time)
            self._access_times[cache_key] = current_time
            
            # 异步写入磁盘缓存
            try:
                cache_file = self.cache_dir / f"{cache_key}.cache"
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            except Exception as e:
                _logger.warning(f"Failed to write disk cache: {e}")

class ConnectionPoolManager:
    """连接池管理器"""
    
    def __init__(self):
        self._cookie_jar = CookieJar()
        self._opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self._cookie_jar)
        )
        # 设置默认的User-Agent
        self._opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        ]
        urllib.request.install_opener(self._opener)
    
    def request(self, url: str, method: str, headers: dict, body: str, timeout: float) -> str:
        """发送HTTP请求"""
        try:
            body_bytes = body.encode('utf-8') if body else None
            request = urllib.request.Request(url, body_bytes, headers, method=method)
            
            with urllib.request.urlopen(request, timeout=timeout) as response:
                response_body = response.read().decode('utf-8')
                
                if 200 <= response.status < 300:
                    return response_body
                else:
                    _logger.warning(f"HTTP {response.status}: {url}")
                    return response_body
                    
        except Exception as e:
            _logger.error(f"HTTP request failed: {url} - {e}")
            raise RequestSendError from e

# 全局实例
_cache_manager = OptimizedCacheManager(_basedir)
_connection_pool = ConnectionPoolManager()

class HttpArgs(Args):
    """优化的HTTP参数类"""

    url: str
    method: str
    headers: dict
    body: Any
    timeout: float
    result: str
    use_cache: bool

    def parse(self, rawargs: dict, context: dict) -> "HttpArgs":
        # URL编码优化
        url = self.substitute(rawargs["url"], context)
        url = urllib.parse.quote(url, safe=":/?&=")

        # 处理请求头
        headers = {
            k.lower(): self.substitute(v, context)
            for k, v in rawargs.get("headers", {}).items()
        }
        
        # 设置默认的Accept编码
        if 'accept-encoding' not in headers:
            headers['accept-encoding'] = 'gzip, deflate'

        # 处理请求体
        body = self.substitute(rawargs.get("body"), context)
        if body is not None:
            content_type = headers.get("content-type", "").lower()
            if content_type.startswith("application/json"):
                body = json.dumps(body, ensure_ascii=False, separators=(',', ':'))
            elif content_type.startswith("application/x-www-form-urlencoded"):
                body = urllib.parse.urlencode(body)

        self.url = url
        self.method = rawargs["method"].upper()
        self.headers = headers
        self.body = body
        self.timeout = rawargs.get("timeout", 10)
        self.result = rawargs["result"]
        self.use_cache = rawargs.get("cache", True)  # 默认启用缓存
        return self

@Func("http_optimized", HttpArgs)
def http_optimized(args: HttpArgs, context: dict) -> None:
    """优化的HTTP请求函数"""
    
    # 检查缓存
    if args.use_cache and args.method == "GET":
        cached_response = _cache_manager.get(args.url, args.body)
        if cached_response:
            context[args.result] = cached_response
            return
    
    # 发送请求
    _logger.info(f"HTTP request: {args.method} {args.url}")
    start_time = time.time()
    
    try:
        response = _connection_pool.request(
            args.url, args.method, args.headers, args.body, args.timeout
        )
        
        # 缓存GET请求的响应
        if args.use_cache and args.method == "GET" and response:
            _cache_manager.set(args.url, response, args.body)
        
        context[args.result] = response
        
        end_time = time.time()
        _logger.info(f"HTTP response: {end_time - start_time:.3f}s")
        
    except RequestSendError:
        raise
    except Exception as e:
        _logger.error(f"Unexpected error in HTTP request: {e}")
        raise RequestSendError from e

# 向后兼容的别名
@Func("http", HttpArgs)  
def http_backward_compatible(args: HttpArgs, context: dict) -> None:
    """向后兼容的HTTP函数"""
    return http_optimized(args, context)

def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    return {
        "memory_cache_size": len(_cache_manager._memory_cache),
        "memory_cache_limit": _cache_manager._memory_size,
        "disk_cache_files": len(list(_cache_manager.cache_dir.glob("*.cache")))
    }

def clear_cache():
    """清空所有缓存"""
    with _cache_manager._lock:
        _cache_manager._memory_cache.clear()
        _cache_manager._access_times.clear()
        
        # 清空磁盘缓存
        for cache_file in _cache_manager.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
            except Exception as e:
                _logger.warning(f"Failed to delete cache file {cache_file}: {e}")