import logging
import os
import sys
import time
from typing import List
import spamwatch
import telegram.ext as tg
from telethon import TelegramClient
from telethon.sessions import MemorySession
from configparser import ConfigParser
from ptbcontrib.postgres_persistence import PostgresPersistence
from logging.config import fileConfig
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.sessions import MemorySession
from config import Config
from pytgcalls import PyTgCalls
StartTime = time.time()


flag = """💖"""

def get_user_list(key):
    # Import here to evade a circular import
    from Telegram.modules.sql import nation_sql
    royals = nation_sql.get_royals(key)
    return [a.user_id for a in royals]

# enable logging

fileConfig('logging.ini')

#print(flag)
log = logging.getLogger('[Telethon]')
logging.getLogger('ptbcontrib.postgres_persistence.postgrespersistence').setLevel(logging.WARNING)
log.info("[TELEGRAM] Bot is starting. | An Telethon Project. | Licensed under GPLv3.")
log.info("[TELEGRAM] Not affiliated to Azur Lane or Yostar in any way whatsoever.")
log.info("[TELEGRAM] Project maintained by: github.com/ITZ-ZAID (t.me/Timesisnotwaiting)")

# if version < 3.6, stop bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 7:
    log.error(
        "[TELEGRAM] You MUST have a python version of at least 3.7! Multiple features depend on this. Bot quitting."
    )
    quit(1)

parser = ConfigParser()
parser.read("config.ini")
zconfig = parser["zaidconfig"]

class AnieINIT:
    def __init__(self, parser: ConfigParser):
        self.parser = parser
        self.SYS_ADMIN: int = self.parser.getint('SYS_ADMIN', 0)
        self.OWNER_ID: int = self.parser.getint('OWNER_ID')
        self.STRING_SESSION: str = self.parser.get("STRING_SESSION") 
        self.OWNER_USERNAME: str = self.parser.get('OWNER_USERNAME', None)
        self.APP_ID: str = self.parser.getint("APP_ID")
        self.API_HASH: str = self.parser.get("API_HASH")
        self.WEBHOOK: bool = self.parser.getboolean('WEBHOOK', False)
        self.URL: str = self.parser.get('URL', None)
        self.CERT_PATH: str = self.parser.get('CERT_PATH', None)
        self.PORT: int = self.parser.getint('PORT', None)
        self.INFOPIC: bool = self.parser.getboolean('INFOPIC', True)
        self.DEL_CMDS: bool = self.parser.getboolean("DEL_CMDS", False)
        self.STRICT_GBAN: bool = self.parser.getboolean("STRICT_GBAN", False)
        self.ALLOW_EXCL: bool = self.parser.getboolean("ALLOW_EXCL", False)
        self.CUSTOM_CMD: List[str] = ['/', '!']
        self.BAN_STICKER: str = self.parser.get("BAN_STICKER", True)
        self.TOKEN: str = self.parser.get("TOKEN")
        self.DB_URI: str = self.parser.get("SQLALCHEMY_DATABASE_URI")
        self.LOAD = self.parser.get("LOAD").split()
        self.LOAD: List[str] = list(map(str, self.LOAD))
        self.MESSAGE_DUMP: int = self.parser.getint('MESSAGE_DUMP', None)
        self.GBAN_LOGS: int = self.parser.getint('GBAN_LOGS', None)
        self.NO_LOAD = self.parser.get("NO_LOAD").split()
        self.NO_LOAD: List[str] = list(map(str, self.NO_LOAD))
        self.spamwatch_api: str = self.parser.get('spamwatch_api', None)
        self.CASH_API_KEY: str = self.parser.get('CASH_API_KEY', None)
        self.TIME_API_KEY: str = self.parser.get('TIME_API_KEY', None)
        self.WALL_API: str = self.parser.get('WALL_API', None)
        self.LASTFM_API_KEY: str = self.parser.get('LASTFM_API_KEY', None)
        self.CF_API_KEY: str =  self.parser.get("CF_API_KEY", None)
        self.bot_id = 0 #placeholder
        self.bot_name = "Anie" #placeholder
        self.bot_username = "AnieRobot_bot" #placeholder
        self.DEBUG: bool = self.parser.getboolean("IS_DEBUG", False)
        self.DROP_UPDATES: bool = self.parser.getboolean("DROP_UPDATES", True)
        self.BOT_API_URL: str = self.parser.get('BOT_API_URL', "https://api.telegram.org/bot")
        self.BOT_API_FILE_URL: str = self.parser.get('BOT_API_FILE_URL', "https://api.telegram.org/file/bot")


    def init_sw():
        if Config.spamwatch_api is None:
            log.warning("SpamWatch API key is missing! Check your config.ini")
            return None
        else:
            try:
                sw = spamwatch.Client(spamwatch_api)
                return sw
            except:
                sw = None
                log.warning("Can't connect to SpamWatch!")
                return sw


