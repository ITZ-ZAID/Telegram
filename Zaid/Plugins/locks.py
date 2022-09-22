import datetime
import re

from telethon import events, types
from telethon.tl.types import PeerChannel
from telethon.tl.types import (
    Channel,
    DocumentAttributeAudio,
    DocumentAttributeVideo,
    MessageEntityBankCard,
    MessageEntityBotCommand,
    MessageEntityEmail,
    MessageEntityPhone,
    MessageEntityUrl,
    MessageMediaDice,
    MessageMediaDocument,
    MessageMediaGame,
    MessageMediaGeo,
    MessageMediaGeoLive,
    MessageMediaInvoice,
    MessageMediaPhoto,
    MessageMediaPoll,
    MessageMediaWebPage,
    PeerChannel,
    PeerUser,
    User,
)

from .. import  Zaid, CMD_HELP
from config import BOT_ID
from . import DEVS
from ..utils import Zbot
from . import can_change_info
from . import db as database
from . import is_admin
from .mongodb import locks_db as db
from . import (
    button_parser,
    can_change_info,
    cb_is_owner,
    format_fill,
    get_reply_msg_btns_text,
    is_owner,
)
from .language import translate

approve_d = database.approve_d
from Zaid.Plugins.mongodb.chats_db import is_chat, add_chat


@Zbot(pattern="^/lock ?(.*)")
async def lock_item(event):
    if (
        event.text.startswith("+locks")
        or event.text.startswith("/locks")
        or event.text.startswith("!locks")
        or event.text.startswith("?locks")
        or event.text.startswith("+locktypes")
        or event.text.startswith("/locktypes")
        or event.text.startswith("?locktypes")
        or event.text.startswith("!locktypes")
    ):
        return
    if event.is_private:
        return await event.reply(translate("This command is made to be used in group chats.", event.chat_id))
    if event.is_group and event.from_id:
        if not await can_change_info(event, event.sender_id):
            return
    if not event.pattern_match.group(1):
        return await event.reply(translate("You haven't specified a type to lock.", event.chat_id))
    try:
        lock_items = event.text.split(None, 1)[1]
    except IndexError:
        return await event.reply(translate("You haven't specified a type to lock.", event.chat_id))
    locks = lock_items.split(None)
    lock_s = []
    av_locks = db.all_locks
    for lock in locks:
        if lock.lower() in av_locks:
            lock_s.append(lock)
    if "all" in lock_s:
        db.lock_all(event.chat_id)
        await event.reply("Locked `all`")
        try:
            await event.client.edit_permissions(event.chat_id, send_messages=False)
        except Exception as e:
            print(e)
        return
    if len(lock_s) == 0:
        await event.reply(translate(f"Unknown lock types:- {lock_items}\nCheck /locktypes!", event.chat_id))
    else:
        qp = 0
        text = "Locked"
        if len(lock_s) == 1:
            text += f" `{lock_s[0]}`"
        else:
            for i in lock_s:
                qp += 1
                if len(lock_s) == qp - 1:
                    text += f" `{i}`"
                else:
                    text += f" `{i}`,"
        await event.reply(text)
    for lock in lock_s:
        db.add_lock(event.chat_id, lock.lower())
    if "text" in lock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_messages=False)
        except:
            pass
    if "media" in lock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_media=False)
        except:
            pass
    if "inline" in lock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_inline=False)
        except:
            pass


@Zbot(pattern="^/locktypes")
async def lock_types(event):
    main_txt = translate("The avaliable lock types are:", event.chat_id)
    av_locks = db.all_locks
    for x in av_locks:
        main_txt += "\n- " + x
    await event.reply(main_txt)


@Zbot(pattern="^/locks")
async def locks(event):
    if not await can_change_info(event, event.sender_id):
        return
    av_locks = db.all_locks
    _final = translate("These are the current lock settings:", event.chat_id)
    locked = db.get_locks(event.chat_id) or []
    for x in av_locks:
        _mode = "false"
        if x in locked:
            _mode = "true"
        _final = _final + "\n- " + x + " = " + _mode
    await event.reply(_final)


@Zbot(pattern="^/unlock ?(.*)")
async def unlock_item(event):
    if event.is_private:
        return await event.reply(translate("This command is made to be used in group chats.", event.chat_id))
    if event.is_group and event.from_id:
        if not await can_change_info(event, event.sender_id):
            return
    if not event.from_id:
        return await a_locks(event, "unlock")
    if not event.pattern_match.group(1):
        return await event.reply(translate("You haven't specified a type to unlock.", event.chat_id))
    try:
        unlock_items = event.text.split(None, 1)[1]
    except IndexError:
        return await event.reply(translate("You haven't specified a type to unlock.", event.chat_id))
    unlocks = unlock_items.split(None)
    unlock_s = []
    av_locks = db.all_locks
    for unlock in unlocks:
        if unlock.lower() in av_locks:
            unlock_s.append(unlock)
    if "all" in unlock_s:
        db.unlock_all(event.chat_id)
        await event.reply(translate("Unlocked `all`", event.chat_id))
        try:
            await event.client.edit_permissions(event.chat_id, send_messages=True)
        except:
            pass
        return
    if len(unlock_s) == 0:
        await event.reply(translate(f"Unknown lock types:- {unlock_items}\nCheck /locktypes!", event.chat_id))
    else:
        text = "Unlocked"
        if len(unlock_s) == 1:
            text += f" `{unlock_s[0]}`"
        else:
            for i in unlock_s:
                text += f" `{i}`,"
        await event.reply(text)
    for lock in unlock_s:
        db.remove_lock(event.chat_id, lock.lower())
    if "text" in unlock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_messages=True)
        except:
            pass
    if "media" in unlock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_media=True)
        except:
            pass
    if "inline" in unlock_s:
        try:
            await event.client.edit_permissions(event.chat_id, send_inline=True)
        except:
            pass


