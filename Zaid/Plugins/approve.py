from telethon import Button

from .. import CMD_HELP
from ..utils import Zbot, Zinline
from . import (
    can_ban_users,
    cb_can_change_info,
    cb_is_owner,
    db,
    get_user,
    is_admin,
    is_owner,
)

approve_d = db.approve_d


@Zbot(pattern="^/approve ?(.*)")
async def appr(event):
    if (
        event.text.startswith("+approved")
        or event.text.startswith("/approved")
        or event.text.startswith("!approved")
        or event.text.startswith("?approved")
        or event.text.startswith("?approval")
        or event.text.startswith("+approval")
        or event.text.startswith("/approval")
        or event.text.startswith("!approvel")
    ):
        return
    if event.is_private:
        return await event.reply(
            "This command is made to be used in group chats, not in pm!"
        )
    if not event.from_id:
        await a_approval(event, "approve")
    else:
        if not await can_ban_users(event, event.sender_id):
            return
        user = None
        try:
            user, reason = await get_user(event)
        except TypeError:
            pass
        if not user:
            return
        if await is_admin(event.chat_id, user.id):
            return await event.reply(
                "User is already admin - locks, blocklists, and antiflood already don't apply to them."
            )
        a_str = "<a href='tg://user?id={}'>{}</a> has been approved in {}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood."
        await event.respond(
            a_str.format(user.id, user.first_name, event.chat.title),
            reply_to=event.reply_to_msg_id or event.id,
            parse_mode="html",
        )
        if not approve_d.find_one({"user_id": user.id, "chat_id": event.chat_id}):
            approve_d.insert_one(
                {"user_id": user.id, "chat_id": event.chat_id, "name": user.first_name}
            )


@Zbot(pattern="^/disapprove ?(.*)")
async def dissapprove(event):
    if (
        event.text.startswith("+disapproveall")
        or event.text.startswith("!disapproveall")
        or event.text.startswith("?disapproveall")
        or event.text.startswith("/disapproveall")
    ):
        return
    if event.is_private:
        return await event.reply(
            "This command is made to be used in group chats, not in pm!"
        )
    if not event.from_id:
        await a_approval(event, "disapprove")
    else:
        if not await can_ban_users(event, event.sender_id):
            return
        user = None
        try:
            user, reason = await get_user(event)
        except TypeError:
            pass
        if not user:
            return
        if await is_admin(event.chat_id, user.id):
            return await event.reply("This user is an admin, they can't be unapproved.")
        if approve_d.find_one({"user_id": user.id, "chat_id": event.chat_id}):
            await event.reply(
                f"{user.first_name} is no longer approved in {event.chat.title}."
            )
            return approve_d.delete_one({"user_id": user.id})
        await event.reply(f"{user.first_name} isn't approved yet!")


@Zbot(pattern="^/approved")
async def approved(event):
    if event.is_private:
        return await event.reply(
            "This command is made to be used in group chats, not in pm!"
        )
    if not event.from_id:
        return
    if not await can_ban_users(event, event.sender_id):
        return
    app_rove_d = approve_d.find({"chat_id": event.chat_id})
    if app_rove_d.count() == 0:
        await event.reply(f"No users are approved in {event.chat.title}")
    else:
        out_str = "The following users are approved:"
        for app_r in app_rove_d:
            out_str += "\n- `{}`: {}".format(app_r["user_id"], app_r["name"])
        await event.reply(out_str)


@Zbot(pattern="^/approval ?(.*)")
async def apr_val(event):
    if event.is_private:
        return await event.reply(
            "This command is made to be used in group chats, not in pm!"
        )
    if not event.reply_to and not event.pattern_match.group(1):
        if not event.from_id:
            return
        user = event.sender
    else:
        user = None
        try:
            user, xtra = await get_user(event)
        except TypeError:
            pass
        if not user:
            return
    if approve_d.find_one({"user_id": user.id, "chat_id": event.chat_id}):
        await event.reply(
            f"{user.first_name} is an approved user. Locks, antiflood, and blocklists won't apply to them."
        )
    else:
        await event.reply(
            f"{user.first_name} is not an approved user. They are affected by normal commands."
        )


