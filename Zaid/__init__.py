from config import API_ID, API_HASH, BOT_TOKEN
from telethon import TelegramClient
import telegram.ext as tg
CMD_HELP = {} 
babe = TelegramClient('Melody', api_id=API_ID, api_hash=API_HASH)
Zaid = babe.start(bot_token=BOT_TOKEN)
updater = tg.Updater(BOT_TOKEN, workers=8, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()
