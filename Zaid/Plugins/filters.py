import datetime
import re
from telegram import Update
from Zaid import dispatcher
from telegram.ext import CommandHandler, CallbackQueryHandler
from telethon import events, types
from Zaid.Plugins.mongodb.chats_db import is_chat, add_chat

from .. import Zaid
from config import BOT_ID 
from ..utils import Zbot, Zinline
from . import (
    button_parser,
    can_change_info,
    cb_is_owner,
    format_fill,
    get_reply_msg_btns_text,
    is_owner,
)
from .mongodb import filters_db as db
from .language import translate

def file_ids(msg):
    if isinstance(msg.media, types.MessageMediaDocument):
        file_id = msg.media.document.id
        access_hash = msg.media.document.access_hash
        file_reference = msg.media.document.file_reference
        type = "doc"
    elif isinstance(msg.media, types.MessageMediaPhoto):
        file_id = msg.media.photo.id
        access_hash = msg.media.photo.access_hash
        file_reference = msg.media.photo.file_reference
        type = "photo"
    elif isinstance(msg.media, types.MessageMediaGeo):
        file_id = msg.media.geo.long
        access_hash = msg.media.geo.lat
        file_reference = None
        type = "geo"
    else:
        return None, None, None, None
    return file_id, access_hash, file_reference, type


def id_tofile(file_id, access_hash, file_reference, type):
    if file_id == None:
        return None
    if type == "doc":
        return types.InputDocument(
            id=file_id, access_hash=access_hash, file_reference=file_reference
        )
    elif type == "photo":
        return types.Photo(
            id=file_id,
            access_hash=access_hash,
            file_reference=file_reference,
            date=datetime.datetime.now(),
            dc_id=5,
            sizes=[7108],
        )
    elif type == "geo":
        geo_file = types.InputMediaGeoPoint(
            types.InputGeoPoint(float(file_id), float(access_hash))
        )
        return geo_file


@Zbot(pattern="^/filter ?(.*)")
async def add_filter(event):
    if (
        event.text.startswith("!filters")
        or event.text.startswith("/filters")
        or event.text.startswith("?filters")
        or event.text.startswith("+filters")
    ):
        return
    if event.from_id:
        if not isinstance(event.from_id, types.PeerUser):
            return
    if event.is_group and event.from_id:
        if not await can_change_info(event, event.sender_id):
            return
    file_id = file_reference = access_hash = type = None
    try:
        f_text = event.text.split(None, 1)[1]
    except IndexError:
        f_text = None
    if not event.reply_to and not f_text:
        return await event.reply(translate("You need to give the filter a name!", event.chat_id))
    elif event.reply_to:
        name = f_text
        if not name:
            return await event.reply(translate("You need to give the filter a name!", event.chat_id))
        reply_msg = await event.get_reply_message()
        if reply_msg.media:
            file_id, access_hash, file_reference, type = file_ids(reply_msg)
        if not reply_msg.text and not reply_msg.media:
            return await event.reply(translate("you need to give the filter some content!", event.chat_id))
        reply = reply_msg.text or "Nil"
        if reply_msg.reply_markup:
            reply = reply + get_reply_msg_btns_text(reply_msg)
    elif f_text:
        _total = f_text
        _t = _total.split(None, 1)
        if len(_t) == 1:
            return await event.reply(translate("You need to give the filter some content!", event.chat_id))
        name = _t[0]
        reply = _t[1]
    await event.reply(translate(f"Saved filter `{name}`", event.chat_id))
    db.save_filter(
        event.chat_id, name, reply, file_id, access_hash, file_reference, type
    )


@Zaid.on(events.NewMessage())
async def filter_trigger(event):
    if not is_chat(event.chat_id):
        add_chat(event.chat_id)
    if event.sender_id == int(BOT_ID):
        return
    if (
        event.text.startswith("/filter")
        or event.text.startswith("!filter")
        or event.text.startswith("?filter")
        or event.text.startswith("+filter")
        or event.text.startswith("!stop")
        or event.text.startswith("?stop")
        or event.text.startswith("+stop")
        or event.text.startswith("/stop")
    ):
        return
    name = event.text
    snips = db.get_all_filters(event.chat_id)
    if not snips:
        return
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            filter = snips[snip]
            file = id_tofile(
                filter["id"], filter["hash"], filter["ref"], filter["mtype"]
            )
            caption = buttons = None
            if filter["reply"] and filter["reply"] != "Nil":
                caption, buttons = button_parser(filter["reply"])
            link_prev = False
            if caption and "{preview}" in caption:
                caption = caption.replace("{preview}")
                link_prev = True
            tm = 0
            if caption:
                caption = await format_fill(event, caption, tm)
            await event.respond(
                caption,
                file=file,
                buttons=buttons,
                link_preview=link_prev,
                reply_to=event.id,
            )

# Because Replying two times
def filters(update: Update, _) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    snips = db.get_all_filters(chat.id)
    if snips:
        tr = translate("Filters in", chat.id)
        text = "<b>{} {}:</b>".format(tr, chat.title)
        for snip in snips:
            text += "\n- <code>{}</code>".format(snip)
        msg.reply_text(text, parse_mode="html")
    else:
        msg.reply_text(translate(f"No filters in {chat.title}!", chat.id))


@Zbot(pattern="^/stop ?(.*)")
async def estop(event):
    if (
        event.text.startswith("+stopall")
        or event.text.startswith("/stopall")
        or event.text.startswith("?stopall")
        or event.text.startswith("!stopall")
    ):
        return
    try:
        name = event.text.split(None, 1)[1]
    except IndexError:
        name = None
    if not name:
        return await event.reply(translate("Not enough arguments provided.", event.chat_id))
    f_exist = db.get_filter(event.chat_id, name)
    if f_exist:
        await event.reply(translate(f"Filter `'{name}'` has been stopped!", event.chat_id))
        return db.delete_filter(event.chat_id, name)
    await event.reply(translate("You haven't saved any filters on this word yet!", event.chat_id))


@Zbot(pattern="^/stopall")
async def delallfilters(event):
    if event.is_private:
        return
    if event.is_group:
        if event.from_id:
            if not await is_owner(event, event.sender_id):
                return
    buttons = [
        [Button.inline(translate("Delete all filters", event.chat_id), data="stopall")],
        [Button.inline(translate("Cancel", event.chat_id), data="cancelstopall")],
    ]
    text = translate(f"Are you sure you would like to stop **ALL** filters in {event.chat.title}? This action cannot be undone.", event.chat_id)
    await event.reply(text, buttons=buttons)


@Zinline(pattern="stopall")
async def stopallcb(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Deleted all chat filters.", event.chat_id), buttons=None)
    db.delete_all_filters(event.chat_id)


@Zinline(pattern="cancelstopall")
async def stopallcb(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Stopping of all filters has been cancelled.", event.chat_id), buttons=None)


FIKTERS = CommandHandler("filters", filters)
dispatcher.add_handler(FIKTERS)
