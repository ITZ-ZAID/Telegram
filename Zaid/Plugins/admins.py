import os

from telethon import Button
from telethon.errors.rpcerrorlist import (
    ChatAboutNotModifiedError,
    ChatNotModifiedError,
    ParticipantsTooFewError,
    UserAdminInvalidError,
)
from telethon.tl.functions.channels import (
    EditPhotoRequest,
    EditTitleRequest,
    SetStickersRequest,
)
from telethon.tl.functions.messages import EditChatAboutRequest, ExportChatInviteRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChannelParticipantsBots,
    DocumentAttributeSticker,
    InputStickerSetID,
    MessageMediaDocument,
    MessageMediaPhoto,
    UserStatusLastMonth,
)

db = {}
from .. import Zaid
from config import OWNER_ID
from ..utils import Zbot, Zinline
from . import (
    DEVS,
    SUDO_USERS,
    can_change_info,
    can_promote_users,
    cb_can_promote_users,
    check_owner,
    get_user,
    is_admin,
    is_owner,
)
from .language import translate

su = DEVS + SUDO_USERS
su.append(OWNER_ID)


@Zbot(pattern="^/promote(?: |$|@Zaid2_Robot)(.*)")
async def promote__user___(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in my PM!", event.chat_id)
        )
    if not e.from_id:
        return await anonymous(e, "promote")
    if not e.sender_id in su:
        if not await can_change_info(e, e.sender_id):
            return
    user = None
    title = "Λ∂мιи"
    try:
        user, title = await get_user(e)
    except TypeError:
        pass
    if not user:
        return
    if e.sender_id == user.id:
        return await e.reply(translate("Why are you trying to promote yourself?", event.chat_id))
    try:
        await e.client.edit_admin(
            e.chat_id,
            user.id,
            manage_call=False,
            add_admins=False,
            pin_messages=True,
            delete_messages=True,
            ban_users=True,
            change_info=True,
            invite_users=True,
            title=title,
        )
        name = "User"
        if user.first_name:
            name = user.first_name.replace("<", "&lt;").replace(">", "&gt!")
            if user.last_name:
                name = name + user.last_name
        men = translate("Successfully Promoted", event.chat_id)
        await e.reply(
            f"{men} <b><a href='tg://user?id={user.id}'>{name}</a></b> !",
            parse_mode="html",
        )
    except:
        await e.reply(translate(
            "I can't promote/demote people here!\nMake sure I'm admin and can appoint new admins.", event.chat_id)
        )


@Zbot(pattern="^/(superpromote|fullpromote)(?: |$|@Zaid2_Robot)(.*)")
async def super_promote(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in my PM!", event.chat_id)
        )
    if not e.from_id:
        return await anonymous(e, "superpromote")
    if not e.sender_id in su:
        if not await can_promote_users(e, e.sender_id):
            return
    user = None
    title = "𝙎υρєя Λ∂мιи"
    try:
        user, title = await get_user(e)
    except TypeError:
        pass
    if not user:
        return
    try:
        await e.client.edit_admin(
            e.chat_id,
            user.id,
            manage_call=True,
            add_admins=True,
            pin_messages=True,
            delete_messages=True,
            ban_users=True,
            change_info=True,
            invite_users=True,
            title=title,
        )
        name = user.first_name
        if name:
            name = (name.replace("<", "&lt;")).replace(">", "&gt!")
        red = translate("Successfully promoted", event.chat_id)
        await e.reply(
            f"{red} <a href='tg://user?id={user.id}'>{name}</a> with full rights!",
            parse_mode="html",
        )
    except UserAdminInvalidError:
        return await e.reply(translate(
            "This user has already been promoted by someone other than me; I can't change their permissions!.", event.chat_id)
        )
    except:
        await e.reply(translate("Seems like I don't have enough rights to do that.", event.chat_id))


