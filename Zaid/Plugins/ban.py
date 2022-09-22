import time

from telethon import Button, events
from telethon.tl.types import Channel

from Zaid import Zaid
from Zaid.utils import Zbot, Zinline

from Zaid.Plugins import DEVS, can_ban_users, cb_can_ban_users
from Zaid.Plugins import extract_time, g_time, get_user, is_admin
from .language import translate

db = {}


async def excecute_operation(
    event,
    user_id,
    name,
    mode,
    reason="",
    tt=0,
    reply_to=None,
    cb=False,
    actor_id=777000,
    actor="Anonymous",
):
    if reply_to == event.id:
        reply_to = event.reply_to_msg_id or event.id
    r = ""
    rea = translate("Reason", event.chat_id)
    if reason:
        r = f"\n{rea}: <code>{reason}</code>"
    if name:
        name = ((name).replace("<", "&lt;")).replace(">", "&gt;")
    if event.chat.admin_rights:
        if not event.chat.admin_rights.ban_users:
            return await event.reply(translate("I haven't got the rights to do this.", event.chat_id))
    if user_id in DEVS and mode in ["ban", "tban", "mute", "tmute", "kick"]:
        return await event.reply(translate("Sorry, I can't act against my devs!", event.chat_id))
    if mode == "ban":
        await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, view_messages=False
        )
        if cb:
            await event.delete()
            reply_to = None
        await event.respond(
            f'{translate("Another one bites the dust...! Banned", event.chat_id)} <a href="tg://user?id={user_id}">{name}</a></b>.{r}',
            parse_mode="html",
            reply_to=reply_to,
        )
    elif mode == "kick":
        await event.client.kick_participant(event.chat_id, int(user_id))
        if cb:
            await event.delete()
            reply_to = None
        await event.respond(
            f'{translate("I have kicked", event.chat_id)} <a href="tg://user?id={user_id}">{name}</a></b>.{r}',
            parse_mode="html",
            reply_to=reply_to,
        )
    elif mode == "mute":
        await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, send_messages=False
        )
        if cb:
            await event.delete()
            reply_to = None
        await event.respond(
            f'{translate("Shhh... quiet now. Muted", event.chat_id)}\n <a href="tg://user?id={user_id}">{name}</a>.{r}',
            parse_mode="html",
            reply_to=reply_to,
        )
    elif mode == "tban":
        if cb:
            await event.delete()
            reply_to = None
        await event.respond(
            f'{translate("Banned", event.chat_id)} <a href="tg://user?id={user_id}">{name}</a> for {g_time(int(tt))}!',
            parse_mode="html",
            reply_to=reply_to,
        )
        await event.client.edit_permissions(
            event.chat_id,
            int(user_id),
            until_date=time.time() + int(tt),
            view_messages=False,
        )
    elif mode == "tmute":
        if cb:
            await event.delete()
            reply_to = None 
        text = translate("Shhh... quiet now. Muted", event.chat_id)
        await event.respond(
            f"{text} <a href='tg://user?id={user_id}'>{name}</a> for{g_time(int(tt))}.{r}",
            parse_mode="html",
            reply_to=reply_to,
        )
        await event.client.edit_permissions(
            event.chat_id,
            int(user_id),
            until_date=time.time() + int(tt),
            send_messages=False,
        )
    elif mode == "unmute":
        if cb:
            await event.delete()
            reply_to = None
        await event.respond(
            f'{translate("Admin", event.chat_id)} <a href="tg://user?id={actor_id}">{actor}</a> {translate("unmuted", event.chat_id)} <a href="tg://user?id={user_id}">{name}</a>! {r}',
            parse_mode="html",
            reply_to=reply_to,
        )
        unmute = await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, send_messages=True
        )
    elif mode == "unban":
        if cb:
            await event.delete()
            reply_to = None
        muted = translate("can join again", event.chat_id)
        mue = translate("Unbaned by", event.chat_id)
        await event.respond(
            f"Yep! <b><a href='tg://user?id={user_id}'>{name}</a></b> (<code>1799400540</code>) {muted}!\n<b> {mue}:</b> <a href='tg://user?id={actor_id}'>{actor}</a>",
            reply_to=reply_to,
            parse_mode="html",
        )
        await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, view_messages=True
        )
    elif mode == "sban":
        ban = await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, view_messages=False
        )
    elif mode == "smute":
        mute = await event.client.edit_permissions(
            event.chat_id, int(user_id), until_date=None, send_messages=False
        )
    elif mode == "skick":
        await event.client.kick_participant(event.chat_id, int(user_id))


