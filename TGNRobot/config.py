# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    API_ID = "6435225"  
    API_HASH = "4e984ea35f854762dcde906dce426c2d"
    TOKEN = ""
    OWNER_ID = "1669178360"
    OWNER_USERNAME = "Timesisnotwaiting"
    MONGO_DB_URI = ""
    MONGO_DB = "ZaidRobot"
    SUPPORT_CHAT = "Superior_Support"
    JOIN_LOGGER = "-1001565570457"
    EVENT_LOGS = "-1001565570457"

    # RECOMMENDED
    INFOPIC = "https://telegra.ph/file/be24bbabbe0ec30dff489.jpg"   
    CF_API_KEY = ""
    LASTFM_API_KEY = ""
    BOT_USERNAME = "TGN_RO_BOT"
    WALL_API = ""
    OPENWEATHERMAP_ID = ""
    TEMP_DOWNLOAD_DIRECTORY = ""
    REM_BG_API_KEY = ""
    TIME_API_KEY = ""
    CASH_API_KEY = ""
    REM_BG_API_KEY = ""
    ARQ_API_KEY = "UIUXOY-NTKWDC-QHFFMD-DHHKVV-ARQ"
    ARQ_API = "UIUXOY-NTKWDC-QHFFMD-DHHKVV-ARQ"
    ARQ_API_URL = "aww"
    HEROKU_APP_NAME = ""
    HEROKU_API_KEY = ""
    BOT_ID = "1901951380"
    STRING_SESSION = ""
    SESSION_STRING = ""
    SQLALCHEMY_DATABASE_URI = ""
    DATABASE_URL = ""
    LOAD = []
    NO_LOAD = ["rss", "cleaner", "connection", "math"]
    WEBHOOK = False
    INFOPIC = True
    URL = None
    SPAMWATCH_API = ""  # go to support.spamwat.ch to get key
    SPAMWATCH_SUPPORT_CHAT = "@SpamWatchSupport"

    # OPTIONAL
    ##List of id's -  (not usernames) for users which have sudo access to the bot.
    DRAGONS = "1669178360"
    ##List of id's - (not usernames) for developers who will have the same perms as the owner
    DEV_USERS = "1669178360"
    ##List of id's (not usernames) for users which are allowed to gban, but can also be banned.
    DEMONS = "1669178360"
    # List of id's (not usernames) for users which WONT be banned/kicked by the bot.
    TIGERS = "1669178360"
    WOLVES = "1669178360"
    DONATION_LINK = None  # EG, paypal
    CERT_PATH = None
    PORT = 5000
    ALLOW_CHATS = True
    DEL_CMDS = True  # Delete commands that users dont have access to, like delete /ban if a non admin uses it.
    STRICT_GBAN = True
    WORKERS = (
        8  # Number of subthreads to use. Set as number of threads your processor uses
    )
    BAN_STICKER = ""  # banhammer marie sticker id, the bot will send this sticker before banning or kicking a user in chat.
    ALLOW_EXCL = True  # Allow ! commands as well as / (Leave this to true so that blacklist can work)
    CASH_API_KEY = (
        "awoo"  # Get your API key from https://www.alphavantage.co/support/#api-key
    )
    TIME_API_KEY = "awoo"  # Get your API key from https://timezonedb.com/api
    WALL_API = (
        "awoo"  # For wallpapers, get one from https://wall.alphacoders.com/api.php
    )
    AI_API_KEY = "awoo"  # For chatbot, get one from https://coffeehouse.intellivoid.net/dashboard
    BL_CHATS = []  # List of groups that you want blacklisted.
    SPAMMERS = None


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
