"""优化版本的爬虫模块 - 提升并发性能和资源管理"""
import argparse
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty

from scraper.enums import lang_type, video_type
from scraper.exceptions import ScrapeError, StopSignal
from scraper.fake import fake_result
from scraper.functions import findfunc

_logger = logging.getLogger(__name__)

# 配置参数
_basedir = Path(__file__).resolve().parent
_flow_path = _basedir / "../scrapeflows"
_flowconf_path = _basedir / "../scrapeflows.conf"
_maxlimit = 10

class OptimizedResultCollector:
    """优化的结果收集器，线程安全且高效"""
    
    def __init__(self, max_results: int):
        self.max_results = max_results
        self._results: List[Any] = []
        self._lock = threading.RLock()
        self._result_count = 0
        self._start_time = time.time()
    
    def add_result(self, result: Any) -> bool:
        """添加结果，返回是否成功添加"""
        with self._lock:
            if self._result_count < self.max_results:
                self._results.append(result)
                self._result_count += 1
                _logger.debug(f"Added result {self._result_count}/{self.max_results}")
                return True
            return False
    
    def get_results(self) -> List[Any]:
        """获取所有结果"""
        with self._lock:
            return self._results.copy()
    
    def is_full(self) -> bool:
        """检查结果是否已满"""
        with self._lock:
            return self._result_count >= self.max_results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            return {
                "result_count": self._result_count,
                "max_results": self.max_results,
                "elapsed_time": time.time() - self._start_time,
                "is_full": self.is_full()
            }

