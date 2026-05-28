"""Enhanced scraper with source management integration."""
import argparse
import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from scraper.enums import lang_type, video_type
from scraper.exceptions import ScrapeError, StopSignal
from scraper.fake import fake_result
from scraper.functions import findfunc
from scraper.source_management import init_sms, get_sms

_logger = logging.getLogger(__name__)

# define default scraping configuration path
_basedir = Path(__file__).resolve().parent
_flow_path = _basedir / "../scrapeflows"
_flowconf_path = _basedir / "../scrapeflows.conf"

# define maximum number of results to return
_maxlimit = 10
_results: List[Any] = []

# Initialize source management system
_sms_initialized = False


def _init_sms():
    """Initialize source management system."""
    global _sms_initialized
    if not _sms_initialized:
        try:
            source_groups_path = _basedir / "../source_groups.json"
            if source_groups_path.exists():
                init_sms(str(source_groups_path))
            else:
                init_sms()
            _sms_initialized = True
        except Exception as e:
            _logger.warning("Failed to initialize source management: %s", e)


def scrape(plugin_id: str) -> str:
    """Scrape video information with source management integration."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--type", type=video_type, required=True)
    parser.add_argument("--lang", type=lang_type, required=False)
    parser.add_argument("--limit", type=int, default=_maxlimit)
    parser.add_argument("--allowguess", action="store_true", default=False)
    parser.add_argument("--loglevel", type=str, default="critical")
    parser.add_argument("--sms-enable", action="store_true", default=True,
                       help="Enable source management system")

    args = parser.parse_known_args()[0]
    videotype = args.type.value
    language = args.lang.value if args.lang is not None else None
    maxlimit = min(args.limit, _maxlimit)
    loglevel = args.loglevel.upper()
    use_sms = args.sms_enable

    # set basic logging configuration
    logformat = (
        "%(asctime)s %(threadName)s %(levelname)s "
        "%(filename)s:%(lineno)d - %(message)s"
    )
    logging.basicConfig(level=getattr(logging, loglevel), format=logformat)

    # parse --input argument as JSON
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

    # Initialize source management system if enabled
    sms = None
    if use_sms:
        _init_sms()
        try:
            sms = get_sms()
            _logger.info("Source management system initialized")
        except Exception as e:
            _logger.warning("Source management unavailable: %s", e)

    # load and execute scrape flows using smart ordering
    start = time.time()
    taskqueue: Dict[int, List[threading.Thread]] = {}
    
    flows = list(ScrapeFlow.load(_flow_path, videotype, language, initialval))
    
    # Use source management to order flows if available
    if sms:
        flows = _order_flows(flows, initialval, sms)
    
    for flow in flows:
        task = threading.Thread(target=_start, args=(flow, maxlimit, sms))
        tasks = taskqueue.get(flow.priority, [])
        tasks.append(task)
        taskqueue[flow.priority] = tasks
    
    for tasks in dict(sorted(taskqueue.items(), key=lambda x: x[0])).values():
        if len(_results) >= maxlimit:
            break
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()
    
    end = time.time()
    _logger.info("Total execution time: %.3f seconds", end - start)
    
    # Save source management data
    if sms:
        try:
            sms.save()
            _logger.info("Source management data saved")
        except Exception as e:
            _logger.warning("Failed to save source management data: %s", e)
    
    return json.dumps(
        {"success": True, "result": _results}, ensure_ascii=False, indent=2
    ).replace("[plugin_id]", plugin_id)


def _order_flows(flows: List["ScrapeFlow"], initialval: Dict, sms) -> List["ScrapeFlow"]:
    """Order flows using source management system."""
    if not flows:
        return flows
    
    # Get content hint for optimization
    content_hint = initialval.get("title", "")
    
    # Get optimal source order
    optimal_sources = sms.get_optimal_sources(
        video_type=initialval.get("type", "movie"),
        content_hint=content_hint,
        limit=len(flows)
    )
    
    if not optimal_sources:
        return flows
    
    # Create source to flow map
    source_flow_map = {flow.site: flow for flow in flows}
    
    # Order flows by optimal source order first, then remaining
    ordered_flows = []
    for source in optimal_sources:
        if source in source_flow_map:
            ordered_flows.append(source_flow_map.pop(source))
    
    # Add remaining flows
    ordered_flows.extend(source_flow_map.values())
    
    _logger.info(
        "Ordered %d flows using source management, %d optimal, %d remaining",
        len(flows),
        len(ordered_flows) - len(source_flow_map),
        len(source_flow_map)
    )
    
    return ordered_flows


def _start(flow: "ScrapeFlow", limit: int, sms=None):
    """Start a scrape flow and store results with source tracking."""
    start_time = time.time()
    success = False
    num_results = 0
    
    try:
        result_gen = flow.start()
        while True:
            if len(_results) >= limit:
                success = num_results > 0
                break
            try:
                result = next(result_gen)
                _results.append(result)
                num_results += 1
            except StopIteration:
                success = num_results > 0
                break
    except ScrapeError:
        _logger.error("Failed to scrape from %s", flow.site, exc_info=True)
    except Exception as e:
        _logger.error("Unexpected error scraping %s: %s", flow.site, e)
    finally:
        duration = time.time() - start_time
        
        # Record scrape result with source management
        if sms:
            try:
                data = {"title": flow.site, "number": flow.context.get("title", "")}
                if num_results > 0 and _results:
                    data = _results[-num_results] if num_results == 1 else _results[-1]
                
                sms.record_scrape(
                    source=flow.site,
                    success=success,
                    duration=duration,
                    data=data
                )
                _logger.debug(
                    "Scrape recorded: %s, success=%s, duration=%.2fs",
                    flow.site,
                    success,
                    duration
                )
            except Exception as e:
                _logger.warning("Failed to record scrape: %s", e)


def _version(plugin_id: str) -> str:
    """Split the plugin ID to get the version."""
    if "-" in plugin_id:
        version = plugin_id.split("-")[-1]
        if version != "plugin":
            return f"/{version}"
    return ""


class ScrapeFlow:
    """A flow of steps to scrape video information."""

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
        """Start the scrape flow and return a generator."""
        for funcname, rawargs in [s.popitem() for s in self.steps]:
            # execute the function with context
            try:
                iterable = findfunc(funcname)(rawargs, self.context)
                if iterable is not None:
                    yield from iterable
            except StopSignal:
                break

    @staticmethod
    def load(path: Path, videotype: str, language: str, initialval: dict):
        """Load scrape flows from given path."""

        flowconf = None
        if _flowconf_path.exists():
            with open(_flowconf_path, "r", encoding="utf-8") as conf_reader:
                flowconf = json.load(conf_reader)

        for filepath in path.glob("*.json"):
            with open(filepath, "r", encoding="utf-8") as def_reader:
                flowdef = json.load(def_reader)
            site = flowdef["site"]
            siteconf = None
            if flowconf is not None and site in flowconf:
                siteconf = flowconf[site]

            # filter out flows that do not match the video type
            if not ScrapeFlow.valid(flowdef, siteconf, videotype, language):
                continue

            # generate a flow instance from the definition
            steps = list(flowdef["steps"])
            context = initialval.copy()
            context["site"] = site
            context["doh"] = flowdef.get("doh_enabled", False)
            priority = None
            if siteconf is not None:
                priority = siteconf["priority"]
                context.update(siteconf)
            yield ScrapeFlow(site, steps, context, priority)

    @staticmethod
    def valid(flowdef: Any, siteconf: Any, videotype: str, language: str):
        """Check if the flow definition is valid."""

        if language is not None and "lang" in flowdef:
            if language not in flowdef["lang"]:
                return False

        if flowdef["type"] != videotype:
            return False

        if siteconf is not None:
            if not any(videotype.startswith(t) for t in siteconf["types"]):
                return False

        return True
