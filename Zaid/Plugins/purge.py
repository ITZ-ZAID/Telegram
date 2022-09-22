import asyncio

from telethon import Button, functions
from telethon.errors import MultiError, UserAlreadyParticipantError
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.tl.functions.messages import ExportChatInviteRequest

from Zaid import Zaid
from Zaid.utils import Zbot, Zinline
from config import BOT_ID, OWNER_ID
from .language import translate

from . import can_del_msg, db, is_owner, ubot

purgex = db.purge


@Zbot(pattern="^/purge(?: |$|@Zaid2_Robot)(.*)")
async def purge(event):
    if (
        event.text.startswith("!purgefrom")
        or event.text.startswith("/purgefrom")
        or event.text.startswith("?purgefrom")
        or event.text.startswith("+purgefrom")
        or event.text.startswith("!purgeto")
        or event.text.startswith("?purgeto")
        or event.text.startswith("/purgeto")
        or event.text.startswith("+purgeto")
    ):
        return
    lt = event.pattern_match.group(1)
    if lt:
        if not lt.isdigit():
            lt = None
    if lt:
        limit = lt
    else:
        limit = 1000
    if event.is_group:
        if not await can_del_msg(event, event.sender_id):
            return
    if not event.reply_to_msg_id:
        return await event.reply(translate("Reply to a message to show me where to purge from.", event.chat_id))
    messages = []
    message_id = event.reply_to_msg_id
    delete_to = event.message.id
    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == limit:
            break
    try:
        await event.client.delete_messages(event.chat_id, messages)
    except MultiError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
    except MessageDeleteForbiddenError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
    x = await event.respond(translate("Purge complete!", event.chat_id))
    await asyncio.sleep(4)
    await x.delete()


@Zbot(pattern="^/purgefrom$")
async def purge_from_(event):
    if event.is_group:
        if not await can_del_msg(event, event.sender_id):
            return
    if not event.reply_to_msg_id:
        return await event.reply(translate("Reply to a message to let me know what to delete.", event.chat_id))
    msg_id = event.reply_to_msg_id
    purgex.update_one({"id": event.chat_id}, {"$set": {"msg_id": msg_id}}, upsert=True)
    await event.respond(translate(
        "Message marked for deletion. Reply to another message with /purgeto to delete all messages in between.", event.chat_id),
        reply_to=msg_id,
    )


@Zbot(pattern="^/purgeto$")
async def purge_to_(event):
    if event.is_group:
        if not await can_del_msg(event, event.sender_id):
            return
    if not event.reply_to_msg_id:
        return await event.reply(translate("Reply to a message to let me know what to delete.", event.chat_id))
    purge = purgex.find_one({"id": event.chat_id})
    if purge == None:
        msg_id = None
    else:
        msg_id = purge.get("msg_id")
    if msg_id == None:
        return await event.reply(translate(
            "You can only use this command after having used the /purgefrom command.", event.chat_id)
        )
    messages = []
    limit = 1000
    delete_to = event.reply_to_msg_id
    messages.append(event.reply_to_msg_id)
    for id in range(msg_id, delete_to + 1):
        messages.append(id)
        if len(messages) == limit:
            break
    try:
        await event.client.delete_messages(event.chat_id, messages)
    except MultiError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
    except MessageDeleteForbiddenError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
    purgex.delete_one({"id": event.chat_id})
    await event.respond(translate("Purge complete!", event.chat_id))


@Zbot(pattern="^/del(?: |$|@Zaid2_Robot)(.*)")
async def deve(event):
    if (
        event.text.startswith("+delall")
        or event.text.startswith("?delall")
        or event.text.startswith("/delall")
        or event.text.startswith("!delall")
    ):
        return
    if event.from_id:
        if event.is_group:
            if not await can_del_msg(event, event.sender_id):
                return
        if not event.reply_to:
            return await event.reply(translate(
                "Reply to a message to let me know what to delete.", event.chat_id)
            )
        try:
            await (await event.get_reply_message()).delete()
        except MessageDeleteForbiddenError:
            return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
        await event.delete()


@Zbot(pattern="^/spurge(?: |$|@Zaid2_Robot)(.*)")
async def b(event):
    lt = event.pattern_match.group(1)
    if lt:
        if not lt.isdigit():
            lt = None
    if lt:
        limit = lt
    else:
        limit = 1000
    if event.is_group:
        if not await can_del_msg(event, event.sender_id):
            return
    if not event.reply_to_msg_id:
        return await event.reply(translate("Reply to a message to show me where to purge from.", event.chat_id))
    messages = []
    message_id = event.reply_to_msg_id
    delete_to = event.message.id
    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == limit:
            break
    try:
        await event.client.delete_messages(event.chat_id, messages)
    except MultiError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))
    except MessageDeleteForbiddenError:
        return await event.reply(translate("I can't delete messages that are too old!", event.chat_id))

"""
@Zbot(pattern="^/delall$")
async def kek(event):
    if event.is_private:
        return await event.reply("This command is made for groups and channels only.")
    elif event.sender_id == OWNER_ID:
        pass
    elif event.is_group:
        if not await is_owner(event, event.sender_id):
            return
    buttons = [
        Button.inline("Delete All", data="d_all"),
        Button.inline("Cancel", data="d_a_cancel"),
    ]
    text = "Are you sure want to delete **ALL** messages of **{}**\n This can't be undone.".format(
        event.chat.title
    )
    await event.respond(text, buttons=buttons)


@Zinline(pattern="d_all")
async def ki(event):
    if event.sender_id == OWNER_ID:
        pass
    else:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perm.is_admin:
            return await event.answer("You need to be an admin to do this.")
        if not perm.is_creator:
            return await event.answer("Chat creator required.")
    mp = await event.client.get_permissions(event.chat_id, BOT_ID)
    if not mp.add_admins:
        return await event.edit(
            "Unable to process delete **ALL** Process due to missing Permission: CanAddAdmins"
        )
    if not mp.delete_messages:
        return await event.edit(
            "Unable to process delete **ALL** Process due to missing Permission: CanDelMessages"
        )
    if not mp.invite_users:
        return await event.edit(
            "Unable to process delete **ALL** Process due to missing Permission: CanInviteUsers"
        )
    await event.edit("begining the cleaning process....")
    try:
        link = await event.client(ExportChatInviteRequest(event.chat_id))
    except Exception as e:
        return await event.edit(str(e))
    link = (link.link).replace("https://t.me/+", "")
    JOINED = False
    try:
        await ubot(functions.messages.ImportChatInviteRequest(link))
        JOINED = True
    except UserAlreadyParticipantError:
        pass
    except Exception as e:
        return await event.edit(str(e))
    try:
        await event.client.edit_admin(
            event.chat_id,
            "@Helper_Xyz",
            manage_call=False,
            add_admins=False,
            pin_messages=True,
            delete_messages=True,
            ban_users=True,
            change_info=True,
            invite_users=True,
            title="delall_helper",
        )
    except Exception as e:
        if await can_del_msg(event, "RoseLoverX"):
            pass
        else:
            return await event.edit(str(e))
    msg_id = event.id
    messages = []
    for msg_id in range(1, msg_id + 1):
        messages.append(msg_id)
        if len(messages) > 300:
            await ubot.delete_messages(event.chat_id, messages)
            messages = []
    await ubot.delete_messages(event.chat_id, messages)
    if JOINED:
        try:
            await event.client.kick_participant(event.chat_id, "Helper_Xyz")
        except:
            pass
    await event.edit("cleaning process completed.")
"""
