import re
import time

from telethon import Button, events
from telethon.tl.types import PeerChannel

from Zaid import Zaid
from config import OWNER_ID
from Zaid.utils import Zbot, Zinline

from . import DEVS, can_change_info, cb_is_owner, extract_time, is_admin, is_owner
from .mongodb import blacklist_db as db
from .mongodb import warns_db as wsql
from .language import translate

@Zbot(pattern="^/addblocklist ?(.*)")
async def _(event):
    if event.is_private:
        return await event.reply(translate("Thid command is made for group chats, not my PM!", event.chat_id))
    if not event.from_id:
        return
    if not await can_change_info(event, event.sender_id):
        return
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        trigger = msg.text.split(None, 1)[0]
    elif event.pattern_match.group(1):
        trigger = event.text.split(None, 1)[1]
    else:
        return await event.reply(translate(
            "You need to provide a blocklist trigger!\neg: `/addblocklist the admins suck`.", event.chat_id)
        )
    if len(trigger) > 33:
        return await event.reply(translate("The BlackList filter is too long!", event.chat_id))
    text = translate(f"Added blocklist filter '{trigger}'!", event.chat_id)
    db.add_to_blacklist(event.chat_id, trigger)
    await event.reply(text)


@Zbot(pattern="^/addblacklist ?(.*)")
async def _(event):
    if event.is_private:
        return await event.reply(translate("This command is made for group chats, not my PM!", event.chat_id))
    if not event.from_id:
        return
    if not await can_change_info(event, event.sender_id):
        return
    if event.reply_to_msg_id:
        msg = await event.get_reply_message()
        trigger = msg.message
    elif event.pattern_match.group(1):
        trigger = event.text.split(None, 1)[1]
    else:
        return await event.reply(translate(
            "You need to provide a blocklist trigger!\neg: `/addblocklist the admins suck`.", event.chat_id)
        )
    if len(trigger) > 20:
        return await event.reply(translate("The BlackList filter is too long!", event.chat_id))
    text = translate(f"Added blocklist filter '{trigger}'!", event.chat_id)
    db.add_to_blacklist(event.chat_id, trigger)
    await event.reply(text)


@Zbot(pattern="^/(blocklist|blacklist)$")
async def _(event):
    if event.is_private:
        return  # connect
    if not await is_admin(event.chat_id, event.sender_id):
        return await event.reply("You need to be an admin to do this.")
    all_blacklisted = db.get_chat_blacklist(event.chat_id)
    if (all_blacklisted and len(all_blacklisted) == 0) or not all_blacklisted:
        text = translate(f"No blocklist filters active in {event.chat.title}!", event.chat_id)
    else:
        text = translate(f"The following blocklist filters are currently active in {event.chat.title}:", event.chat_id)
        for i in all_blacklisted:
            text += f"\n- `{i}`"
    await event.reply(text)


