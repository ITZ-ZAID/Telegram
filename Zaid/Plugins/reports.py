from telethon.tl.types import ChannelParticipantsAdmins

from Zaid.utils import Zbot
from .language import translate

from . import can_change_info, get_user, is_admin
from .mongodb import reporting_db as db

Ron = """
Reports are currently enabled in this chat.
Users can use the /report command, or mention @admin, to tag all admins.

To change this setting, try this command again, with one of the following args: yes/no/on/off
"""
Roff = """
Reports are currently disabled in this chat.

To change this setting, try this command again, with one of the following args: yes/no/on/off
"""


@Zbot(pattern="^/reports ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if event.from_id:
        if not await can_change_info(event, event.sender_id):
            return
    args = event.pattern_match.group(1)
    chat = event.chat_id
    if args:
        if args == "on" or args == "yes":
            await event.reply(translate("Users will now be able to report messages.", event.chat_id))
            db.set_chat_setting(chat, True)
        elif args == "off" or args == "no":
            await event.reply(translate(
                "Users will no longer be able to report via @admin or /report.", event.chat_id)
            )
            db.set_chat_setting(chat, False)
        else:
            await event.reply(translate("Your input was not recognised as one of: yes/no/on/off", event.chat_id))
            return
    else:
        if db.chat_should_report(chat):
            await event.reply(translate(f"{Ron}", event.chat_id))
        else:
            await event.reply(translate(f"{Roff}", event.chat_id))


@Zbot(pattern="^/report ?(.*)")
async def _(event):
    if event.is_private:
        return  # add_reply
    if not db.chat_should_report(event.chat_id):
        return
    if await is_admin(event.chat_id, event.sender_id):
        return
    if not event.reply_to and not event.pattern_match.group(1):
        user = event.sender
    else:
        try:
            user, extra = await get_user(event)
        except TypeError:
            pass
    if await is_admin(event.chat_id, event.sender_id):
        return
    text = "Reported <a href='tg://user?id={}'>{}</a> to admins."
    await event.respond(
        text.format(user.id, user.first_name),
        parse_mode="html",
        reply_to=event.reply_to_msg_id or event.id,
    )


@Zbot(pattern="^@admin ?(.*)")
async def I(event):
    if event.is_private:
        return  # add_reply
    if not db.chat_should_report(event.chat_id):
        return
    if await is_admin(event.chat_id, event.sender_id):
        return
    user = None
    if not event.reply_to and not event.pattern_match.group(1):
        user = event.sender
    else:
        try:
            user, extra = await get_user(event)
        except TypeError:
            pass
    if await is_admin(event.chat_id, event.sender_id):
        return
    text = "Reported <a href='tg://user?id={}'>{}</a> to admins."
    await event.respond(
        text.format(user.id, user.first_name),
        parse_mode="html",
        reply_to=event.reply_to_msg_id or event.id,
    )


__help__ = """
 ❍ /report <reason>*:* reply to a message to report it to admins.
 ❍ @admin*:* reply to a message to report it to admins.
*NOTE:* Neither of these will get triggered if used by admins.
*Admins only:*
 ❍ /reports <on/off>*:* change report setting, or view current status.
   • If done in pm, toggles your status.
   • If in group, toggles that groups's status.
"""

__name__ = "reports"


CMD_HELP.update({__name__: [__name__, __help__]})