@Zaid.on(events.NewMessage())
async def locks(event):
    if event.is_private:
        return
    if not is_chat(event.chat_id):
        add_chat(event.chat_id)
    if not event.from_id:
        return
    if not isinstance(event.sender, User):
        return
    if event.chat.admin_rights:
        if not event.chat.admin_rights.delete_messages:
            return
    else:
        return
    if approve_d.find_one({"user_id": event.sender_id, "chat_id": event.chat_id}):
        return
    locked = db.get_locks(event.chat_id)
    if not locked or len(locked) == 0:
        return
    trigg = await lock_check(event, locked)
    if trigg:
        if not await is_admin(event.chat_id, event.sender_id):
            await event.delete()



async def lock_check(event, locked):
    if "sticker" in locked:
        if event.sticker:
            return True
    if "gif" in locked:
        if event.gif:
            return True
    if "document" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDocument):
                if not event.media.document.mime_type in [
                    "image/webp",
                    "application/x-tgsticker",
                    "image/jpeg",
                    "audio/ogg",
                    "audio/m4a",
                    "audio/mp3",
                    "video/mp4",
                ]:
                    return True
    if "location" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaGeo) or isinstance(
                event.media, MessageMediaGeoLive
            ):
                return True
    if "phone" in locked:
        if event.message.entities:
            if isinstance(event.message.entities[0], MessageEntityPhone):
                return True
    if "email" in locked:
        if event.message.entities:
            if isinstance(event.message.entities[0], MessageEntityEmail):
                return True
    if "command" in locked:
        if event.message.entities:
            if isinstance(event.message.entities[0], MessageEntityBotCommand):
                return True
    if "url" in locked:
        if event.message.entities:
            if isinstance(event.message.entities[0], MessageEntityUrl):
                return True
    if "invitelink" in locked:
        if event.text:
            if "t.me/" in event.text:
                return True
    if "poll" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaPoll):
                return True
    if "photo" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaPhoto):
                return True
    if "videonote" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDocument):
                if event.media.document.mime_type == "video/mp4":
                    return True
    if "video" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDocument):
                if isinstance(
                    event.media.document.attributes[0], DocumentAttributeVideo
                ):
                    return True
    if "voice" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDocument):
                if isinstance(
                    event.media.document.attributes[0], DocumentAttributeAudio
                ):
                    if event.media.document.attributes[0].voice:
                        return True
    if "audio" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDocument):
                if isinstance(
                    event.media.document.attributes[0], DocumentAttributeAudio
                ):
                    return True
    if "bot" in locked:
        if event.sender.bot:
            return True
    if "button" in locked:
        if event.reply_markup:
            return True
    if "game" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaGame):
                return True
    if "contact" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDice):
                return True
    if "forward" in locked:
        if event.fwd_from:
            return True
    if "emojigame" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaDice):
                return True
    if "forwardchannel" in locked:
        if event.fwd_from:
            if event.fwd_from.from_id:
                if isinstance(event.fwd_from.from_id, PeerChannel) or isinstance(
                    event.fwd_from.from_id, Channel
                ):
                    return True
    if "forwarduser" in locked:
        if event.fwd_from:
            if event.fwd_from.from_id:
                if isinstance(event.fwd_from.from_id, PeerUser):
                    return True
    if "preview" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaWebPage):
                return True
    if "forwardbot" in locked:
        if event.fwd_from:
            if event.fwd_from.from_id:
                if event.sender.bot:
                    return True
    if "invoice" in locked:
        if event.media:
            if isinstance(event.media, MessageMediaInvoice):
                return True
    if "comment" in locked:
        return False
    if "card" in locked:
        if event.message.entities:
            for x in range(len(event.message.entities)):
                if isinstance(event.message.entities[x], MessageEntityBankCard):
                    return True
    return False


# --------Album Lock---------
@Zaid.on(events.Album())
async def album(e):
    if e.is_private:
        return
    if not isinstance(e.sender, User):
        return
    if e.chat.admin_rights:
        if not e.chat.admin_rights.delete_messages:
            return
    else:
        return
    if approve_d.find_one({"user_id": e.sender_id, "chat_id": e.chat_id}):
        return
    locked = db.get_locks(e.chat_id)
    if not locked or len(locked) == 0:
        return
    if "album" in locked:
        if not await is_admin(e.chat_id, e.sender_id):
            await e.delete()



__name__ = "locks"
__help__ = """
Here is the help for **Locks** module:
The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!
**Admin commands:**
-> /lock <item(s)>: Lock one or more items. Now, only admins can use this type!
-> /unlock <item(s)>: Unlock one or more items. Everyone can use this type again!
-> /locks: List currently locked items.
-> /lockwarns <yes/no/on/off>: Enabled or disable whether a user should be warned when using a locked item.
-> /locktypes: Show the list of all lockable items.
**Examples:**
- Lock stickers with:
-> /lock sticker
- You can lock/unlock multiple items by chaining them:
-> /lock sticker photo gif video
"""

CMD_HELP.update({__name__: [__name__, __help__]})
