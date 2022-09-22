import time

from telethon import events

from .. import Zaid
from config import OWNER_ID
from . import can_change_info, extract_time
from . import g_time as get_time
from .mongodb import antiflood_db as db

badtime = """
It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode [tban/tmute] <timevalue>`.

Examples of time value: `4m = 4 minutes`, `3h = 3 hours`, `6d = 6 days`, `5w = 5` weeks.
"""
badargs = """
I expected some arguments! Either `off`, or an integer. eg: `/setflood 5`, or `/setflood off`
"""


@Zbot(pattern="^/setfloodmode ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    options = event.pattern_match.group(1)
    if not options:
        return await event.reply(
            "You need to specify an action to take upon flooding. Current modes are: ban/kick/mute/tban/tmute"
        )
    supported = ["ban", "mute", "kick", "tban", "tmute"]
    options = options.split()
    if not options[0] in supported:
        return await event.reply(
            f"Unknown type '{options}'. Please use one of: ban/kick/mute/tban/tmute"
        )
    if options[0] == "ban":
        db.set_flood_strength(event.chat_id, "ban")
        txt = "Banned"
    elif options[0] == "kick":
        db.set_flood_strength(event.chat_id, "kick")
        txt = "Kicked"
    elif options[0] == "mute":
        db.set_flood_strength(event.chat_id, "mute")
        txt = "Muted"
    elif options[0] == "tban":
        if len(options) == 1:
            return await event.reply(badtime)
        time = await extract_time(event, options[1])
        if not time:
            return
        db.set_flood_strength(event.chat_id, "tban", time)
        txt = "temporarly Banned for {}".format(options[1])
    elif options[0] == "tmute":
        if len(options) == 1:
            return await event.reply(badtime)
        time = await extract_time(event, options[1])
        if not time:
            return
        db.set_flood_strength(event.chat_id, "tmute", time)
        txt = "temporarly Muted for {}".format(options[1])
    await event.respond(
        "Updated antiflood reaction in {} to: **{}**".format(event.chat.title, txt)
    )


@Zbot(pattern="^/setflood ?(.*)")
async def _(event):
    if (
        event.text.startswith("/setfloodmode")
        or event.text.startswith("!setfloodmode")
        or event.text.startswith("?setfloodmode")
        or event.text.startswith("+setfloodmode")
    ):
        return
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    if not args:
        return await event.reply(badargs)
    if args == "off":
        db.set_flood(event.chat_id, 0)
        text = "Antiflood has been disabled."
    elif args == "∞":
        db.set_flood(event.chat_id, 0)
        text = "Antiflood has been disabled."
    elif args == "0":
        db.set_flood(event.chat_id, 0)
        text = "Antiflood has been disabled."
    elif args.isdigit():
        if not int(args):
            return await event.reply(f"{args} is not a valid integer.")
        elif int(args) <= 0:
            db.set_flood(event.chat_id, 0)
            text = "Antiflood has been disabled."
        else:
            db.set_flood(event.chat_id, int(args))
            text = f"Antiflood settings for {event.chat.title} have been updated to {int(args)}."
    else:
        return await event.reply(f"{args}is not a valid integer.")
    await event.reply(text)


@Zbot(pattern="^/flood")
async def _(event):
    if event.is_private:
        return  # connect
    limit = db.get_flood_limit(event.chat_id)
    if limit == 0:
        text = "This chat is not currently enforcing flood control."
    else:
        text = f"This chat is currently enforcing flood control after {limit} messages."
    await event.respond(text)


@Zaid.on(events.NewMessage())
async def flood_control(fx):
    if db.get_flood_limit(fx.chat_id) == 0:
        return
    if fx.is_private:
        return
    if not fx.from_id:
        return
    d = db.update_flood(fx.chat_id, fx.sender_id)
    if not d:
        return
    if (
        fx.sender_id == OWNER_ID
        or await is_admin(fx.chat_id, fx.sender_id)
    ):
        return
    suffix = f"Yeah, I don't like yout flooding.\n**{fx.sender.first_name}** has been "
    flmd = db.get_flood_settings(fx.chat_id)
    if flmd[0] == "ban":
        await fx.reply(suffix + "banned!")
        await event.client.edit_permissions(fx.chat_id, fx.sender_id, view_messages=False)
    elif flmd[0] == "kick":
        await fx.reply(suffix + "kicked!")
        await event.client.kick_participant(fx.chat_id, fx.sender_id)
    elif flmd[0] == "mute":
        await fx.reply(suffix + "muted!")
        await event.client.edit_permissions(fx.chat_id, fx.sender_id, send_messages=False)
    elif flmd[0] == "tban":
        await fx.reply(suffix + "banned for " + str(get_time(flmd[1])))
        await event.client.edit_permissions(
            fx.chat_id,
            fx.sender_id,
            view_messages=False,
            until_date=time.time() + flmd[1],
        )
    elif flmd[0] == "tmute":
        await fx.reply(suffix + "muted for " + str(get_time(flmd[1])))
        await event.client.edit_permissions(
            fx.chat_id,
            fx.sender_id,
            view_messages=False,
            until_date=time.time() + flmd[1],
        )
