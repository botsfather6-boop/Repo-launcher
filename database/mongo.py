# database/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

# --- Database Initialization ---
# Connecting to MongoDB Atlas using the URL from Config
client = AsyncIOMotorClient(Config.MONGO_URL)
db = client["startlove"]  # Using the requested database name 'startlove'

# --- Collection Definitions ---
sessions_db = db["sessions"]
sudo_db = db["sudo_users"]
settings_db = db["settings"]

# --- Session Management Logic ---

async def add_session(user_id: int, session_str: int):
    """
    Saves a session string to the database.
    Uses 'update_one' with 'upsert' to prevent duplicate session entries for the same user.
    """
    await sessions_db.update_one(
        {"user_id": user_id, "session": session_str},
        {"$set": {"user_id": user_id, "session": session_str}},
        upsert=True
    )

async def get_sessions(user_id: int):
    """
    Retrieves all session strings associated with a specific Telegram user ID.
    """
    cursor = sessions_db.find({"user_id": user_id})
    return [s["session"] async for s in cursor]

async def delete_all_sessions(user_id: int):
    """
    Completely wipes all session data for a specific user from the database.
    """
    await sessions_db.delete_many({"user_id": user_id})

# --- Sudo/Permission Management ---

async def add_sudo(user_id: int):
    """Adds a user to the Sudo list, giving them bypass permissions."""
    await sudo_db.update_one(
        {"user_id": user_id}, 
        {"$set": {"user_id": user_id}}, 
        upsert=True
    )

async def remove_sudo(user_id: int):
    """Revokes Sudo permissions from a user."""
    await sudo_db.delete_one({"user_id": user_id})

async def is_sudo(user_id: int):
    """
    Checks if a user has Sudo privileges. 
    Owner ID from config is automatically granted Sudo status.
    """
    if user_id == Config.OWNER_ID:
        return True
    sudo = await sudo_db.find_one({"user_id": user_id})
    return sudo is not None

async def get_all_sudos():
    """Fetches a list of all numeric IDs in the Sudo collection."""
    cursor = sudo_db.find({})
    return [s["user_id"] async for s in cursor]

# --- Global Bot Configuration Management ---

async def get_bot_settings():
    """
    Fetches global settings like 'Force Subscribe' and 'Min Sessions'.
    If no settings exist, it initializes the database with default values.
    """
    settings = await settings_db.find_one({"id": "bot_config"})
    if not settings:
        default = {
            "id": "bot_config",
            "min_sessions": Config.DEFAULT_MIN_SESSIONS,
            "force_sub": None
        }
        await settings_db.insert_one(default)
        return default
    
    # Reliability Fix: Ensure keys exist even if document was modified manually
    if "min_sessions" not in settings: settings["min_sessions"] = Config.DEFAULT_MIN_SESSIONS
    if "force_sub" not in settings: settings["force_sub"] = None
    
    return settings

async def update_bot_settings(updates: dict):
    """
    Updates global configuration values.
    Uses 'upsert' to ensure the document exists during the update.
    """
    await settings_db.update_one(
        {"id": "bot_config"}, 
        {"$set": updates}, 
        upsert=True
    )
