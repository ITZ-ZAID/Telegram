import sys
import os
import asyncio
import io
from ..utils import Zbot
from Zaid import Zaid
from config import OWNER_ID
from Zaid.Plugins.mongodb.chats_db import get_total_chats, get_all_chat_id
from Zaid.Plugins.mongodb.notes_db import get_total_notes
from Zaid.Plugins.mongodb.filters_db import get_total_filters
from Zaid.Plugins.mongodb.rules_db import get_total_rules
from Zaid.Plugins.mongodb.welcome_db import get_total_welcome
from Zaid.Plugins.mongodb.nightmode_db import get_total_nightmode
from Zaid.Plugins.mongodb.locks_db import get_total_locks

@Zbot(pattern="^/stats ?(.*)", from_users=[OWNER_ID])
async def stats(event):
    a = get_total_notes()
    b = len(Zaid.list_event_handlers())
    c = get_total_chats()
    d = get_total_filters()
    e = get_total_welcome()
    f = get_total_rules()
    g = get_total_nightmode()
    h = get_total_locks()
    await event.reply(f"✘ Current Stats\n‣ Total Notes: {a}\n‣ Total Commands: {b}\n‣ Total Chats: {c}\n‣ Total Filters: {d}\n‣ Welcome: {e}\n‣ Total Rules: {f}\n‣Total Nightmode: {g}\n‣ Total Locks: {h}")



@Zbot(pattern="^/restart$", from_users=[OWNER_ID])
async def restart(e):
    await e.reply("**__Restarting....__**")
    args = [sys.executable, "-m", "Zaid"]
    os.execle(sys.executable, *args, os.environ)



@Zbot(pattern="^/broadcast ?(.*)", from_users=[OWNER_ID])
async def bc(event):
    if not event.sender_id in [OWNER_ID]:
        return await event.reply(
            "You don't have access to use this, visit @TheSupportChat."
        )
    if event.reply_to:
        r = await event.get_reply_message()
        b_text = r.text
        b_file = r.media
    elif event.pattern_match.group(1):
        b_text = event.text.split(None, 1)[1]
        b_file = None
    chats = get_all_chat_id()
    s = f = 0
    for chat in chats:
        try:
            await event.client.send_message(int(chat), b_text, file=b_file)
            s += 1
        except:
            f += 1
    await event.reply(f"Sucessfully broadcasted, Sucess in {s} chats, {f} failed")