ZInit = Config
ZZInit = AnieINIT
ZAID_USER = 1669178360
SYS_ADMIN = ZInit.SYS_ADMIN
OWNER_ID = ZInit.OWNER_ID
OWNER_USERNAME = ZInit.OWNER_USERNAME
APP_ID = ZInit.APP_ID
API_HASH = ZInit.API_HASH
WEBHOOK = ZInit.WEBHOOK
URL = ZInit.URL
CERT_PATH = ZInit.CERT_PATH
PORT = ZInit.PORT
INFOPIC = ZInit.INFOPIC
DEL_CMDS = ZInit.DEL_CMDS
ALLOW_EXCL = ZInit.ALLOW_EXCL
CUSTOM_CMD = ZInit.CUSTOM_CMD
BAN_STICKER = ZInit.BAN_STICKER
TOKEN = ZInit.TOKEN
DB_URI = ZInit.DB_URI
LOAD = ZInit.LOAD
MESSAGE_DUMP = ZInit.MESSAGE_DUMP
GBAN_LOGS = ZInit.GBAN_LOGS
NO_LOAD = ZInit.NO_LOAD
SUDO_USERS = [Config.SUDO_USERS] + get_user_list("sudos")
DEV_USERS = [Config.ZAID_USER] + get_user_list("devs")
SUPPORT_USERS = get_user_list("supports")
SARDEGNA_USERS = get_user_list("sardegnas")
WHITELIST_USERS = get_user_list("whitelists")
SPAMMERS = get_user_list("spammers")
spamwatch_api = ZInit.spamwatch_api
CASH_API_KEY = ZInit.CASH_API_KEY
TIME_API_KEY = ZInit.TIME_API_KEY
WALL_API = ZInit.WALL_API
LASTFM_API_KEY = ZInit.LASTFM_API_KEY
CF_API_KEY = ZInit.CF_API_KEY

# SpamWatch
sw = ZZInit.init_sw()

API_HASH = '4e984ea35f854762dcde906dce426c2d'
API_ID = '6435225'
STRING_SESSION = ZInit.STRING_SESSION
WORKERS = 8
ASSISTANT_ID = ZInit.ASSISTANT_ID

from Telegram.modules.sql import SESSION

updater = tg.Updater(TOKEN, workers=WORKERS, use_context=True)
telethn = TelegramClient(MemorySession(), APP_ID, API_HASH)
if STRING_SESSION:
   ubot2 = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
else: 
   ubot2 = None

client = ubot2
call_py = PyTgCalls(ubot2)
try:
    ubot2.start()
    call_py.start()
except BaseException:
    print("WARNING ⚠️ ! Have you added a STRING_SESSION in deploying?? Some modules are affect")
    sys.exit(1)

dispatcher = updater.dispatcher



from Telegram.modules.helper_funcs.handlers import CustomCommandHandler

if CUSTOM_CMD and len(CUSTOM_CMD) >= 1:
    tg.CommandHandler = CustomCommandHandler


def spamfilters(text, user_id, chat_id):
    # print("{} | {} | {}".format(text, user_id, chat_id))
    if int(user_id) not in SPAMMERS:
        return False

    print("This user is a spammer!")
    return True
