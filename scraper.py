import asyncio
import logging
import random
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

from database import (
    save_insight,
    insight_exists,
    set_scraper_state,
)

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CoinGeckoScraper:
    BASE_URL = "https://www.coingecko.com/en/coins/ethereum"
    TIMELINE_API = (
        "https://www.coingecko.com/price_charts/"
        "ethereum/insight_annotations?timeframe=d90"
    )
    INSIGHT_URL = (
        "https://www.coingecko.com/en/coins/ethereum/insights?cursor={}"
    )

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    # -------------------------------------------------------------------
    # Browser lifecycle
    # -------------------------------------------------------------------
    async def initialize(self):
        logger.info("Launching browser…")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

        self.page = await self.browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        # Correct stealth usage based on documentation
        await Stealth().apply_stealth_async(self.page)

        logger.info("Opening main page to establish session…")
        try:
            await self.page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=60000)
            # wait_until="mask" isn't a valid option, strict playwright uses 'load', 'domcontentloaded', 'networkidle', 'commit'
            # The user code had 'networkidle', I'llstick to 'domcontentloaded' for speed + explicit wait
        except:
             # retry once
             await self.page.goto(self.BASE_URL, timeout=60000)

        try:
            await self.page.wait_for_selector("body", timeout=30000)
        except Exception as e:
            logger.warning(f"Main page body wait failed: {e}")

        # Human-like pause
        await asyncio.sleep(random.uniform(3, 6))

    async def close(self):
        logger.info("Closing browser…")
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    # -------------------------------------------------------------------
    # Data fetching (browser-native)
    # -------------------------------------------------------------------
    async def fetch_timeline(self):
        logger.info("Fetching insight timeline…")

        try:
            # Return object with status/data to avoid throwing inside evaluate blindly
            result = await self.page.evaluate(
                """async (url) => {
                    try {
                        const r = await fetch(url);
                        if (!r.ok) return { success: false, status: r.status, text: r.statusText };
                        return { success: true, data: await r.json() };
                    } catch (e) {
                        return { success: false, error: e.toString() };
                    }
                }""",
                self.TIMELINE_API,
            )
            
            if result.get("success"):
                return result.get("data")
            else:
                logger.error(f"Timeline fetch failed: {result}")
                return []
        except Exception as e:
            logger.error(f"Timeline fetch exception: {e}")
            return []

    async def fetch_insight_html(self, cursor: str):
        url = self.INSIGHT_URL.format(cursor)
        logger.info(f"Fetching insight page …{cursor[-8:]}")

        try:
            result = await self.page.evaluate(
                """async (url) => {
                    try {
                        const r = await fetch(url);
                        if (!r.ok) return { success: false, status: r.status, text: r.statusText };
                        return { success: true, data: await r.text() };
                    } catch (e) {
                        return { success: false, error: e.toString() };
                    }
                }""",
                url,
            )
            
            if result.get("success"):
                return result.get("data")
            else:
                logger.error(f"Insight fetch failed: {result}")
                return None
        except Exception as e:
            logger.error(f"Insight fetch exception: {e}")
            return None

    # -------------------------------------------------------------------
    # Parsing
    # -------------------------------------------------------------------
    def parse_insights(self, html: str, timestamp: int):
        soup = BeautifulSoup(html, "html.parser")
        results = []

        for entry in soup.select(".gecko-timeline-entry"):
            try:
                data_url = entry.get("data-url", "")
                insight_id = data_url.split("/")[-1] if data_url else None

                if not insight_id:
                    insight_id = f"gen_{timestamp}_{random.randint(1000,9999)}"

                content = entry.select_one(".gecko-timeline-entry-content")
                if not content:
                    continue

                title_el = content.select_one(".gecko-insight .tw-font-semibold")
                body_el = content.select_one(".gecko-insight .tw-font-normal")
                sources_el = content.select_one(
                    ".tw-text-xs.tw-leading-4"
                )

                title = title_el.get_text(strip=True).rstrip(":") if title_el else ""
                body = body_el.get_text(strip=True) if body_el else ""

                source_count = 0
                if sources_el:
                    try:
                        source_count = int(sources_el.get_text(strip=True).split()[0])
                    except Exception:
                        pass

                results.append(
                    {
                        "id": insight_id,
                        "timestamp": timestamp,
                        "title": title,
                        "content": body,
                        "source_count": source_count,
                    }
                )
            except Exception as e:
                logger.warning(f"Parse error: {e}")

        return results

    # -------------------------------------------------------------------
    # Job runner
    # -------------------------------------------------------------------
    async def run(self):
        await self.initialize()

        try:
            timeline = await self.fetch_timeline()
            if not timeline:
                logger.warning("Timeline empty.")
                return

            timeline.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

            inserted = 0

            for item in timeline:
                cursor = item.get("latest_insight_cursor")
                timestamp = item.get("timestamp")

                if not cursor:
                    continue

                await asyncio.sleep(random.uniform(2.5, 5.5))

                html = await self.fetch_insight_html(cursor)
                if not html:
                    continue

                insights = self.parse_insights(html, timestamp)

                for insight in insights:
                    if insight_exists(insight["id"]):
                        continue

                    save_insight(insight)
                    inserted += 1

            logger.info(f"Scraping finished. New insights: {inserted}")
            set_scraper_state("last_run", str(int(time.time())))

        finally:
            await self.close()


# -------------------------------------------------------------------
# Entrypoint
# -------------------------------------------------------------------
async def main():
    scraper = CoinGeckoScraper()
    await scraper.run()


if __name__ == "__main__":
    asyncio.run(main())
