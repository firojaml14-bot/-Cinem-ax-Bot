import os

API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "0"))
FORCE_SUB_CHANNELS = os.environ.get("FORCE_SUB_CHANNELS", "") # -100 wale id comma se

ADMINS = [int(x) for x in os.environ.get("ADMINS", "").split() if x]
