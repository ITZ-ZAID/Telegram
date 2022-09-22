from telethon import Button
from telethon.errors import ChatAdminRequiredError
from telethon.tl.types import InputMessagePinned


from Zaid.utils import Zbot, Zinline
from config import OWNER_ID

from Zaid import Zaid
from . import button_parser, can_pin_messages, cb_is_owner, is_owner
from .language import translate

@Zbot(pattern="^/pinned$")
async def _(event):
    if event.is_private:
        return  # connect
    x = await event.reply(translate("`Getting the pinned message..`", event.chat_id))
    try:
        async for msg in event.client.iter_messages(
            event.chat_id, ids=InputMessagePinned(), limit=1
        ):
            if msg == None:
                return await x.edit(translate("There are no pinned messages in this chat.", event.chat_id))
            id = msg.id
    except ChatAdminRequiredError:
        return await x.edit(translate("There are no pinned messages in this chat.", event.chat_id))
    if event.chat.username:
        mmm = translate("The Pinned Messages are", event.chat_id)
        await x.edit(
            f"{mmm} **[Here]**(http://t.me/{event.chat.username}/{id}).",
            link_preview=False,
        )
    else:
        chat_id = (str(event.chat_id)).replace("-100", "")
        fa = translate("The Pinned Messages are", event.chat_id)
        await x.edit(
            f"{fa} **[here]**(http://t.me/c/{chat_id}/{id}).",
            link_preview=False,
        )


@Zbot(pattern="^/pin ?(.*)")
async def _(event):
    virulent = ["silent", "violent", "notify", "loud", "quiet"]
    if (
        event.text.startswith("?pinned")
        or event.text.startswith("!pinned")
        or event.text.startswith("/pinned")
        or event.text.startswith("+pinned")
        or event.text.startswith("!ping")
        or event.text.startswith("?ping")
        or event.text.startswith("/ping")
        or event.text.startswith("+ping")
    ):
        return
    if event.is_private:
        return  # connect
    if not event.sender_id == OWNER_ID or event.sender_id in ELITES:
        if not await can_pin_messages(event, event.sender_id):
            return
    if not event.reply_to_msg_id:
        return await event.reply(translate("You need to reply to a message to pin it!", event.chat_id))
    reply_msg = await event.get_reply_message()
    options = event.pattern_match.group(1)
    if options and options not in virulent:
        return await event.reply(translate(
            f"'{options}' was not recognised as a valid pin option. Please use one of: loud/violent/notify/silent/quiet", event.chat_id)
        )
    is_silent = True
    if options == "silent" or options == "quiet":
        is_silent = False
    chat = (str(event.chat_id)).replace("-100", "")
    ths = translate("this message", event.chat_id)
    nm = translate("I have pinned", event.chat_id)
    sz = translate("and notified to all the users", event.chat_id)
    text = f"{nm} [{ths}](t.me/c/{chat}/{reply_msg.id})."
    if options == "notify":
        text = f"{nm} [{ths}](t.me/c/{chat}/{reply_msg.id}). {sz}."
    try:
        await event.client.pin_message(event.chat_id, reply_msg.id, notify=is_silent)
        if is_silent:
            await event.respond(text, reply_to=reply_msg.id)
    except:
        await event.reply(translate(
            f"Looks like I dont have permission to pin messages. Could you please promote me?", event.chat_id)
        )


@Zbot(pattern="^/unpin(:?|$) ?(.*)")
async def _(event):
    if (
        event.text.startswith("?unpinall")
        or event.text.startswith("!unpinall")
        or event.text.startswith("/unpinall")
        or event.text.startswith("+unpinall")
    ):
        return
    if event.is_private:
        return  # connect
    if not await can_pin_messages(event, event.sender_id):
        return
    if not event.reply_to_msg_id:
        msg = await event.client.get_messages(event.chat_id, ids=InputMessagePinned())
        if not msg:
            return await event.reply(translate(
                "Failed to get the last pinned messages, Reply to the message!", event.chat_id)
            )
        id = msg.id
        text = f"I have unpinned the last pinned message."
    else:
        reply = await event.get_reply_message()
        id = reply.id
        chat = (str(event.chat_id)).replace("-100", "")
        hshs = translate("I have unpinned this message", event.chat_id)
        text = f"[{hshs}](t.me/c/{chat}/{reply.id})."
    try:
        await event.client.unpin_message(event.chat_id, id)
        await event.reply(text)
    except:
        await event.reply(translate(
            f"Looks like I dont have permission to pin messages. Could you please promote me?", event.chat_id)
        )


@Zbot(pattern="^/permapin ?(.*)")
async def _(event):
    args = event.pattern_match.group(1)
    if event.is_private:
        return  # connect
    if not event.sender_id == OWNER_ID or event.sender_id in ELITES:
        if not await can_pin_messages(event, event.sender_id):
            return
    if not args and not event.reply_to_msg_id:
        return await event.reply(translate("You need to give some message content to pin!", event.chat_id))
    is_silent = True
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        lolz = await event.respond(reply_msg)
        msg_id = lolz.id
        if args == "silent" or args == "quiet":
            is_silent = False
    elif not event.reply_to_msg_id and args:
        txt = (
            event.text[len("?permapin ") :]
            or event.text[len("!permapin ") :]
            or event.text[len("/permapin ") :]
        )
        buttons = None
        text, buttons = button_parser(txt)
        reply_msg = await event.respond(text, buttons=buttons)
        msg_id = reply_msg.id
    try:
        await event.client.pin_message(event.chat_id, msg_id, notify=is_silent)
    except:
        await event.reply(translate(
            "Looks like I dont have permission to pin messages. Could you please promote me?", event.chat_id)
        )


@Zbot(pattern="^/unpinall")
async def upinall(event):
    if event.is_private:
        return  # connect
    if event.sender_id == OWNER_ID:
        pass
    elif await is_owner(event, event.sender_id):
        pass
    else:
        return
    text = translate("Are you sure you want to unpin all messages?", event.chat_id)
    buttons = [Button.inline(translate("Yes", event.chat_id), data="upin"), Button.inline(translate("No", event.chat_id), data="cpin")]
    await event.respond(text, buttons=buttons)


@Zinline(pattern=r"cpin")
async def start_again(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Unpin of all pinned messages has been cancelled.", event.chat_id), buttons=None)


@Zinline(pattern=r"upin")
async def start_again(event):
    if not await cb_is_owner(event, event.sender_id): 
        return
    await event.edit(translate("All pinned messages have been unpinned.", event.chat_id), buttons=None)
    await event.client.unpin_message(event.chat_id)
