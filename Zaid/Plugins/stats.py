from ..utils import Zbot
from Zaid import Zaid
from Zaid.Plugins.mongodb.chats_db import get_total_chats
from Zaid.Plugins.mongodb.notes_db import get_total_notes
from Zaid.Plugins.mongodb.filters_db import get_total_filters
from Zaid.Plugins.mongodb.warns_db import get_total_warns
from Zaid.Plugins.mongodb.welcome_db import get_total_welcome




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
    e = get_total_welcome()
    f = get_total_warns()
    await event.reply(f"✘ Current Stats\n‣ Total Notes: {a}\n‣ Total Commands: {b}\n‣ Total Chats: {c}\n‣ Total Filters: {d}\n‣ Welcome: {e}\n\n‣ Total Warned: {f}")
