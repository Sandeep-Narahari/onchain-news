"""
Multi-token CoinGecko Insights Scraper with anti-blocking strategies.
"""
import asyncio
import logging
import random
import time
from typing import Optional, Dict, List
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Safe import for playwright-stealth
try:
    from playwright_stealth import stealth_async
except ImportError:
    try:
        from playwright_stealth.stealth import stealth_async
    except ImportError:
        from playwright_stealth import Stealth
        async def stealth_async(page):
            await Stealth().apply_stealth_async(page)

import config
from database import (
    save_insight,
    insight_exists,
    update_token_last_scraped,
    get_tokens_due_for_scrape,
)

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BrowserPool:
    """Manages browser instances with proxy rotation."""
    
    def __init__(self):
        self.playwright = None
        self.browsers: List[Browser] = []
        self.proxy_index = 0
    
    async def start(self):
        self.playwright = await async_playwright().start()
        logger.info("Browser pool started")
    
    async def stop(self):
        for browser in self.browsers:
            try:
                await browser.close()
            except:
                pass
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser pool stopped")
    
    def _get_next_proxy(self) -> Optional[str]:
        """Round-robin proxy selection."""
        if not config.PROXY_LIST:
            return None
        proxy = config.PROXY_LIST[self.proxy_index % len(config.PROXY_LIST)]
        self.proxy_index += 1
        return proxy
    
    async def get_browser(self) -> Browser:
        """Get or create a browser instance."""
        proxy = self._get_next_proxy()
        
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--window-size=1280,800"
        ]
        
        launch_kwargs = {
            "headless": config.HEADLESS,
            "args": launch_args,
        }
        
        if proxy:
            launch_kwargs["proxy"] = {"server": proxy}
            logger.info(f"Launching browser with proxy: {proxy[:30]}...")
        
        browser = await self.playwright.chromium.launch(**launch_kwargs)
        self.browsers.append(browser)
        return browser
    
    async def create_context(self, browser: Browser) -> BrowserContext:
        """Create a new browser context with stealth settings."""
        context = await browser.new_context(
            user_agent=random.choice(config.USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            device_scale_factor=random.choice([1, 2]),
        )
        return context


class TokenScraper:
    """Scrapes insights for a single token."""
    
    def __init__(self, token: Dict, context: BrowserContext):
        self.token = token
        self.token_id = token["id"]
        self.token_name = token.get("name", token["id"])
        self.context = context
        self.page: Optional[Page] = None
    
    @property
    def base_url(self) -> str:
        return config.COINGECKO_BASE_URL.format(token_slug=self.token_id)
    
    @property
    def timeline_api(self) -> str:
        return config.COINGECKO_TIMELINE_API.format(token_slug=self.token_id)
    
    def insight_url(self, cursor: str) -> str:
        return config.COINGECKO_INSIGHT_URL.format(token_slug=self.token_id, cursor=cursor)
    
    async def initialize(self):
        """Open page and navigate to token page."""
        self.page = await self.context.new_page()
        await stealth_async(self.page)
        await self.page.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        logger.info(f"[{self.token_name}] Opening page...")
        try:
            await self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=60000)
            await self._human_jitter()
            await asyncio.sleep(random.uniform(2, 4))
        except Exception as e:
            logger.warning(f"[{self.token_name}] Navigation warning: {e}")
    
    async def close(self):
        if self.page:
            await self.page.close()
    
    async def _human_jitter(self):
        """Simulate human-like mouse movements."""
        if not self.page:
            return
        try:
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1000)
                y = random.randint(100, 600)
                await self.page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.3))
        except:
            pass
    
    async def fetch_timeline(self) -> List[Dict]:
        logger.info(f"[{self.token_name}] Fetching timeline...")
        await self._human_jitter()
        
        try:
            result = await self.page.evaluate("""async (url) => {
                try {
                    const r = await fetch(url, { headers: {'Accept': 'application/json'} });
                    if (!r.ok) return { success: false, status: r.status };
                    return { success: true, data: await r.json() };
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            }""", self.timeline_api)
            
            if result.get("success"):
                return result.get("data", [])
            else:
                logger.error(f"[{self.token_name}] Timeline failed: {result}")
                return []
        except Exception as e:
            logger.error(f"[{self.token_name}] Timeline exception: {e}")
            return []
    
    async def fetch_insight_html(self, cursor: str) -> Optional[str]:
        url = self.insight_url(cursor)
        logger.info(f"[{self.token_name}] Fetching insight ...{cursor[-8:]}")
        
        delay = random.uniform(config.REQUEST_DELAY_MIN, config.REQUEST_DELAY_MAX)
        await asyncio.sleep(delay)
        
        try:
            result = await self.page.evaluate("""async (url) => {
                try {
                    const r = await fetch(url);
                    if (!r.ok) return { success: false, status: r.status };
                    return { success: true, data: await r.text() };
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            }""", url)
            
            if result.get("success"):
                return result.get("data")
            elif result.get("status") == 429:
                logger.warning(f"[{self.token_name}] Rate limited. Backing off {config.RATE_LIMIT_BACKOFF}s...")
                await asyncio.sleep(config.RATE_LIMIT_BACKOFF)
                return None
            else:
                logger.error(f"[{self.token_name}] Insight failed: {result}")
                return None
        except Exception as e:
            logger.error(f"[{self.token_name}] Insight exception: {e}")
            return None
    
    def parse_insights(self, html: str, timestamp: int) -> List[Dict]:
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        for entry in soup.select(".gecko-timeline-entry"):
            try:
                data_url = entry.get("data-url", "")
                insight_id = data_url.split("/")[-1] if data_url else None
                if not insight_id:
                    insight_id = f"gen_{self.token_id}_{timestamp}_{random.randint(1000,9999)}"
                
                # Prefix with token_id to ensure uniqueness across tokens
                full_id = f"{self.token_id}_{insight_id}"
                
                content = entry.select_one(".gecko-timeline-entry-content")
                if not content:
                    continue
                
                title_el = content.select_one(".gecko-insight .tw-font-semibold")
                body_el = content.select_one(".gecko-insight .tw-font-normal")
                sources_el = content.select_one(".tw-text-xs.tw-leading-4")
                
                title = title_el.get_text(strip=True).rstrip(":") if title_el else ""
                body = body_el.get_text(strip=True) if body_el else ""
                
                # Extract source count
                source_count = 0
                if sources_el:
                    try:
                        source_count = int(sources_el.get_text(strip=True).split()[0])
                    except:
                        pass
                
                # Extract source URLs - look for links in the entry
                sources = []
                
                # Try different selectors for source links
                # Sources are typically in a section with links to news/articles
                source_links = entry.select("a[href*='http']")
                for link in source_links:
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    
                    # Skip internal CoinGecko links
                    if "coingecko.com" in href:
                        continue
                    
                    # Skip empty links
                    if not href or not text:
                        continue
                    
                    sources.append({
                        "url": href,
                        "title": text[:200]  # Limit title length
                    })
                
                # Also check for source indicators/citations
                source_section = entry.select(".gecko-insight-sources a, .insight-source a, [class*='source'] a")
                for link in source_section:
                    href = link.get("href", "")
                    text = link.get_text(strip=True)
                    if href and "coingecko.com" not in href:
                        # Avoid duplicates
                        if not any(s["url"] == href for s in sources):
                            sources.append({
                                "url": href,
                                "title": text[:200]
                            })
                
                results.append({
                    "id": full_id,
                    "token_id": self.token_id,
                    "timestamp": timestamp,
                    "title": title,
                    "content": body,
                    "source_count": source_count,
                    "sources": sources,  # Array of {url, title}
                })
            except Exception as e:
                logger.warning(f"[{self.token_name}] Parse error: {e}")
        
        
        return results
    
    async def scrape(self) -> int:
        """Run the full scraping flow for this token. Returns count of new insights."""
        await self.initialize()
        inserted = 0
        
        try:
            timeline = await self.fetch_timeline()
            if not timeline:
                logger.warning(f"[{self.token_name}] Empty timeline")
                return 0
            
            timeline.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            for item in timeline:
                cursor = item.get("latest_insight_cursor")
                timestamp = item.get("timestamp")
                if not cursor:
                    continue
                
                html = await self.fetch_insight_html(cursor)
                insights = self.parse_insights(html, timestamp)
                
                for insight in insights:
                    if insight_exists(insight["id"]):
                        continue
                    save_insight(insight)
                    inserted += 1
            
            update_token_last_scraped(self.token_id)
            logger.info(f"[{self.token_name}] Done. New insights: {inserted}")
            
        finally:
            await self.close()
        
        return inserted