@Zbot(pattern="^/unapproveall$")
async def unapprove_all(event):
    if event.is_private:
        return await event.reply(
            "This command is made to be used in group chats, not in pm!"
        )
    if not event.from_id:
        await a_approval(event, "unapproveall")
    else:
        if not await is_owner(event, event.sender_id):
            return
        c_text = f"Are you sure you would like to unapprove **ALL** users in {event.chat.title}? This action cannot be undone."
        buttons = [
            [Button.inline("Unapprove all users", data="un_ap")],
            [Button.inline("Cancel", data="c_un_ap")],
        ]
        await event.reply(c_text, buttons=buttons)


@Zinline(pattern="un_ap")
async def un_app(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(
        "Unapproved all users in chat. All users will now be affected by locks, blocklists, and antiflood."
    )
    approve_d.delete_many({"chat_id": event.chat_id})


@Zinline(pattern="c_un_ap")
async def c_un_ap(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit("Unapproval of all approved users has been cancelled")


async def a_approval(event, mode):
    if mode in ["approve", "disapprove"]:
        user = reason = None
        try:
            user, reason = await get_user(event)
        except TypeError:
            if not user:
                return
        cb_data = str(user.id) + "|" + mode + "|" + str(user.first_name[:15])
    elif mode == "unapproveall":
        cb_data = str(6) + "|" + "unapproveall" + "|" + "noise"
    a_text = "It looks like you're anonymous. Tap this button to confirm your identity."
    a_button = Button.inline("Click to prove admin", data="anap_{}".format(cb_data))
    await event.reply(a_text, buttons=a_button)


@Zinline(pattern=r"anap(\_(.*))")
async def _(event):
    input = ((event.pattern_match.group(1)).decode()).split("_", 1)[1]
    user, mode, name = input.split("|")
    user = int(user.strip())
    mode = mode.strip()
    name = name.strip()
    if mode == "unapproveall":
        if not await cb_is_owner(event, event.sender_id):
            return
    else:
        if not await cb_can_change_info(event, event.sender_id):
            return
    if mode == "disapprove":
        if await is_admin(event.chat_id, user):
            return await event.edit("This user is an admin, they can't be unapproved.")
        if approve_d.find_one({"user_id": user, "chat_id": event.chat_id}):
            await event.edit(f"{name} is no longer approved in {event.chat.title}.")
            return approve_d.delete_one({"user_id": user})
        await event.edit(f"{name} isn't approved yet!")
    elif mode == "approve":
        if await is_admin(event.chat_id, user):
            return await event.edit(
                "User is already admin - locks, blocklists, and antiflood already don't apply to them."
            )
        a_str = "<a href='tg://user?id={}'>{}</a> has been approved in {}! They will now be ignored by automated admin actions like locks, blocklists, and antiflood."
        await event.edit(
            a_str.format(user, name, event.chat.title),
            parse_mode="html",
        )
        if not approve_d.find_one({"user_id": user, "chat_id": event.chat_id}):
            approve_d.insert_one(
                {"user_id": user, "chat_id": event.chat_id, "name": user.first_name}
            )
    elif mode == "unapproveall":
        c_text = f"Are you sure you would like to unapprove **ALL** users in {event.chat.title}? This action cannot be undone."
        buttons = [
            [Button.inline("Unapprove all users", data="un_ap")],
            [Button.inline("Cancel", data="c_un_ap")],
        ]
        await event.edit(c_text, buttons=buttons)


__name__ = "approval"
__help__ = """
Here is the help for **Approval** module:

Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.

That's what approvals are for - approve of trustworthy users to allow them to send 

**Admin Commands:**
- /approve `<user>`: Approve the user, Locks Antiflood and Blacklists won't apply to them anymore.
- /disapprove `<user>`: Disapprove the user, they will now be subject to Locks Antiflood and Blacklists again.
- /approved: List the approved users of a chat.
- /approval `<user>`: Check the approval status of a user.
- /disapproveall: Disapprove **ALL** users of a chat, This cannot be undone.
"""
CMD_HELP.update({__name__: [__name__, __help__]})