@Zbot(pattern="^/dban ?(.*)")
async def dban(event):
    if event.is_private:
        return await event.reply(translate("This command is made to be used in group chats, not in pm!", event.chat_id))
    if not event.from_id:
        return await a_ban(event, "dban")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if event.chat.admin_rights.delete_messages:
            await reply_msg.delete()
    else:
        return await event.reply(translate("You have to reply to a message to delete it and ban the user.", event.chat_id))
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate("Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id))
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I unmute an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "ban",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/ban ?(.*)")
async def ban(event):
    if (
        event.text.startswith("!banme")
        or event.text.startswith("/banme")
        or event.text.startswith(".banme")
        or event.text.startswith("?banme")
    ):
        return
    if event.is_private:
        return await event.reply(translate("This command is made to be used in group chats, not in pm!", event.chat_id))
    if not event.from_id:
        return await a_ban(event, "ban")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate("Maybe it's a channel Try /cban.", event.chat_id))
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I ban an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "ban",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/sban ?(.*)")
async def ban(event):
    if event.is_private:
        return await event.reply(translate("This command is made to be used in group chats, not in pm!", event.chat_id))
    if not event.from_id:
        return await a_ban(event, "sban")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate("Maybe it's a channel Try /cban", event.chat_id))
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I ban an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "sban",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/unban ?(.*)")
async def unban(event):
    if (
        event.text.startswith(".unbanall")
        or event.text.startswith("?unbanall")
        or event.text.startswith("/unbanall")
        or event.text.startswith("!unbanall")
    ):
        return
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "unban")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate("It's seems like a Channel use /cunban", event.chat_id))
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I unban an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "unban",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/dmute ?(.*)")
async def dmute(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "dmute")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if event.chat.admin_rights.delete_messages:
            await reply_msg.delete()
    else:
        return await event.reply(translate("You have to reply to a message to delete it and mute the user.", event.chat_id))
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I mute an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "mute",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/mute ?(.*)")
async def mute(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "mute")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I mute an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "mute",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/smute ?(.*)")
async def smute(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "smute")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate(
            "Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate(
            "Why would I mute an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "smute",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/unmute ?(.*)")
async def unmute(event):
    if (
        event.text.startswith(".unmuteall")
        or event.text.startswith("?unmuteall")
        or event.text.startswith("/unmuteall")
        or event.text.startswith("!unmuteall")
    ):
        return
    if not event.from_id:
        return await a_ban(event, "unmute")
    if event.is_private:
        return
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I unmute an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "unmute",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/dkick ?(.*)")
async def dkick(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "kick")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if event.chat.admin_rights.delete_messages:
            await reply_msg.delete()
    else:
        return await event.reply(translate("You have to reply to a message to delete it and kick the user.", event.chat_id))
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "kick",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/(kick|punch) ?(.*)")
async def kick(event):
    if (
        event.text.startswith(".kickme")
        or event.text.startswith("/kickme")
        or event.text.startswith("?kickme")
        or event.text.startswith("!kickme")
        or event.text.startswith("/kickthefools")
        or event.text.startswith(".kickthefools")
        or event.text.startswith("!kickthefools")
        or event.text.startswith("?kickthefools")
    ):
        return
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "kick")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "kick",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/skick ?(.*)")
async def skick(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "skick")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "skick",
        reason,
        0,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/tban ?(.*)")