@Zbot(pattern="^/demote(?: |$|@Zaid2_Robot)(.*)")
async def _de(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in my PM!", event.chat_id)
        )
    if not e.from_id:
        return await anonymous(e, "demote")
    if not e.sender_id in su:
        if not await can_promote_users(e, e.sender_id):
            return
    user = None
    try:
        user, title = await get_user(e)
    except TypeError:
        pass
    if not user:
        return
    if await check_owner(e, user.id):
        return await e.reply(translate(
            "I don't really feel like staging a mutiny today, I think the chat owner deserves to stay an admin.", event.chat_id)
        )
    elif user.bot:
        return await e.reply(translate(
            "Due to telegram limitations, I can't demote bots. Please demote them manually!", event.chat_id)
        )
    if not await is_admin(e.chat_id, user.id):
        return await e.reply(translate("This user isn't an admin anyway!", event.chat_id))
    try:
        await e.client.edit_admin(
            e.chat_id,
            user.id,
            is_admin=False,
            manage_call=False,
            add_admins=False,
            pin_messages=False,
            delete_messages=False,
            ban_users=False,
            change_info=False,
            invite_users=False,
        )
        name = user.first_name
        if name:
            name = (name.replace("<", "&lt;")).replace(">", "&gt!")
        demote = translate("Demoted User", event.chat_id)
        await e.reply(
            f"{demote} <a href='tg://user?id={user.id}'>{name}</a> !",
            parse_mode="html",
        )
    except UserAdminInvalidError:
        return await e.reply(translate(
            "This user was promoted by someone other than me; I can't change their permissions! Demote them manually.", event.chat_id)
        )
    except:
        await e.reply(translate("Seems like I don't have enough rights to do that.", event.chat_id))


async def a_ad(event, mode):
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
    a_buttons = Button.inline(translate("Click to prove admin", event.chat_id), data="bad_{}".format(cb_data))
    await event.reply(translate(
        "It looks like you're anonymous. Tap this button to confirm your identity.", event.chat_id),
        buttons=a_buttons,
    )


@Zinline(pattern=r"bad(\_(.*))")
async def _(e):
    event = e
    d_ata = ((e.pattern_match.group(1)).decode()).split("_", 1)[1]
    da_ta = d_ata.split("|", 1)
    event_id = int(da_ta[0])
    try:
        cb_data = db[event_id]
    except KeyError:
        return await e.edit(translate("This requests has been expired, please resend it.", event.chat_id))
    user_id = cb_data[1]
    first_name = cb_data[2]
    title = cb_data[0]
    if not e.sender_id in su:
        if not await cb_can_promote_users(e, e.sender_id):
            return
    if mode == "promote":
        try:
            await e.client.edit_admin(
                e.chat_id,
                int(user_id),
                manage_call=False,
                add_admins=False,
                pin_messages=True,
                delete_messages=True,
                ban_users=True,
                change_info=True,
                invite_users=True,
                title=title if title else "Admin",
            )
            tex = translate("Promoted", event.chat_id)
            text = "{} <b><a href='tg://user?id={}'>{}</a> in <b>{}</b>.".format(
                tex, user_id, first_name or "User", e.chat.title
            )
        except:
            text = translate("Seems like I don't have enough rights to do that.", event.chat_id)
    elif mode == "superpromote":
        try:
            await e.client.edit_admin(
                e.chat_id,
                int(user_id),
                manage_call=True,
                add_admins=True,
                pin_messages=True,
                delete_messages=True,
                ban_users=True,
                change_info=True,
                invite_users=True,
                title=title or "Admin",
            )
            tile = translate("Promoted", event.chat_id)
            text = "{} <b><a href='tg://user?id={}'>{}</a> in <b>{}</b> .".format(
                tile, user_id, first_name or "User", e.chat.title
            )
        except:
            text = translate("Seems like I don't have enough rights to do that.", event.chat_id)
    elif mode == "demote":
        try:
            await e.client.edit_admin(
                e.chat_id,
                int(user_id),
                is_admin=False,
                manage_call=False,
                add_admins=False,
                pin_messages=False,
                delete_messages=False,
                ban_users=False,
                change_info=False,
                invite_users=False,
            )
            jps = translate("Demoted", event.chat_id)
            text = "{} <b><a href='tg://user?id={}'>{}</a> !".format(
                jps, user_id, first_name or "User"
            )
        except:
            text = translate("Seems like I don't have enough rights to do that.", event.chat_id)
    await e.delete()
    await e.respond(text, parse_mode="html")


@Zbot(pattern="^/invitelink$")
async def link(event):
    if event.is_private:
        return  # connection
    if event.from_id:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perm.is_admin:
            return await event.reply(translate("You need to be an admin to do this ", event.chat_id))
        if not perm.invite_users:
            return await event.reply(translate(
                "You are missing the following rights to use this command: CanInviteUsers.", event.chat_id)
            )
    link = await event.client(ExportChatInviteRequest(event.chat_id))
    await event.reply(f"{link.link}", link_preview=False)


