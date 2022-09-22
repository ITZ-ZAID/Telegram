import time

from telethon import Button, types

from config import OWNER_ID
from ..utils import Zbot, Zinline
from . import (
    can_ban_users,
    can_change_info,
    cb_can_ban_users,
    cb_is_owner,
    extract_time,
)
from . import g_time as get_time
from . import get_user, is_admin, is_owner
from .mongodb import warns_db as db
from .language import translate

@Zbot(pattern="^/setwarnlimit ?(.*)")
async def set_warn_limit____(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_change_info(e, e.sender_id):
        return
    c = e.pattern_match.group(1)
    if not c:
        await e.reply(translate(
            "Please specify how many warns a user should be allowed to receive before being acted upon.", event.chat_id)
        )
    elif c.isdigit():
        if int(c) > 128:
            return await e.reply(translate("Max no of warn limit is 128!", event.chat_id))
        awa = translate("Warn limit settings for", event.chat_id)
        ok = translate("have been updated to", event.chat_id)
        await e.reply(
            "{} {} {} {}.".format(
                awa, e.chat.title, ok, c
            )
        )
        db.set_warn_limit(e.chat_id, int(c))
    else:
        await e.reply(translate(f"Expected an integer, got '{c}'.", event.chat_id))


@Zbot(pattern="^/setwarnmode ?(.*)")
async def set_warn__mode____(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_change_info(e, e.sender_id):
        return
    c = p = e.pattern_match.group(1)
    if not c:
        return await e.reply(translate(
            "You need to specify an action to take upon too many warns. Current modes are: ban/kick/mute/tban/tmute", event.chat_id)
        )
    c = c.split(None, 1)
    if not c[0] in ["ban", "kick", "mute", "tban", "tmute"]:
        return await e.reply(translate(
            f"Unknown type '{c[0]}'. Please use one of: ban/kick/mute/tban/tmute", event.chat_id)
        )
    c_time = 0
    if c[0] in ["tban", "tmute"]:
        try:
            c_time = await extract_time(e, c[1])
        except IndexError:
            return await e.reply(translate(
                "Looks like you're trying to set a temporary value for warnings, but haven't specified a time; use `/setwarnmode tban <timevalue>`.\nExample time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.", event.chat_id)
            )
    await e.reply(translate(f"Updated warn mode to:{p}", event.chat_id))
    db.set_warn_strength(e.chat_id, c[0], c_time)


@Zbot(pattern="^/setwarntime ?(.*)")
async def set_warn_last__(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_change_info(e, e.sender_id):
        return
    q = e.pattern_match.group(1)
    if not q:
        return await e.reply(translate("Please specify how long warns should last for.", event.chat_id))
    xp = e.text.split(" ", 1)[1]
    time = await extract_time(e, xp)
    await e.reply(translate(
        f"The warn time has been set to {get_time(time)}. Older warns will be automatically removed.", event.chat_id)
    )
    db.set_warn_expire(e.chat_id, time)


warn_settings = """
There is a {} warning limit in {}. When that limit has been exceeded, the user will be {}.
Warnings {}.
"""


@Zbot(pattern="^/warnings ?(.*)")
async def check_warn___settings__(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_change_info(e, e.sender_id):
        return
    chat_id = e.chat_id
    title = e.chat.title
    limit, mode, time, expiretime = db.get_warn_settings(chat_id)
    if mode in ["ban", "tban"]:
        d = "banned"
        if mode == "tban":
            d += "for " + str(get_time(time))
    elif mode in ["mute", "tmute"]:
        d = "muted"
        if mode == "tmute":
            d += "for " + str(get_time(time))
    elif mode == "kick":
        d = "kicked"
    if expiretime != 0:
        dc = "expire after{}".format(get_time(expiretime))
    else:
        dc = "do not expire"
    await e.reply(warn_settings.format(limit, title, d, dc))


@Zbot(pattern="^/resetwarn ?(.*)")
async def reset_warns___(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_change_info(e, e.sender_id):
        return
    user = None
    try:
        user, xtra = await get_user(e)
    except:
        pass
    if user == None:
        return
    reset = db.reset_warns(user.id, e.chat_id)
    use = translate("User", event.chat_id)
    tos = translate("has had all their previous warns removed. ⚠️", event.chat_id)
    if reset:
        await e.reply(
            f"{use} <a href='tg://user?id={user.id}'>{user.first_name}</a> {tos}",
            parse_mode="html",
        )
    else:
        await e.reply(
            f"{use} <a href='tg://user?id={user.id}'>{user.first_name}</a> {tos}",
            parse_mode="html",
        )


@Zbot(pattern="^/resetallwarns(@Zaid2_Robot)?$")
async def reset_all_warns_of___chat____(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not e.sender_id == OWNER_ID and not await is_owner(e, e.sender_id):
        return
    await e.reply(translate(
        f"Are you sure you would like to reset **ALL** warnings in {e.chat.title}? This action cannot be undone.", event.chat_id),
        buttons=[
            [Button.inline(translate("Reset all warnings", event.chat_id), data="rm_all_w")],
            [Button.inline(translate("Cancel", event.chat_id), data="c_rm_all_w")],
        ],
    )


@Zinline(pattern="rm_all_w")
async def rm_all_warns(e):
    if not await cb_is_owner(e, e.sender_id):
        return
    await e.edit(translate("Reset all chat warnings.", e.chat_id))
    db.reset_all_warns(e.chat_id)


@Zinline(pattern="c_rm_all_w")
async def c_rm_all_w(e):
    if not await cb_is_owner(e, e.sender_id):
        return
    await e.edit(translate("Resetting of all warnings has been cancelled.", e.chat_id))


@Zbot(pattern="^/(warn|swarn|dwarn)(@Zaid2_Robot|zaid2_robot)? ?(.*)")
async def warn_peepls____(e):
    event = e
    for x in [
        "+warnings",
        "/warnings",
        "!warnings",
        "?warnings",
        "+warns",
        "/warns",
        "!warns",
        "?warns",
    ]:
        if e.text.startswith(x):
            return
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_ban_users(e, e.sender_id):
        return
    q = e.text.split(" ", 1)
    pq = q[0]
    for x in ["+", "?", "/", "!"]:
        pq = pq.replace(x, "")
    if e.reply_to:
        user = (await e.get_reply_message()).sender
        if len(q) == 2:
            reason = q[1]
        else:
            reason = ""
    elif len(q) == 2:
        q = q[1].split(" ", 1)
        u_obj = q[0]
        if u_obj.isnumeric():
            u_obj = int(u_obj)
        try:
            user = await e.client.get_entity(u_obj)
        except (ValueError, TypeError) as rr:
            return await e.reply(str(rr))
        if len(q) == 2:
            reason = q[1]
        else:
            reason = ""
    else:
        return await e.reply(translate("I can't warn nothing! Tell me to whom I should warn!", event.chat_id))
    if not user or isinstance(user, types.Channel):
        return await e.reply(translate("I can't warn nothing! Tell me to whom I should warn!", event.chat_id))
    if await is_admin(e.chat_id, user.id):
        return await e.reply(translate("Well.. you are wrong. You can't warn an admin.", event.chat_id))
    if pq == "dwarn":
        await (await e.get_reply_message()).delete()
    warn, strength, actiontime, limit, num_warns, reasons = db.warn_user(
        user.id, e.chat_id, reason
    )
    if reason:
        text = translate("Reason", event.chat_id)
        reason = f"\n<b>{text}:</b>\n{reason}"
    if not warn:
    sg1 = translate("User", event.chat_id)
    sg2 = translate("has", event.chat_id)
    sq3 = translate("warnings ⚠️; Be careful", event.chat_id)
    text = f'{sg1} <a href="tg://user?id={user.id}">{user.first_name}</a> {sg2} {num_warns}/{limit} {sg3}!{reason}'
    buttons = [
        Button.inline(translate("Remove warn (Admin Only)", event.chat_id), data="rmwarn_{}".format(user.id))
    ]
    if not pq == "swarn":
        await e.respond(
            text,
            buttons=buttons,
            parse_mode="html",
            reply_to=e.reply_to_msg_id or e.id,
        )
    if warn:
        if strength == "tban":
            await e.client.edit_permissions(
                e.chat_id,
                user.id,
                until_date=time.time() + int(actiontime),
                view_messages=False,
            )
            action = translate("banned for", event.chat_id) + get_time(actiontime)
        elif strength == "tmute":
            await e.client.edit_permissions(
                e.chat_id,
                user.id,
                until_date=time.time() + int(actiontime),
                send_messages=False,
            )
            action = translate("muted for", event.chat_id) + get_time(actiontime)
        elif strength == "ban":
            await e.client.edit_permissions(e.chat_id, user.id, view_messages=False)
            action = translate("banned", event.chat_id)
        elif strength == "mute":
            await e.client.edit_permissions(e.chat_id, user.id, send_messages=False)
            action = "muted"
        elif strength == "kick":
            await e.client.kick_participant(e.chat_id, user.id)
            action = "kicked"
        kk = translate("That's", event.chat_id)
        kka = translate("Warnings ⚠️", event.chat_id)
        warn_action_notif = (
            "{} {}/{} {}; <a href='tg://user?id={}'>{}</a> is {}!".format(
                kk, num_warns, limit, kka, user.id, user.first_name, action
            )
        )
        qp = 0
        if reasons:
            xg = translate("Reasons", event.chat_id)
            rr = f"\n<b>{xg}:</b>"
            for reason in reasons:
                qp += 1
                rr += "\n{}: {}".format(qp, reason)
            warn_action_notif += rr
        await e.respond(
            warn_action_notif, reply_to=e.reply_to_msg_id or e.id, parse_mode="html"
        )


@Zbot(pattern="^/warns(@Zaid2_Robot)? ?(.*)")
async def warns___(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    q = e.text.split(" ", 1)
    if e.reply_to:
        user = (await e.get_reply_message()).sender
    elif len(q) == 2:
        q = q[1].split(" ", 1)
        u_obj = q[0]
        if u_obj.isnumeric():
            u_obj = int(u_obj)
        try:
            user = await e.client.get_entity(u_obj)
        except (ValueError, TypeError) as rr:
            return await e.reply(str(rr))
    else:
        user = e.sender
    warns = db.get_warns(user.id, e.chat_id)
    if not warns or warns[0] == 0:
        xg = translate("User", event.chat_id)
        non = translate("has no warnings⚠️", event.chat_id)
        await e.reply(
            f"{xg} <a href='tg://user?id={user.id}'>{user.first_name}</a> {non}!",
            parse_mode="html",
        )
    else:
        count, reasons = warns
        gk = translate("User", event.chat_id)
        hks = translate("has warning ⚠️", event.chat_id)
        limit = db.get_warn_limit(e.chat_id)
        r = "{} <a href='tg://user?id={}'>{}</a> {}/{} {}."
        if reasons:
            m = translate("Reasons are", event.chat_id)
            r += f"\n{m}:"
            qc = 0
            for x in reasons:
                qc += 1
                r += "\n{}. {}".format(qc, x)
        await e.reply(
            r.format(gk, user.id, user.first_name, count, limit, hks), parse_mode="html"
        )


@Zbot(pattern="^/rmwarn(@Zaid2_Robot)? ?(.*)")
async def rmwarns__(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await anon_warn()
    if not await can_ban_users(e, e.sender_id):
        return
    q = e.text.split(" ", 1)
    if e.reply_to:
        user = (await e.get_reply_message()).sender
        if len(q) == 2:
            reason = q[1]
        else:
            reason = ""
    elif len(q) == 2:
        q = q[1].split(" ", 1)
        u_obj = q[0]
        if u_obj.isnumeric():
            u_obj = int(u_obj)
        try:
            user = await e.client.get_entity(u_obj)
        except (ValueError, TypeError) as rr:
            return await e.reply(str(rr))
        if len(q) == 2:
            reason = q[1]
        else:
            reason = ""
    else:
        return await e.reply(translate(
            "I can't remove warns of nothing! Tell me user whose warn should be removed!", event.chat_id)
        )
    rm = db.remove_warn(user.id, e.chat_id)
    if rm:
        if reason:
            kk = translate("Reason", event.chat_id)
            reason = f"\n{kk}: {reason}"
        cd = translate("Removed", event.chat_id)
        last = translate("last warn", event.chat_id)
        await e.reply(
            "{} <a href='tg://user?id={}'>{}</a>'s {}.{}".format(
                cd, user.id, user.first_name, last, reason
            ),
            parse_mode="html",
        )
    else:
        k = translate("User", event.chat_id)
        m = translate("has no warnings ⚠️", event.chat_id)
        await e.reply(
            "{} <a href='tg://user?id={}'>{}</a> {}.".format(
                k, user.id, user.first_name, m
            ),
            parse_mode="htm",
        )


@Zinline(pattern=r"rmwarn(\_(.*))")
async def rm_warn_cb(e):
    if not await cb_can_ban_users(e, e.sender_id):
        return
    r = e.pattern_match.group(1).decode().split("_", 1)[1]
    r = int(r)
    wa = translate("Warn removed by admin", e.chat_id)
    await e.edit(
        "{} <a href='tg://user?id={}'>{}</a>".format(
            wa, e.sender_id, e.sender.first_name
        ),
        parse_mode="html",
    )
    db.remove_warn(r, e.chat_id)
