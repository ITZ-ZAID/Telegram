from ..utils import Zbot
from Zaid import Zaid
from Zaid.Plugins.mongodb.chats_db import get_total_chats
from Zaid.Plugins.mongodb.notes_db import get_total_notes
from Zaid.Plugins.mongodb.notes_db import get_total_filters



stats_layout = """
<b>Current Stats</b>
<b>•</b> <code>{}</code> total notes
<b>•</b> <code>{}</code> total commands registred
<b>•</b> <code>{}</code> chats
"""



@Zbot(pattern="^/stats ?(.*)")
async def stats(event):
    a = get_total_notes()
    b = len(Zaid.list_event_handlers())
    c = get_total_chats()
    d = get_total_filters()
    await event.reply(f"✘ Current Stats\n‣ Total Notes: {a}\n‣ Total Commands: {b}\n‣ Total Chats: {c}\n‣ Total Filters: {d}")
