import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import CoinGeckoScraper
from database import supabase
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler setup
scheduler = AsyncIOScheduler()

async def run_scraper_job():
    logger.info("Running scheduled scraper job...")
    scraper = CoinGeckoScraper()
    try:
        await scraper.run()
    except Exception as e:
        logger.error(f"Scraper job failed: {e}")
        await scraper.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    scheduler.add_job(run_scraper_job, 'interval', hours=1, id='scraper_job')
    scheduler.start()
    
    # Run the job immediately on startup (optional, maybe async background)
    asyncio.create_task(run_scraper_job())
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan, title="On-Chain News Provider")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "On-Chain News Provider API is running"}

@app.get("/news")
async def get_news(limit: int = 20, offset: int = 0):
    """
    Get latest insights from Supabase.
    """
    try:
        response = supabase.table("insights") \
            .select("*") \
            .order("timestamp", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return response.data
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    """
    Get scraper status.
    """
    try:
        last_run = supabase.table("scraper_state").select("value").eq("key", "last_run").execute()
        return {
            "scheduler_running": scheduler.running,
            "jobs": [job.id for job in scheduler.get_jobs()],
            "last_run": last_run.data[0]["value"] if last_run.data else "Never"
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
