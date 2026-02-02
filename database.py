import os
import logging
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Supabase Client
# -------------------------------------------------------------------
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABSE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in .env")

supabase: Client = create_client(url, key)

# -------------------------------------------------------------------
# Scraper State
# -------------------------------------------------------------------
def get_scraper_state(key_name: str):
    try:
        response = supabase.table("scraper_state").select("value").eq("key", key_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["value"]
        return None
    except Exception as e:
        logger.error(f"Error getting state for {key_name}: {e}")
        return None

def set_scraper_state(key_name: str, value: str):
    try:
        data = {"key": key_name, "value": value}
        supabase.table("scraper_state").upsert(data).execute()
    except Exception as e:
        logger.error(f"Error setting state for {key_name}: {e}")

# -------------------------------------------------------------------
# Insights
# -------------------------------------------------------------------
def insight_exists(insight_id: str) -> bool:
    try:
        response = supabase.table("insights").select("id").eq("id", insight_id).execute()
        return len(response.data) > 0
    except Exception as e:
        logger.error(f"Error checking existence for {insight_id}: {e}")
        return False

def save_insight(insight_data: dict):
    try:
        supabase.table("insights").upsert(insight_data).execute()
        logger.info(f"Saved insight: {insight_data.get('id')}")
    except Exception as e:
        logger.error(f"Error saving insight {insight_data.get('id')}: {e}")

# -------------------------------------------------------------------
# Tokens
# -------------------------------------------------------------------
def get_all_tokens(enabled_only: bool = True):
    """Get all tokens from the registry."""
    try:
        query = supabase.table("tokens").select("*")
        if enabled_only:
            query = query.eq("enabled", True)
        response = query.execute()
        return response.data or []
    except Exception as e:
        logger.error(f"Error fetching tokens: {e}")
        return []

def get_tokens_due_for_scrape():
    """Get tokens that are due for scraping based on their interval."""
    try:
        tokens = get_all_tokens(enabled_only=True)
        now = datetime.now(timezone.utc)
        due_tokens = []
        
        for token in tokens:
            last_scraped = token.get("last_scraped")
            interval_minutes = token.get("scrape_interval", 60)
            
            if last_scraped is None:
                due_tokens.append(token)
            else:
                # Parse ISO timestamp
                if isinstance(last_scraped, str):
                    last_scraped = datetime.fromisoformat(last_scraped.replace("Z", "+00:00"))
                
                elapsed = (now - last_scraped).total_seconds() / 60
                if elapsed >= interval_minutes:
                    due_tokens.append(token)
        
        return due_tokens
    except Exception as e:
        logger.error(f"Error getting due tokens: {e}")
        return []

def update_token_last_scraped(token_id: str):
    """Update the last_scraped timestamp for a token."""
    try:
        supabase.table("tokens").update({
            "last_scraped": datetime.now(timezone.utc).isoformat()
        }).eq("id", token_id).execute()
    except Exception as e:
        logger.error(f"Error updating last_scraped for {token_id}: {e}")

def add_token(token_id: str, name: str, enabled: bool = True, scrape_interval: int = 60):
    """Add a new token to the registry."""
    try:
        data = {
            "id": token_id,
            "name": name,
            "enabled": enabled,
            "scrape_interval": scrape_interval
        }
        supabase.table("tokens").upsert(data).execute()
        logger.info(f"Added/updated token: {token_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding token {token_id}: {e}")
        return False

def delete_token(token_id: str):
    """Remove a token from the registry."""
    try:
        supabase.table("tokens").delete().eq("id", token_id).execute()
        logger.info(f"Deleted token: {token_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting token {token_id}: {e}")
        return False

def toggle_token(token_id: str, enabled: bool):
    """Enable or disable a token."""
    try:
        supabase.table("tokens").update({"enabled": enabled}).eq("id", token_id).execute()
        return True
    except Exception as e:
        logger.error(f"Error toggling token {token_id}: {e}")
        return False
