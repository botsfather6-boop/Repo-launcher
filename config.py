# config.py
import os

class Config:
    """
    Ultimate KarmaReport Pro v3.0 - Configuration Management
    Set these values as Environment Variables on Heroku/VPS.
    """
    
    # --- Telegram API Credentials ---
    # Get these from https://my.telegram.org
    API_ID = int(os.environ.get("API_ID", 38524920)) 
    API_HASH = os.environ.get("API_HASH", "08290d2c8cbd436f3b1c16f082777620")
    
    # --- Bot Credentials ---
    # Get from @BotFather
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8541624692:AAHqY-fw48MThEszRudWJNrkkq5Z7xzIrCw")
    
    # --- Administrative Control ---
    # Your personal Telegram User ID (Get from @userinfobot)
    OWNER_ID = int(os.environ.get("OWNER_ID", 8169571144))
    
    # --- Persistent Storage ---
    # MongoDB Connection String (Get from https://mongodb.com)
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://Karma_h4ree:<db_password>@cluster0.5bs7pao.mongodb.net/?appName=Cluster0")
    
    # --- Logic & Restrictions ---
    # Default minimum sessions required for non-sudo users
    DEFAULT_MIN_SESSIONS = int(os.environ.get("DEFAULT_MIN_SESSIONS", 1))
    
    # Supported command prefixes for the bot
    PREFIX = ["/", "!", "."]
    
    # --- Optimization ---
    # Maximum concurrent session logins during task start
    MAX_CONCURRENT_STARTUP = 5
