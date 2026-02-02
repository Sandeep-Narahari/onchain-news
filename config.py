"""
Centralized configuration for the On-Chain News scraper.
Optimized for proxy-free operation at scale.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# Supabase
# -------------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABSE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# -------------------------------------------------------------------
# Scraper Settings (Conservative for proxy-free)
# -------------------------------------------------------------------
MAX_CONCURRENT_WORKERS = int(os.getenv("MAX_WORKERS", "1"))  # Only 1 worker without proxies!
TOKENS_PER_BATCH = int(os.getenv("TOKENS_PER_BATCH", "5"))   # Max tokens per scheduled run
DEFAULT_SCRAPE_INTERVAL_MINUTES = int(os.getenv("SCRAPE_INTERVAL", "60"))

# Delays (longer = safer without proxies)
REQUEST_DELAY_MIN = 8.0   # seconds between insight page fetches
REQUEST_DELAY_MAX = 15.0
TOKEN_DELAY_MIN = 30.0    # seconds between different tokens (important!)
TOKEN_DELAY_MAX = 60.0
PAGE_LOAD_DELAY_MIN = 3.0  # after loading main page
PAGE_LOAD_DELAY_MAX = 6.0

# Rate limit handling
RATE_LIMIT_BACKOFF_INITIAL = 60   # seconds on first 429
RATE_LIMIT_BACKOFF_MAX = 300       # max backoff (5 min)
RATE_LIMIT_BACKOFF_MULTIPLIER = 2  # exponential multiplier

# Error handling
MAX_RETRIES_PER_TOKEN = 2
SKIP_ON_FAILURE = True  # Skip token if fails, don't crash

# -------------------------------------------------------------------
# Browser Settings
# -------------------------------------------------------------------
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

VIEWPORTS = [
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 800},
    {"width": 1440, "height": 900},
]

# -------------------------------------------------------------------
# Proxy Settings (optional - leave empty for proxy-free)
# -------------------------------------------------------------------
PROXY_LIST = [p.strip() for p in os.getenv("PROXY_LIST", "").split(",") if p.strip()]

# -------------------------------------------------------------------
# CoinGecko URL Templates
# -------------------------------------------------------------------
COINGECKO_BASE_URL = "https://www.coingecko.com/en/coins/{token_slug}"
COINGECKO_TIMELINE_API = "https://www.coingecko.com/price_charts/{token_slug}/insight_annotations?timeframe=d90"
COINGECKO_INSIGHT_URL = "https://www.coingecko.com/en/coins/{token_slug}/insights?cursor={cursor}"