@Zbot(pattern="^/(rmblacklist|rmblocklist) ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(2)
    if not args:
        return await event.reply(translate("You need to specify the blocklist filter to remove", event.chat_id))
    d = db.rm_from_blacklist(event.chat_id, args)
    if d:
        text = translate(f"I will no longer blocklist '{args}'.", event.chat_id)
    else:
        text = translate(f"`{args}` has not been blocklisted, and so could not be stopped. Use the /blocklist command to see the current blocklist.", event.chat_id)
    await event.reply(text)


@Zbot(pattern="^/(unblocklistall|unblacklistall)$")
async def _(event):
    if event.is_private:
        return  # connect
    if not await is_owner(event, event.sender_id):
        return
    buttons = [Button.inline(translate("Delete blocklist", event.chat_id), data="dabl")], [
        Button.inline(translate("Cancel", event.chat_id), data="cabl")
    ]
    text = translate(f"Are you sure you would like to stop **ALL** of the blocklist in {event.chat.title}? This action cannot be undone.", event.chat_id)
    await event.reply(text, buttons=buttons)


@Zinline(pattern="dabl")
async def dabl(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Deleted all chat blocklist filters.", event.chat_id))
    db.remove_all_blacklist(event.chat_id)


@Zinline(pattern="cabl")
async def cabl(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Removal of the all chat blocklist filters has been cancelled.", event.chat_id))






@Zbot(pattern="^/(blocklistmode|blacklistmode) ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(2)
    if not args:
        mode, time = db.get_mode(event.chat_id)
        if mode == "nothing":
            text = translate("Your current blocklist preference is just to delete messages with blocklisted words.", event.chat_id)
        elif mode == "warn":
            text = translate("Your current blocklist preference is to warn users on messages containing blocklisted words, and delete the message.", event.chat_id)
        elif mode == "ban":
            text = translate("Your current blocklist preference is to ban users on messages containing blocklisted words, and delete the message.", event.chat_id)
        elif mode == "mute":
            text = translate("Your current blocklist preference is to mute users on messages containing blocklisted words, and delete the message.", event.chat_id)
        elif mode == "kick":
            text = translate("Your current blocklist preference is to kick users on messages containing blocklisted words, and delete the message.", event.chat_id)
        elif mode == "tban":
            text = translate("Your current blocklist preference is to tban users on messages containing blocklisted words, and delete the message.", event.chat_id)
        elif mode == "tmute":
            text = translate("Your current blocklist preference is to tmute users on messages containing blocklisted words, and delete the message.", event.chat_id)
        await event.reply(text + translate("If you want to change this setting, you will need to specify an action to take on blocklisted words. Possible modes are: nothing/ban/mute/kick/warn/tban/tmute", event.chat_id))
    else:
        lolz = args
        args = args.split()
        if not args[0] in ["ban", "mute", "kick", "tban", "tmute", "nothing", "warn"]:
            return await event.reply(translate(
                f"Unknown type {args[0]}. Please use one of: nothing/ban/mute/kick/warn/tban/tmute", event.chat_id)
            )
        if args[0] in ["tban", "tmute"]:
            if len(args) == 1:
                return await event.reply(translate("It looks like you tried to set time value for blacklist but you didn't specified  time; try, `/blacklistmode tmute/tban <timevalue>`.\nExamples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.", event.chat_id))
            time = await extract_time(event, args[1])
            db.set_mode(event.chat_id, args[0], time)
            if args[0] == "tban":
                text = translate(f"Changed blacklist mode: temporarily ban for {lolz}!", event.chat_id)
            elif args[0] == "tmute":
                text = translate(f"Changed blacklist mode: temporarily mute for {lolz}!", event.chat_id)
        else:
            db.set_mode(event.chat_id, args[0])
            text = translate(f"Changed blacklist mode: {args[0]} the sender!", event.chat_id)
        await event.reply(text)


@Zaid.on(events.NewMessage(incoming=True))
async def on_new_message(event):
    if event.is_private:
        return
    if not event.from_id:
        return
    if isinstance(event.from_id, PeerChannel) or event.fwd_from or event.media:
        return
    name = event.text
    trigg = False
    snips = db.get_chat_blacklist(event.chat_id)
    if not snips:
        return
    snip_t = ""
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            trigg = True
            snip_t = snip
    if trigg:
        if (
            event.sender_id in DEVS
            or event.sender_id == OWNER_ID
            or await is_admin(event.chat_id, event.sender_id)
        ):
            return  # admins
        await blocklist_action(event, snip_t)


async def blocklist_action(event, name):
    await event.delete()
    mode, ban_time = db.get_mode(event.chat_id)
    if mode == "nothing":
        return
    elif mode == "ban":
        task = "Banned"
        await event.client.edit_permissions(
            event.chat_id, event.sender_id, until_date=None, view_messages=False
        )
    elif mode == "kick":
        task = "Kicked"
        await event.client.kick_participant(event.chat_id, event.sender_id)
    elif mode == "mute":
        task = "Muted"
        await event.client.edit_permissions(
            event.chat_id, event.sender_id, until_date=None, send_messages=False
        )
    elif mode == "tban":
        task = "Banned"
        await event.client.edit_permissions(
            event.chat_id,
            event.sender_id,
            until_date=time.time() + int(ban_time),
            view_messages=False,
        )
    elif mode == "tmute":
        task = "Muted"
        await event.client.edit_permissions(
            event.chat_id,
            event.sender_id,
            until_date=time.time() + int(ban_time),
            send_messages=False,
        )
    elif mode == "warn":
        await bl_warn(
            event.chat_id, event.sender.first_name, event.sender_id, event.id, name
        )
    if mode in ["ban", "mute", "kick", "tban", "tmute"]:
        await event.respond(
            "[{}](tg://user?id={}) has been {}!\nReason: `Automatic blacklist action, due to match on {}`".format(
                event.sender.first_name, event.sender_id, task, name
            )
        )


async def bl_warn(chat_id, first_name, user_id, reply_id, name):
    limit = wsql.get_limit(chat_id)
    num_warns, reasons = wsql.warn_user(
        user_id, chat_id, f"Automatic blocklist action, due to a match on {name}"
    )
    if num_warns < limit:
        await Zaid.send_message(
            chat_id,
            "User [{}](tg://user?id={}) has {}/{} warnings; be careful!.\nReason: `Automatic blacklist action, due to match on {}`".format(
                first_name, user_id, num_warns, limit, name
            ),
            buttons=Button.inline(
                "Remove warn (admin only)", data=f"rm_warn-{user_id}"
            ),
            reply_to=reply_id,
        )
    else:
        wsql.reset_warns(usee_id, chat_id)
        mode = wsql.get_warn_strength(chat_id)
        if mode == "ban":
            task = "Banned"
            await Zaid.edit_permissions(
                chat_id, user_id, until_date=None, view_messages=False
            )
        elif mode == "kick":
            task = "Kicked"
            await Zaid.kick_participant(chat_id, user_id)
        elif mode == "mute":
            task = "Muted"
            await Zaid.edit_permissions(
                chat_id, user_id, until_date=None, send_messages=False
            )
        elif mode == "tban":
            task = "Banned"
            ban_time = int(sql.get_time(event.chat_id))
            await Zaid.edit_permissions(
                chat_id,
                user_id,
                until_date=time.time() + ban_time,
                view_messages=False,
            )
        elif mode == "tmute":
            task = "Muted"
            mute_time = int(sql.get_time(event.chat_id))
            await Zaid.edit_permissions(
                chat_id,
                user_id,
                until_date=time.time() + mute_time,
                send_messages=False,
            )
        await Zaid.send_message(
            chat_id,
            "Thats {}/{} warnings. [{}](tg://user?id={}) has been {}!\nReason: `Automatic blacklist action, due to match on {}`".format(
                limit, limit, first_name, user_id, task, name
            ),
            reply_to=reply_id,
        )


__name__ = "blocklist"

__help__ = """
Blacklists are used to stop certain triggers from being said in a group. Any time the trigger is mentioned, the message will immediately be deleted. A good combo is sometimes to pair this up with warn filters!
*NOTE*: Blacklists do not affect group admins.
 ❍ /blacklist*:* View the current blacklisted words.
Admin only:
 ❍ /addblacklist <triggers>*:* Add a trigger to the blacklist. Each line is considered one trigger, so using different lines will allow you to add multiple triggers.
 ❍ /unblacklist <triggers>*:* Remove triggers from the blacklist. Same newline logic applies here, so you can remove multiple triggers at once.
 ❍ /blacklistmode <off/del/warn/ban/kick/mute/tban/tmute>*:* Action to perform when someone sends blacklisted words.
Blacklist sticker is used to stop certain stickers. Whenever a sticker is sent, the message will be deleted immediately.
*NOTE:* Blacklist stickers do not affect the group admin
 ❍ /blsticker*:* See current blacklisted sticker
*Only admin:*
 ❍ /addblsticker <sticker link>*:* Add the sticker trigger to the black list. Can be added via reply sticker
 ❍ /unblsticker <sticker link>*:* Remove triggers from blacklist. The same newline logic applies here, so you can delete multiple triggers at once
 ❍ /rmblsticker <sticker link>*:* Same as above
 ❍ /blstickermode <ban/tban/mute/tmute>*:* sets up a default action on what to do if users use blacklisted stickers
Note:
 ❍ <sticker link> can be `https://t.me/addstickers/<sticker>` or just `<sticker>` or reply to the sticker message
"""
from .. import CMD_HELP
CMD_HELP.update({__name__: [__name__, __help__]})
