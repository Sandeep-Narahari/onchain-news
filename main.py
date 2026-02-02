import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper import ScraperOrchestrator
from database import (
    supabase,
    get_all_tokens,
    add_token,
    delete_token,
    toggle_token,
)
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler setup
scheduler = AsyncIOScheduler()


async def run_scraper_job():
    """Run the orchestrated multi-token scraper."""
    logger.info("Running scheduled scraper job...")
    orchestrator = ScraperOrchestrator()
    try:
        await orchestrator.run_all_due_tokens()
    except Exception as e:
        logger.error(f"Scraper job failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    scheduler.add_job(run_scraper_job, 'interval', hours=1, id='scraper_job')
    scheduler.start()
    
    # Run immediately on startup
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


# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------
class TokenCreate(BaseModel):
    id: str
    name: str
    enabled: bool = True
    scrape_interval: int = 60


class TokenUpdate(BaseModel):
    enabled: Optional[bool] = None
    scrape_interval: Optional[int] = None


# -------------------------------------------------------------------
# Root
# -------------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "On-Chain News Provider API is running"}


# -------------------------------------------------------------------
# News Endpoints
# -------------------------------------------------------------------
@app.get("/news")
async def get_news(limit: int = 20, offset: int = 0, token_id: Optional[str] = None):
    """Get latest insights from Supabase. Optionally filter by token."""
    try:
        query = supabase.table("insights").select("*")
        
        if token_id:
            query = query.eq("token_id", token_id)
        
        response = query.order("timestamp", desc=True).range(offset, offset + limit - 1).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Token Management Endpoints
# -------------------------------------------------------------------
@app.get("/tokens")
async def list_tokens():
    """List all tokens in the registry."""
    try:
        tokens = get_all_tokens(enabled_only=False)
        return tokens
    except Exception as e:
        logger.error(f"Error listing tokens: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tokens")
async def create_token(token: TokenCreate):
    """Add a new token to the registry."""
    try:
        success = add_token(
            token_id=token.id,
            name=token.name,
            enabled=token.enabled,
            scrape_interval=token.scrape_interval
        )
        if success:
            return {"status": "created", "token_id": token.id}
        else:
            raise HTTPException(status_code=500, detail="Failed to create token")
    except Exception as e:
        logger.error(f"Error creating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/tokens/{token_id}")
async def remove_token(token_id: str):
    """Remove a token from the registry."""
    try:
        success = delete_token(token_id)
        if success:
            return {"status": "deleted", "token_id": token_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete token")
    except Exception as e:
        logger.error(f"Error deleting token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/tokens/{token_id}/enable")
async def enable_token(token_id: str):
    """Enable a token."""
    try:
        success = toggle_token(token_id, enabled=True)
        if success:
            return {"status": "enabled", "token_id": token_id}
        raise HTTPException(status_code=500, detail="Failed to enable token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/tokens/{token_id}/disable")
async def disable_token(token_id: str):
    """Disable a token."""
    try:
        success = toggle_token(token_id, enabled=False)
        if success:
            return {"status": "disabled", "token_id": token_id}
        raise HTTPException(status_code=500, detail="Failed to disable token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------------------
# Status Endpoint
# -------------------------------------------------------------------
@app.get("/status")
async def get_status():
    """Get scraper status."""
    try:
        last_run = supabase.table("scraper_state").select("value").eq("key", "last_run").execute()
        token_count = len(get_all_tokens(enabled_only=True))
        
        return {
            "scheduler_running": scheduler.running,
            "jobs": [job.id for job in scheduler.get_jobs()],
            "last_run": last_run.data[0]["value"] if last_run.data else "Never",
            "enabled_tokens": token_count
        }
    except Exception as e:
        return {"error": str(e)}


# -------------------------------------------------------------------
# Manual Trigger
# -------------------------------------------------------------------
@app.post("/scrape")
async def trigger_scrape():
    """Manually trigger a scrape run."""
    asyncio.create_task(run_scraper_job())
    return {"status": "Scrape job started"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