class ScraperOrchestrator:
    """Orchestrates scraping across multiple tokens with rate limiting."""
    
    def __init__(self):
        self.pool = BrowserPool()
        self.rate_limit_backoff = config.RATE_LIMIT_BACKOFF_INITIAL
    
    async def run_all_due_tokens(self):
        """Scrape tokens that are due, respecting batch limits."""
        logger.info("Starting orchestrated scrape run...")
        await self.pool.start()
        
        try:
            all_due_tokens = get_tokens_due_for_scrape()
            if not all_due_tokens:
                logger.info("No tokens due for scraping")
                return
            
            # Batch limit: only process N tokens per run
            tokens = all_due_tokens[:config.TOKENS_PER_BATCH]
            remaining = len(all_due_tokens) - len(tokens)
            
            logger.info(f"Processing {len(tokens)} tokens this batch ({remaining} queued for next run)")
            
            # Sequential processing is safer without proxies
            browser = await self.pool.get_browser()
            
            for i, token in enumerate(tokens):
                logger.info(f"[{i+1}/{len(tokens)}] Starting {token['name']}...")
                
                context = await self.pool.create_context(browser)
                
                try:
                    scraper = TokenScraper(token, context)
                    await scraper.scrape()
                    # Reset backoff on success
                    self.rate_limit_backoff = config.RATE_LIMIT_BACKOFF_INITIAL
                except Exception as e:
                    logger.error(f"Error scraping {token['id']}: {e}")
                    if config.SKIP_ON_FAILURE:
                        logger.info(f"Skipping {token['id']} and continuing...")
                    else:
                        raise
                finally:
                    await context.close()
                
                # Delay between tokens (important for avoiding blocks)
                if i < len(tokens) - 1:
                    delay = random.uniform(config.TOKEN_DELAY_MIN, config.TOKEN_DELAY_MAX)
                    logger.info(f"Waiting {delay:.0f}s before next token...")
                    await asyncio.sleep(delay)
            
        finally:
            await self.pool.stop()
        
        logger.info("Batch complete")
    
    async def scrape_single_token(self, token_id: str):
        """Scrape a single token by ID."""
        await self.pool.start()
        
        try:
            browser = await self.pool.get_browser()
            context = await self.pool.create_context(browser)
            
            token = {"id": token_id, "name": token_id}
            scraper = TokenScraper(token, context)
            await scraper.scrape()
            
            await context.close()
        finally:
            await self.pool.stop()


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
async def main():
    """Run a full scrape of all due tokens."""
    orchestrator = ScraperOrchestrator()
    await orchestrator.run_all_due_tokens()


if __name__ == "__main__":
    asyncio.run(main())