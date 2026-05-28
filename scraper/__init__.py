"""A simple web scraper used by the Synology VideoInfo plugin."""

__all__ = ["scrape"]

# Try to use enhanced version if available, else fall back to original
try:
    from scraper.scraper_enhanced import scrape
except ImportError:
    from scraper.scraper import scrape
