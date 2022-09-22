"""Config fill properly"""
import os

API_ID = int(os.environ.get("API_ID", ""))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
DB_URI = os.environ.get("ELEPHANT_SQL", "")
OWNER_ID = int(os.environ.get("OWNER_ID", ""))
BOT_ID = int(os.environ.get("BOT_ID", ""))
