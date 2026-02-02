import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Handle the typo in the .env file if necessary, or use the standard one
url: str = os.getenv("SUPABASE_URL")
# The user's env has a typo: SUPABSE_SERVICE_ROLE_KEY
key: str = os.getenv("SUPABSE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in .env")

supabase: Client = create_client(url, key)

def get_scraper_state(key_name: str):
    """
    Get a value from the scraper_state table.
    """
    try:
        response = supabase.table("scraper_state").select("value").eq("key", key_name).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["value"]
        return None
    except Exception as e:
        print(f"Error getting state for {key_name}: {e}")
        return None

def set_scraper_state(key_name: str, value: str):
    """
    Upsert a value into the scraper_state table.
    """
    try:
        data = {"key": key_name, "value": value}
        # Upsert requires the data to be a dictionary or list of dictionaries
        supabase.table("scraper_state").upsert(data).execute()
    except Exception as e:
        print(f"Error setting state for {key_name}: {e}")

def insight_exists(insight_id: str) -> bool:
    """
    Check if an insight already exists in the database.
    """
    try:
        response = supabase.table("insights").select("id").eq("id", insight_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error checking existance for {insight_id}: {e}")
        return False

def save_insight(insight_data: dict):
    """
    Save or update an insight.
    """
    try:
        supabase.table("insights").upsert(insight_data).execute()
        print(f"Saved/Updated insight: {insight_data.get('id')}")
    except Exception as e:
        print(f"Error saving insight {insight_data.get('id')}: {e}")