async def tban(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "tban")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate("Why would I ban an admin? That sounds like a pretty dumb idea.", event.chat_id))
    if not reason:
        return await event.reply(translate("You haven't specified a time to ban this user for!", event.chat_id))
    if not reason[0].isdigit():
        return await event.reply(translate(f"failed to get specified time: {reason} is not a valid number", event.chat_id))

    if len(reason) == 1:
        return await event.reply(translate(
            f"""failed to get specified time: '{reason}' does not follow the expected time patterns.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""", event.chat_id)
        )
    ban_time = int(await extract_time(event, reason))
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "tban",
        reason,
        ban_time,
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/tmute ?(.*)")
async def tmute(event):
    if event.is_private:
        return
    if not event.from_id:
        return await a_ban(event, "tmute")
    if event.is_group:
        if not event.sender_id in DEVS:
            if not await can_ban_users(event, event.sender_id):
                return
    reason = ""
    user = None
    try:
        user, reason = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if isinstance(user, Channel):
        return await event.reply(translate(
            "Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    if await is_admin(event.chat_id, user.id):
        return await event.reply(translate(
            "Why would I mute an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    if not reason:
        return await event.reply(translate("You haven't specified a time to ban this user for!", event.chat_id))
    if not reason[0].isdigit():
        return await event.reply(translate(
            f"failed to get specified time: {reason} is not a valid number", event.chat_id)
        )
    if len(reason) == 1:
        return await event.reply(translate(
            f"""failed to get specified time: '{reason}' does not follow the expected time patterns.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""", event.chat_id)
        )
    mute_time = await extract_time(event, reason)
    await excecute_operation(
        event,
        user.id,
        user.first_name,
        "tmute",
        reason,
        int(mute_time),
        event.id,
        False,
        event.sender_id,
        event.sender.first_name,
    )


@Zbot(pattern="^/(kickme|punchme) ?(.*)")
async def k_me(event):
    if not event.is_group:
        return
    if not event.sender:
        return
    if isinstance(event.sender, Channel):
        return await event.reply(translate(
            "Why would I kick an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    if await is_admin(event.chat_id, event.sender_id):
        return await event.reply(translate(
            "Ha, I'm not kicking you, you're an admin! You're stuck with everyone here.", event.chat_id)
        )
    try:
        await event.client.kick_participant(event.chat_id, event.sender_id)
        await event.reply(translate("Yeah, you're right - get out.", event.chat_id))
    except:
        await event.reply(translate("Failed to kick!", event.chat_id))


# -------Anonymous_Admins--------


async def a_ban(event, mode):
    user_id = None
    first_name = None
    e_t = None
    if event.reply_to:
        user = (await event.get_reply_message()).sender
        if isinstance(user, Channel):
            return
        user_id = user.id
        first_name = user.first_name
    elif event.pattern_match.group(1):
        u_obj = event.text.split(None, 2)[1]
        try:
            user = await event.client.get_entity(u_obj)
            user_id = user.id
            first_name = user.first_name
        except:
            pass
    try:
        if event.reply_to:
            e_t = event.text.split(None, 1)[1]
        elif user_id:
            e_t = event.text.split(None, 2)[2]
    except IndexError:
        e_t = None
    db[event.id] = [e_t, user_id, first_name]
    cb_data = str(event.id) + "|" + str(mode)
    a_buttons = Button.inline("Click to prove admin", data="banon_{}".format(cb_data))
    await event.reply(translate(
        "It looks like you're anonymous. Tap this button to confirm your identity.", event.chat_id),
        buttons=a_buttons,
    )


@Zinline(pattern=r"banon(\_(.*))")
async def rules_anon(e):
    if not await cb_can_ban_users(e, e.sender_id):
        return
    d_ata = ((e.pattern_match.group(1)).decode()).split("_", 1)[1]
    da_ta = d_ata.split("|", 1)
    event_id = int(da_ta[0])
    mode = da_ta[1]
    try:
        cb_data = db[event_id]
    except KeyError:
        return await e.edit(translate("This requests has been expired.", event.chat_id))
    user_id = cb_data[1]
    fname = cb_data[2]
    reason = cb_data[0]
    mute_time = 0
    if not reason:
        reason = ""
    if not user_id:
        return await e.edit(translate(
            "I don't know who you're talking about, you're going to need to specify a user...!", event.chat_id)
        )
    if await is_admin(e.chat_id, user_id):
        return await e.edit(translate(
            f"Why would I {mode} an admin? That sounds like a pretty dumb idea.", event.chat_id)
        )
    if mode in ["tban", "tmute"]:
        if not reason:
            return await e.edit(translate(
                "You haven't specified a time to ban/mute this user for!", event.chat_id)
            )
        if not reason[0].isdigit():
            return await e.edit(translate(
                "failed to get specified time: {reason} is not a valid number", event.chat_id)
            )
        if len(reason) == 1:
            return await e.edit(translate(
                f"""failed to get specified time: '{reason}' does not follow the expected time patterns.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""", event.chat_id)
            )
        mute_time = await extract_time(e, reason)
    await excecute_operation(
        e,
        user_id,
        fname,
        mode,
        reason,
        mute_time,
        None,
        True,
    )



from .. import CMD_HELP
__help__ = """
 ❍ /punchme*:* punchs the user who issued the command
*Admins only:*
 ❍ /ban or /dban <userhandle>*:* bans a user. (via handle, or reply)
 ❍ /sban <userhandle>*:* Silently ban a user. Deletes command, Replied message and doesn't reply. (via handle, or reply)
 ❍ /tban <userhandle> x(m/h/d)*:* bans a user for `x` time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
 ❍ /unban <userhandle>*:* unbans a user. (via handle, or reply)
 ❍ /punch <userhandle>*:* Punches a user out of the group, (via handle, or reply)
 *Admins only:*
 ❍ /mute or /dmute <userhandle>*:* silences a user. Can also be used as a reply, muting the replied to user.
 ❍ /tmute <userhandle> x(m/h/d)*:* mutes a user for x time. (via handle, or reply). `m` = `minutes`, `h` = `hours`, `d` = `days`.
 ❍ /unmute <userhandle>*:* unmutes a user. Can also be used as a reply, muting the replied to user.
"""
__name__ = "bans"
CMD_HELP.update({__name__: [__name__, __help__]})
