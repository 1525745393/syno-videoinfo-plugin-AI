"""
Enhanced entry point with source management integration.
"""
from pathlib import Path
import argparse
import sys
import logging

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import core modules
import scraper
from scraper.source_management import init_sms, get_sms


def scrape_with_management(plugin_id):
    """
    Scrape video metadata using the enhanced source management system.
    """
    try:
        # Initialize source management system
        try:
            sms = init_sms('source_groups.json')
            logging.info("Source management system initialized")
        except Exception as e:
            logging.warning(f"Source management init failed: {e}, using default scraper")
            return scraper.scrape(plugin_id)

        # Get optimal sources based on content (if available)
        content_hint = ""  # Would get from input in real use
        optimal_sources = sms.get_optimal_sources('movie', content_hint, limit=10)
        logging.info(f"Optimal sources: {optimal_sources[:5]}")

        # Use standard scraper
        result = scraper.scrape(plugin_id)

        return result

    except Exception as e:
        logging.error(f"Error: {e}")
        return scraper.scrape(plugin_id)


def main():
    parser = argparse.ArgumentParser(
        description="Synology VideoInfo Plugin with enhanced source management"
    )
    parser.add_argument(
        "--type", type=str, choices=["movie", "tvshow", "episode"],
        help="Video type"
    )
    parser.add_argument(
        "--input", type=str,
        help="Input data in JSON format"
    )
    parser.add_argument(
        "--limit", type=int, default=1,
        help="Maximum number of results"
    )
    parser.add_argument(
        "--loglevel", type=str, choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO", help="Log level"
    )
    parser.add_argument(
        "--health", action="store_true",
        help="Run health check and exit"
    )
    parser.add_argument(
        "--sources", action="store_true",
        help="Show source statistics and exit"
    )
    parser.add_argument(
        "--test-source", type=str,
        help="Test a specific source and exit"
    )

    args = parser.parse_args()

    # Set log level
    if args.loglevel:
        logging.getLogger().setLevel(getattr(logging, args.loglevel))

    root_dir = Path(__file__).resolve().parent
    plugin_id = root_dir.name

    # Health check mode
    if args.health:
        print("=== Source Health Check ===")
        try:
            sms = init_sms('source_groups.json')
            report = sms.get_health_report()
            print(f"Total sources: {report['total_sources']}")
            print(f"Healthy: {len(report['healthy'])}")
            print(f"Warning: {len(report['warning'])}")
            print(f"Error: {len(report['error'])}")
            if report['alerts']:
                print("\nAlerts:")
                for alert in report['alerts'][:5]:
                    print(f"  [{alert['level'].upper()}] {alert['source']}: {alert['message']}")
        except Exception as e:
            print(f"Health check failed: {e}")
        return 0

    # Source statistics mode
    if args.sources:
        print("=== Source Statistics ===")
        try:
            sms = init_sms('source_groups.json')
            stats = sms.get_statistics()
            print(f"Total sources: {stats['source_manager']['total_sources']}")
            print(f"Categories: {stats['source_manager']['total_categories']}")
            print(f"Enabled: {stats['source_manager']['enabled_categories']}")
            print(f"Disabled: {stats['source_manager']['disabled_categories']}")
            print("\nCategory details:")
            for cat_id, cat_info in stats['source_manager']['categories'].items():
                print(f"  {cat_info['name']}: {cat_info['source_count']} sources")
        except Exception as e:
            print(f"Statistics failed: {e}")
        return 0

    # Test source mode
    if args.test_source:
        print(f"=== Testing source: {args.test_source} ===")
        try:
            sms = init_sms('source_groups.json')
            status = sms.get_source_status(args.test_source)
            if status:
                print(f"Status: {status.status}")
                print(f"Success rate: {status.success_rate:.1%}")
                print(f"Average duration: {status.avg_duration:.2f}s")
                print(f"Total requests: {status.total_requests}")
                print(f"Successful: {status.successful_requests}")
                print(f"Failed: {status.failed_requests}")
                print(f"Healthy: {status.is_healthy}")
            else:
                print(f"No data for source: {args.test_source}")
        except Exception as e:
            print(f"Test failed: {e}")
        return 0

    # Normal scraping mode
    print(scrape_with_management(plugin_id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
