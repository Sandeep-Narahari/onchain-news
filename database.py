import os
import logging
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

# Base Mainnet Config
BASE_RPC_URL = "https://mainnet.base.org"
USDC_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
TREASURY_ADDRESS = os.getenv("NEXT_PUBLIC_TREASURY_ADDRESS", "0x6baeF23eeb7c09D731095bb5531da50b96b2D9B4") # User Treasury Wallet

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

def get_user_usage_stats(user_address: str):
    """Get usage statistics for the user."""
    try:
        # Total requests
        total = supabase.table("usage_logs").select("id", count="exact").eq("user_address", user_address.lower()).execute()
        
        # Requests in last 24h
        one_day_ago = datetime.now(timezone.utc).timestamp() - 86400
        # Supabase API might strictly need ISO string for gt filter on timestamp, but let's try. 
        # Actually easier to just get recent logs or rely on client side aggregation if volume is low, 
        # but for scalability we should use count queries.
        # For MVP, let's just return total count.
        
        return {
            "total_requests": total.count,
            "plan": "Free" # TODO: Fetch from credits table
        }
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        return {"total_requests": 0, "plan": "Unknown"}

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

# -------------------------------------------------------------------
# User Management
# -------------------------------------------------------------------
def upsert_user(address: str):
    """Create or update a user."""
    try:
        data = {
            "address": address.lower(),
            "last_login": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("users").upsert(data).execute()
        # Ensure free credits entry exists
        supabase.table("credits").upsert(
            {"user_address": address.lower(), "balance": 5}, 
            on_conflict="user_address",
            ignore_duplicates=True
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Error upserting user {address}: {e}")
        return False

def get_user(address: str):
    try:
        response = supabase.table("users").select("*").eq("address", address.lower()).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching user {address}: {e}")
        return None

# -------------------------------------------------------------------
# API Keys
# -------------------------------------------------------------------
def create_api_key(user_address: str, key_hash: str, name: str):
    """Store a new API key."""
    try:
        data = {
            "user_address": user_address.lower(),
            "key_hash": key_hash,
            "name": name,
            "is_active": True
        }
        response = supabase.table("api_keys").insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating API key for {user_address}: {e}")
        return None

def get_user_api_keys(user_address: str):
    try:
        response = supabase.table("api_keys").select("*").eq("user_address", user_address.lower()).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching keys for {user_address}: {e}")
        return []

def revoke_api_key(key_id: str, user_address: str):
    try:
        supabase.table("api_keys").delete().eq("id", key_id).eq("user_address", user_address.lower()).execute()
        return True
    except Exception as e:
        logger.error(f"Error revoking key {key_id}: {e}")
        return False

def validate_api_key(key_hash: str):
    """Check if key exists and is active."""
    try:
        response = supabase.table("api_keys").select("id, user_address, is_active").eq("key_hash", key_hash).execute()
        if response.data:
            key_data = response.data[0]
            if key_data["is_active"]:
                return key_data
        return None
    except Exception as e:
        logger.error(f"Error validating key: {e}")
        return None

# -------------------------------------------------------------------
# Credits & Usage
# -------------------------------------------------------------------
def get_user_credits(user_address: str):
    try:
        response = supabase.table("credits").select("balance").eq("user_address", user_address.lower()).execute()
        return response.data[0]["balance"] if response.data else 0
    except Exception as e:
        logger.error(f"Error getting credits for {user_address}: {e}")
        return 0

def deduct_credit(user_address: str, amount: int = 1):
    """Deduct credits transactionally (simulated pending RPC)."""
    # Note: Supabase-py doesn't support easy decrement without RPC function.
    # For now, we fetch, substract, and update (optimistic concurrency).
    try:
        current = get_user_credits(user_address)
        if current < amount:
            return False
        
        supabase.table("credits").update({"balance": current - amount}).eq("user_address", user_address.lower()).execute()
        return True
    except Exception as e:
        logger.error(f"Error deducting credit for {user_address}: {e}")
        return False

def log_api_usage(api_key_id: str, user_address: str, endpoint: str, status_code: int):
    try:
        supabase.table("usage_logs").insert({
            "api_key_id": api_key_id,
            "user_address": user_address,
            "endpoint": endpoint,
            "status_code": status_code
        }).execute()
    except Exception as e:
        logger.error(f"Error logging usage: {e}")

# -------------------------------------------------------------------
# Payments
# -------------------------------------------------------------------
def add_credits(user_address: str, amount: int):
    """Add credits to a user."""
    try:
        current = get_user_credits(user_address)
        supabase.table("credits").update({"balance": current + amount}).eq("user_address", user_address.lower()).execute()
        return True
    except Exception as e:
        logger.error(f"Error adding credits for {user_address}: {e}")
        return False

def verify_payment_transaction(tx_hash: str, user_address: str):
    """Verify on-chain USDC transaction and credit user."""
    try:
        logger.info(f"Verifying tx {tx_hash} for {user_address}...")
        
        # 1. Check if hash already processed
        res = supabase.table("payments").select("tx_hash").eq("tx_hash", tx_hash).execute()
        if res.data:
            logger.warning("Transaction already processed")
            return {"success": False, "message": "Transaction already processed"}

        # 2. Verify On-Chain
        w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        try:
            tx = w3.eth.get_transaction(tx_hash)
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception as e:
            logger.error(f"Web3 error: {e}")
            return {"success": False, "message": "Transaction not found on Base"}

        if receipt["status"] != 1:
            return {"success": False, "message": "Transaction failed on-chain"}

        # 3. Verify USDC Contract Interaction
        if tx["to"].lower() != USDC_ADDRESS.lower():
             return {"success": False, "message": "Transaction is not valid USDC interaction"}

        # Decode 'transfer(address,uint256)' -> methodId: 0xa9059cbb
        # input data is usually HexBytes
        input_str = tx["input"].hex() if hasattr(tx["input"], "hex") else tx["input"]
        
        # Normalize to 0x prefix
        if not input_str.startswith("0x"):
            input_str = "0x" + input_str
            
        logger.info(f"Input Data: {input_str}")
        
        if not input_str.startswith("0xa9059cbb"):
             logger.error(f"Invalid method ID: {input_str[:10]}")
             return {"success": False, "message": "Not a transfer function call"}
        
        # Extract Destination Address (Param 1)
        # Skip method ID (10 chars) + padding (24 chars) -> Take 40 chars
        to_address_hex = "0x" + input_str[34:74]
        
        # Extract Amount (Param 2)
        # Skip method ID (10 chars) + Param 1 (64 chars) -> Take 64 chars
        amount_hex = "0x" + input_str[74:138]
        amount_wei = int(amount_hex, 16)
        amount_usdc = amount_wei / 1e6 # USDC has 6 decimals
        
        logger.info(f"Tx Details: {amount_usdc} USDC to {to_address_hex}")

        if to_address_hex.lower() != TREASURY_ADDRESS.lower():
             logger.error(f"Wrong destination: {to_address_hex} != {TREASURY_ADDRESS}")
             return {"success": False, "message": f"Payment not sent to Treasury (sent to {to_address_hex})"}

        # 4. Calculate Credits (1 USDC = 100 Credits)
        credits_to_add = int(amount_usdc * 100)
        
        if credits_to_add <= 0:
             return {"success": False, "message": "Amount too small"}

        # 5. Record Payment
        payment_data = {
            "tx_hash": tx_hash,
            "user_address": user_address.lower(),
            "amount_usdc": amount_usdc,
            "credits_added": credits_to_add,
            "status": "confirmed",
            "chain_id": 8453
        }
        supabase.table("payments").insert(payment_data).execute()
        
        # 6. Add Credits
        add_credits(user_address, credits_to_add)
        
        return {"success": True, "credits_added": credits_to_add, "new_balance": get_user_credits(user_address)}

    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        return {"success": False, "message": str(e)}