@Zbot(pattern="^/adminlist$")
async def admeene(event):
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not event.chat.admin_rights.ban_users:
        return
    ms = translate("Admins in", event.chat_id)
    mentions = f"{ms} **{event.chat.title}:**"
    async for user in event.client.iter_participants(
        event.chat_id, filter=ChannelParticipantsAdmins
    ):
        if not user.bot:
            if not user.deleted:
                if user.username:
                    link = "- @{}".format(user.username)
                    mentions += f"\n{link}"
    await event.reply(mentions)


@Zbot(pattern="^/kickthefools$")
async def kekthem(event):
    if event.is_private:
        return await event.reply(translate("This command is made for Groups, not my PM.", event.chat_id))
    if not await is_owner(event, event.sender_id):
        return
    if not event.chat.admin_rights.ban_users:
        return await event.reply(translate("Unable to perform, not enough rights.", event.chat_id))
    total = 0
    zec = await event.reply(translate("Working....", event.chat_id))
    async for c in event.client.iter_participants(event.chat_id):
        if isinstance(c.status, UserStatusLastMonth):
            try:
                await event.client.kick_participant(event.chat_id, c.id)
                total += 1
            except:
                pass
    if total == 0:
        return await zec.edit(translate("congo, No inactive users to kick.", event.chat_id))
    await zec.edit(translate(f"Sucessfully kicked {total} Inactive users.", event.chat_id))


@Zbot(pattern="^/bots$")
async def bot(event):
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if event.is_group:
        if not await is_admin(event.chat_id, event.sender_id):
            return await event.reply(translate("Only admins can execute this command!", event.chat_id))
    js = translate("Bots in", event.chat_id)
    final = f"{js} __{event.chat.title}__:"
    async for user in event.client.iter_participants(
        event.chat_id, filter=ChannelParticipantsBots
    ):
        final += f"\n- @{user.username}"
    await event.reply(final)


@Zbot(pattern="^/rpromote(?: |$|@Zaid2_Robot)(.*)")
async def kek(event):
    if not event.sender_id == OWNER_ID:
        return
    user = None
    try:
        user, chat = await get_user(event)
    except TypeError:
        pass
    if not user:
        return
    if chat:
        if chat.replace("-", "").isnumeric():
            chat = int(chat)
    try:
        chat = await event.client.get_entity(chat)
    except (TypeError, ValueError):
        return await event.reply(translate("Unable to find the chat/channel!", event.chat_id))
    chat_id = chat.id
    try:
        await event.client.edit_admin(
            chat_id,
            int(user_id),
            manage_call=True,
            add_admins=True,
            pin_messages=True,
            delete_messages=True,
            ban_users=True,
            change_info=True,
            invite_users=True,
            title="Admin",
        )
        fm = translate("Promoted", event.chat_id)
        await event.reply(f"{fm} **{user.first_name}** **{chat.title}**")
    except:
        await event.reply(translate("Seems like I don't have enough rights to do that.", event.chat_id))


@Zbot(pattern="^/setgpic$")
async def x_pic(e):
    event = e
    if not e.is_channel:
        return await e.reply(translate("This command is made to be used in groups!", event.chat_id))
    if e.from_id:
        if not await can_change_info(e, e.sender_id):
            return
    if not e.reply_to:
        return await e.reply(translate("Reply to some photo or file to set new chat pic!", event.chat_id))
    reply = await e.get_reply_message()
    if e.chat.admin_rights:
        if not e.chat.admin_rights.change_info:
            return await e.reply(translate("Error! Not enough rights to change chat photo", event.chat_id))
    else:
        return
    if not reply.media:
        return await e.reply(translate("That's not a valid image for group pic!", event.chat_id))
    elif isinstance(reply.media, MessageMediaPhoto):
        photo = reply.media.photo
    elif (
        isinstance(reply.media, MessageMediaDocument)
        and reply.media.document.mime_type.split("/", 1)[0] == "image"
    ):
        photo = reply.media.document
        photo_x = await event.client.download_media(photo, "photo.jpg")
        photo = await e.client.upload_file(photo_x)
        os.remove(photo_x)
    else:
        return await e.reply(translate("That's not a valid image for group photo!", event.chat_id))
    try:
        await event.client(EditPhotoRequest(e.chat_id, photo))
    except Exception as x:
        return await e.reply(str(x))
    await e.reply(translate("✨ Successfully set new chatpic!", event.chat_id))


