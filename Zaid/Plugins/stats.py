from ..utils import Zbot
from Zaid import Zaid
from Zaid.Plugins.mongodb.chats_db import get_all_chat_id
from Zaid.Plugins.mongodb.notes_db import get_total_notes



stats_layout = """
<b>Current Stats</b>
<b>•</b> <code>{}</code> total notes
<b>•</b> <code>{}</code> total commands registred
<b>•</b> <code>{}</code> chats
"""



@Zbot(pattern="^/stats ?(.*)")
async def stats(event):
    1 = get_total_notes()
    2 = len(Zaid.list_event_handlers())
    3 = len(get_all_chat_id())
    await event.reply(f"Total Notes: {1}\nTotal Commands: {2}\nTotal Chats: {3}")
