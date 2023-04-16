import os
from os import getenv
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
class Config(object):
    log = True
    APP_ID = getenv("API_ID", "28875022")
    API_HASH = getenv("API_HASH", "5b42749c8464a36077e1ab4a12de1eb8")
    TOKEN = getenv("TOKEN", "6140840920:AAF878Muh6rMeC9wkQkoKjAzXUIyNvH6JRs")
    OWNER_ID = getenv("OWNER_ID", "5937212945")
    ASSISTANT_ID = getenv("ASSISTANT_ID", "5937212945")
    STRING_SESSION = getenv("STRING_SESSION", "1BJWap1sBu4JqDsex-C1BDua0-3TVUtPNYa1Vjy5NWWM1-zD4kFEfs660Eia9hE7d137KJmifBwRqUyImfOZtw9UddEYp9t3u4mcGG5ZUYTButIkK_rlPcaumlxXpzuic3sq2ZWt6i91EvazMAjllt3c6Yw3N4vPDFxag0-xVLB2vNcirBh9OmTiz9KR3MtKrlF02Q_0NIaflbdudzhjB-h22dX_wPFyyXjxFl8M0RAn2U8VkM9rpcae7DFRsAUZyCGysIaffqb6iusu5W-wZr_YHAZr1X6h9gvkdSlP8O6RwiIORL_9y3bj9F1uBrLj2FDfs3rnYA9JfKNTJbBjV3pq1qklC_Bg=") #telethon
    OWNER_USERNAME = getenv("OWNER_USERNAME", "cxzsaewm")
    DB_URI = getenv("DATABASE_URL", "mongodb+srv://BS:<password>@cluster0.hjawjqk.mongodb.net/?retryWrites=true&w=majority")
    DB_URI = DB_URI.replace("postgres", "postgresql")
    MESSAGE_DUMP = getenv("MESSAGE_DUMP", "-1001509525202")
    GBAN_LOGS = getenv("GBAN_LOGS", "-1001847260423")
    SYS_ADMIN = getenv("SYS_ADMIN", "1669178360")
    DEV_USERS = getenv("DEV_USERS", "1669178360")
    LOAD = getenv("LOAD")
    WEBHOOK = False
    SPB_MODE = True
    DROP_UPDATES = False
    DEBUG = False
    URL = None
    INFOPIC = True
    CERT_PATH = None
    PORT = 5000
    DEL_CMDS = True
    STRICT_GBAN = True
    BAN_STICKER = getenv("BAN_STICKER", "")
    ALLOW_EXCL = True
    CUSTOM_CMD = False
    CHANNEL = getenv("CHANNEL", "TheUpdatesChannel")
    SUPPORT = getenv("SUPPORT", "TheSupportChat")
    START_IMG = os.environ.get("START_IMG", "https://telegra.ph/file/35a7b5d9f1f2605c9c0d3.png")
    CMD_IMG = os.environ.get("CMD_IMG", "https://telegra.ph/file/66518ed54301654f0b126.png")
    CASH_API_KEY = getenv("CASH_API_KEY", "https://www.alphavantage.co/support/#api-key")
    TIME_API_KEY = getenv("TIME_API_KEY", "https://timezonedb.com/api")
    WALL_API = getenv("WALL_API", "https://wall.alphacoders.com/api.php")
    spamwatch_api = getenv("spamwatch_api", "https://t.me/SpamWatchBot")
    SPAMMERS = getenv("SPAMMERS", "")
    LASTFM_API_KEY = getenv("LASTFM_API_KEY", "https://www.last.fm/api/account/create")
    CF_API_KEY = getenv("CF_API_KEY", "coffehouse.intellivoid.net")
    BOT_API_URL = getenv("BOT_API_URL", "https://api.telegram.org/bot")
    BOT_API_FILE_URL = getenv("BOT_API_FILE_URL", "https://api.telegram.org/file/bot")
    SUDO_USERS = list(map(int, getenv("SUDO_USERS", "1669178360").split()))
    ZAID_USER = list(map(int, getenv("DEV_USERS", "1669178360").split()))
    NO_LOAD = list(map(int, getenv("NO_LOAD", "").split()))