@Zbot(pattern="^/setgtitle(?: |$|@Zaid2_Robot)(.*)")
async def x_title(e):
    event = e
    if not e.is_group:
        return await e.reply(translate("This command is made to be used in groups!", event.chat_id))
    if e.from_id:
        if not await can_change_info(e, e.sender_id):
            return
    if not e.pattern_match.group(1):
        return await e.reply(translate("Enter some text to set new title in your chat!", event.chat_id))
    if e.chat.admin_rights:
        if not e.chat.admin_rights.change_info:
            return await e.reply(translate("Error! Not enough rights to change chat title", event.chat_id))
    else:
        return
    text = e.pattern_match.group(1)
    try:
        await e.client(EditTitleRequest(e.chat_id, text))
        await e.reply(translate(f"✨ Successfully set **{text}** as new chat title!", event.chat_id))
    except ChatNotModifiedError:
        await e.reply(translate(f"✨ Successfully set **{text}** as new chat title!", event.chat_id))
    except Exception as x:
        await e.reply(str(x))


@Zbot(pattern="^/setgsticker$")
async def x_sticker_set(e):
    event = e
    if not e.is_channel:
        return await e.reply(translate("This command is made to be used in groups!", event.chat_id))
    if e.from_id:
        if not await can_change_info(e, e.sender_id):
            return
    if not e.reply_to:
        return await e.reply(translate("Reply to some sticker to set new chat sticker pack!", event.chat_id))
    reply = await e.get_reply_message()
    if not reply.media:
        return await e.reply(translate(
            "You need to reply to some sticker to set chat sticker set!", event.chat_id)
        )
    if not isinstance(reply.media, MessageMediaDocument):
        return await e.reply(translate(
            "You need to reply to some sticker to set chat sticker set!", event.chat_id)
        )
    x_meme = reply.media.document.mime_type
    if not str(x_meme) == "image/webp":
        return await e.reply(translate(
            "You need to reply to some sticker to set chat sticker set!", event.chat_id)
        )
    sticker_set_id = sticker_set_access_hash = None
    try:
        for x in range(len(reply.media.document.attributes)):
            _x = reply.media.document.attributes[x]
            if isinstance(_x, DocumentAttributeSticker):
                sticker_set_id = _x.stickerset.id
                sticker_set_access_hash = _x.stickerset.access_hash
    except Exception as x:
        return await e.reply(translate(
            "You need to reply to some sticker to set chat sticker set!", event.chat_id) + str(x)
        )
    if not sticker_set_id:
        return await e.reply(translate("Failed to find the sticker set for the sticker!", event.chat_id))
    try:
        await e.client(
            SetStickersRequest(
                e.chat_id,
                InputStickerSetID(
                    id=sticker_set_id, access_hash=sticker_set_access_hash
                ),
            )
        )
        await e.reply(translate(f"✨ Successfully set new group stickers in {e.chat.title}!", event.chat_id))
    except ChatNotModifiedError:
        await e.reply(translate(f"✨ Successfully set new group stickers in {e.chat.title}!", event.chat_id))
    except ParticipantsTooFewError:
        await e.reply(translate("Failed to set stickerset, Not enough participants.", event.chat_id))
    except Exception as x:
        await e.reply(str(x))


@Zbot(pattern="^/(setgdesc|setgdescription)(?: |$|@Zaid2_Robot)(.*)")
async def x_description(e):
    event = e
    if not e.is_channel:
        return await e.reply(translate("This command is made to be used in groups!", event.chat_id))
    if e.from_id:
        if not await can_change_info(e, e.sender_id):
            return
    if not e.reply_to:
        try:
            about = e.text.split(None, 1)[1]
        except IndexError:
            about = ""
        if not about:
            await e.reply(translate(f"✨ Sucessfully removed chat description in {e.chat.title}", event.chat_id))
    elif e.reply_to:
        reply = await e.get_reply_message()
        if not reply.text:
            await e.reply(translate(f"✨ Sucessfully removed chat description in {e.chat.title}", event.chat_id))
        about = reply.text or ""
    try:
        await event.client(EditChatAboutRequest(e.chat_id, about))
        if not about == "":
            await e.reply(translate(f"✨ Successfully updated chat description in {e.chat.title}!", event.chat_id))
    except ChatAboutNotModifiedError:
        if not about == "":
            await e.reply(translate(f"✨ Successfully updated chat description in {e.chat.title}!", event.chat_id))
    except Exception as x:
        await e.reply(str(x))