class OptimizedThreadPoolManager:
    """优化的线程池管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None
        
    def __enter__(self):
        self._executor = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="ScraperWorker"
        )
        return self._executor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)

def optimized_scrape(plugin_id: str) -> str:
    """优化版本的爬虫主函数"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--type", type=video_type, required=True)
    parser.add_argument("--lang", type=lang_type, required=False)
    parser.add_argument("--limit", type=int, default=_maxlimit)
    parser.add_argument("--allowguess", action="store_true", default=False)
    parser.add_argument("--loglevel", type=str, default="critical")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of worker threads")

    args = parser.parse_known_args()[0]
    videotype = args.type.value
    language = args.lang.value if args.lang is not None else None
    maxlimit = min(args.limit, _maxlimit)
    loglevel = args.loglevel.upper()
    max_workers = min(args.max_workers, 8)  # 限制最大线程数

    # 设置日志
    logformat = (
        "%(asctime)s [%(threadName)-12s] %(levelname)-8s "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    logging.basicConfig(level=getattr(logging, loglevel), format=logformat)

    # 解析输入
    jsoninput = json.loads(args.input)
    if jsoninput["title"] == "--install":
        return fake_result(plugin_id, videotype)
    
    initialval = {
        "title": jsoninput["title"],
        "season": jsoninput.get("season", 0),
        "episode": jsoninput.get("episode", 1),
        "available": jsoninput.get("original_available", None),
        "year": str(jsoninput.get("original_available", ""))[:4],
        "lang": language,
        "limit": maxlimit,
        "version": _version(plugin_id),
    }

    # 初始化结果收集器
    result_collector = OptimizedResultCollector(maxlimit)
    
    # 加载爬虫流程
    flows = list(ScrapeFlow.load(_flow_path, videotype, language, initialval))
    if not flows:
        _logger.warning("No scraping flows found")
        return json.dumps({"success": True, "result": []}, ensure_ascii=False, indent=2)
    
    # 按优先级分组
    priority_groups = {}
    for flow in flows:
        priority = flow.priority
        if priority not in priority_groups:
            priority_groups[priority] = []
        priority_groups[priority].append(flow)
    
    start_time = time.time()
    
    # 按优先级顺序执行
    with OptimizedThreadPoolManager(max_workers) as executor:
        for priority in sorted(priority_groups.keys()):
            if result_collector.is_full():
                break
                
            priority_flows = priority_groups[priority]
            _logger.info(f"Processing priority {priority} with {len(priority_flows)} flows")
            
            # 提交当前优先级的所有任务
            futures = []
            for flow in priority_flows:
                if result_collector.is_full():
                    break
                future = executor.submit(_process_flow_safe, flow, result_collector)
                futures.append(future)
            
            # 等待当前优先级的任务完成
            for future in as_completed(futures):
                try:
                    future.result()  # 获取结果，如果有异常会被抛出
                except Exception as e:
                    _logger.error(f"Flow execution error: {e}")
                
                # 如果结果已满，取消剩余任务
                if result_collector.is_full():
                    for remaining_future in futures:
                        remaining_future.cancel()
                    break
    
    end_time = time.time()
    stats = result_collector.get_stats()
    
    _logger.info(f"Scraping completed: {stats['result_count']} results in {end_time - start_time:.3f}s")
    
    return json.dumps(
        {"success": True, "result": result_collector.get_results()}, 
        ensure_ascii=False, indent=2
    ).replace("[plugin_id]", plugin_id)

def _process_flow_safe(flow: "ScrapeFlow", result_collector: OptimizedResultCollector):
    """安全的流程处理函数，包含错误处理"""
    try:
        _logger.debug(f"Starting flow: {flow.site}")
        result_gen = flow.start()
        
        while not result_collector.is_full():
            try:
                result = next(result_gen)
                if not result_collector.add_result(result):
                    break  # 结果已满
                _logger.debug(f"Flow {flow.site} produced result")
            except StopIteration:
                _logger.debug(f"Flow {flow.site} completed")
                break
            except StopSignal:
                _logger.debug(f"Flow {flow.site} stopped by signal")
                break
                
    except ScrapeError as e:
        _logger.error(f"Scrape error in {flow.site}: {e}")
    except Exception as e:
        _logger.error(f"Unexpected error in {flow.site}: {e}", exc_info=True)

def _version(plugin_id: str) -> str:
    """解析插件版本"""
    if "-" in plugin_id:
        version = plugin_id.split("-")[-1]
        if version != "plugin":
            return f"/{version}"
    return ""

class ScrapeFlow:
    """优化的爬虫流程类"""

    def __init__(
        self,
        site: str,
        steps: list,
        context: dict,
        priority: Optional[int],
    ):
        self.site = site
        self.steps = steps
        self.context = context
        self.priority = priority if priority is not None else 999

    def start(self):
        """启动爬虫流程并返回生成器"""
        _logger.debug(f"Starting scrape flow for {self.site}")
        
        for step_idx, step_dict in enumerate([s.copy() for s in self.steps]):
            if not step_dict:
                continue
                
            funcname, rawargs = next(iter(step_dict.items()))
            _logger.debug(f"Executing step {step_idx + 1}: {funcname}")
            
            try:
                iterable = findfunc(funcname)(rawargs, self.context)
                if iterable is not None:
                    yield from iterable
            except StopSignal:
                _logger.debug(f"Flow {self.site} stopped at step {step_idx + 1}")
                break
            except Exception as e:
                _logger.error(f"Error in step {step_idx + 1} of {self.site}: {e}")
                raise

    @staticmethod
    def load(path: Path, videotype: str, language: Optional[str], initialval: dict):
        """加载爬虫流程配置"""
        _logger.info(f"Loading scrape flows from {path}")
        
        # 加载站点配置
        flowconf = None
        if _flowconf_path.exists():
            try:
                with open(_flowconf_path, "r", encoding="utf-8") as conf_reader:
                    flowconf = json.load(conf_reader)
                _logger.debug(f"Loaded flow configuration with {len(flowconf)} sites")
            except Exception as e:
                _logger.warning(f"Failed to load flow configuration: {e}")

        loaded_count = 0
        for filepath in path.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as def_reader:
                    flowdef = json.load(def_reader)
                
                site = flowdef["site"]
                siteconf = flowconf.get(site) if flowconf else None

                # 验证流程定义
                if not ScrapeFlow.valid(flowdef, siteconf, videotype, language):
                    _logger.debug(f"Skipping {site}: not valid for {videotype}/{language}")
                    continue

                # 生成流程实例
                steps = list(flowdef["steps"])
                context = initialval.copy()
                context["site"] = site
                context["doh"] = flowdef.get("doh_enabled", False)
                
                priority = None
                if siteconf is not None:
                    priority = siteconf.get("priority")
                    context.update(siteconf)
                
                yield ScrapeFlow(site, steps, context, priority)
                loaded_count += 1
                
            except Exception as e:
                _logger.error(f"Failed to load flow from {filepath}: {e}")
        
        _logger.info(f"Loaded {loaded_count} scrape flows")

    @staticmethod
    def valid(flowdef: Any, siteconf: Any, videotype: str, language: Optional[str]) -> bool:
        """验证流程定义是否有效"""
        # 检查语言匹配
        if language is not None and "lang" in flowdef:
            if language not in flowdef["lang"]:
                return False

        # 检查视频类型匹配
        if flowdef["type"] != videotype:
            return False

        # 检查站点配置
        if siteconf is not None:
            if not any(videotype.startswith(t) for t in siteconf.get("types", [])):
                return False

        return True

# 为了向后兼容，保留原函数名
def scrape(plugin_id: str) -> str:
    """向后兼容的爬虫函数"""
    return optimized_scrape(plugin_id)