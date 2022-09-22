import datetime

from telethon import Button, events, types

import Zaid.Plugins.mongodb.notes_db as db
from Zaid import Zaid
from Zaid.utils import Zbot, Zinline
from .language import translate
from . import (
    button_parser,
    can_change_info,
    cb_is_owner,
    format_fill,
    get_reply_msg_btns_text,
    is_admin,
    is_owner,
)


def file_ids(msg):
    if isinstance(msg.media, types.MessageMediaDocument):
        file_id = msg.media.document.id
        access_hash = msg.media.document.access_hash
        file_reference = msg.media.document.file_reference
        type = "doc"
    elif isinstance(msg.media, types.MessageMediaPhoto):
        file_id = msg.media.photo.id
        access_hash = msg.media.photo.access_hash
        file_reference = msg.media.photo.file_reference
        type = "photo"
    elif isinstance(msg.media, types.MessageMediaGeo):
        file_id = msg.media.geo.long
        access_hash = msg.media.geo.lat
        file_reference = None
        type = "geo"
    else:
        return None, None, None, None
    return file_id, access_hash, file_reference, type


def id_tofile(file_id, access_hash, file_reference, type):
    if file_id == None:
        return None
    if type == "doc":
        return types.InputDocument(
            id=file_id, access_hash=access_hash, file_reference=file_reference
        )
    elif type == "photo":
        return types.Photo(
            id=file_id,
            access_hash=access_hash,
            file_reference=file_reference,
            date=datetime.datetime.now(),
            dc_id=5,
            sizes=[718118],
        )
    elif type == "geo":
        geo_file = types.InputMediaGeoPoint(
            types.InputGeoPoint(float(file_id), float(access_hash))
        )
        return geo_file


@Zbot(pattern="^/save ?(.*)")
async def save(event):
    if (
        event.text.startswith("+saved")
        or event.text.startswith("/saved")
        or event.text.startswith("?saved")
        or event.text.startswith("!saved")
    ):
        return
    if event.from_id:
        file_id = access_hash = file_reference = type = None
        if event.is_group:
            if not await can_change_info(event, event.sender_id):
                return
        try:
            f_text = event.text.split(None, 1)[1]
        except IndexError:
            f_text = None
        if not event.reply_to and not f_text:
            return await event.reply(translate("You need to give the note a name!", event.chat_id))
        elif event.reply_to:
            xp = f_text.split(None, 1)
            n = xp[0]
            r_msg = await event.get_reply_message()
            if r_msg.media:
                file_id, access_hash, file_reference, type = file_ids(r_msg)
            if not r_msg.text and not r_msg.media:
                return await event.reply(translate("you need to give the note some content!", event.chat_id))
            if not n:
                return await event.reply(translate("You need to give the note a name!", event.chat_id))
            note = r_msg.text or ""
            if len(xp) == 2:
                note = xp[1]
            if r_msg.reply_markup:
                _buttons = get_reply_msg_btns_text(r_msg)
                note = r_msg.text + _buttons
            x = [n, note]
        elif f_text:
            n = f_text or "x"
            x = n.split(" ", 1)
            if len(x) == 1:
                return await event.reply(translate("you need to give the note some content!", event.chat_id))
        db.save_note(
            event.chat_id, x[0], x[1], file_id, access_hash, file_reference, type
        )
        mm = translate("Saved note", event.chat_id)
        await event.reply(f"{mm} `{x[0]}`")


@Zbot(pattern="^/privatenotes ?(.*)")
async def pnotes(event):
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not event.from_id:
        return  # for now
    if event.is_group:
        if not await can_change_info(event, event.sender_id):
            return
    arg = event.pattern_match.group(1)
    if not arg:
        mode = db.get_pnotes(event.chat_id)
        if mode:
            await event.reply(translate(
                "Your notes are currently being sent in private. neko will send a small note with a button which redirects to a private chat.", event.chat_id)
            )
        else:
            await event.reply(translate("Your notes are currently being sent in the group.", event.chat_id))
    elif arg in ["y", "yes", "on"]:
        await event.reply(translate(
            "neko will now send a message to your chat with a button redirecting to PM, where the user will receive the note.", event.chat_id)
        )
        db.change_pnotes(event.chat_id, True)
    elif arg in ["n", "no", "off"]:
        await event.reply(translate("Now send notes straight to the group.", event.chat_id))
        db.change_pnotes(event.chat_id, False)
    else:
        await event.reply(translate(
            f"failed to get boolean value from input: expected one of y/yes/on or n/no/off; got: {arg}", event.chat_id)
        )


@Zaid.on(events.NewMessage(pattern=r"\#(\S+)"))
async def new_message_note(event):
    name = event.pattern_match.group(1)
    note = db.get_note(event.chat_id, name)
    if not note:
        return
    p_mode = db.get_pnotes(event.chat_id)
    if note["note"] == "Nil":
        caption = None
    else:
        caption = note["note"]
        if "{admin}" in caption:
            caption = caption.replace("{admin}", "")
            if event.is_group:
                if not await is_admin(event.chat_id, event.sender_id):
                    return
        elif "{private}" in caption:
            caption = caption.replace("{private}", "")
            p_mode = True
        elif "{noprivate}" in caption:
            caption = caption.replace("{noprivate}", "")
            p_mode = False
    if p_mode == False:
        file = id_tofile(note["id"], note["hash"], note["ref"], note["mtype"])
        if caption:
            caption, buttons = button_parser(caption)
        else:
            buttons = None
        if caption == "\n":
            caption = ""
        tm = 0
        if caption:
            caption = await format_fill(event, caption, tm)
        await event.respond(
            caption,
            file=file,
            buttons=buttons,
            parse_mode="md",
            reply_to=event.reply_to_msg_id or event.id,
        )
    else:
        await event.respond(translate(
            "Tap here to view '{name}' in your private chat.", event.chat_id),
            buttons=Button.url(
                translate("Click me", event.chat_id),
                data=f"t.me/Zaid2_Robot?start=notes_{event.chat_id}|{name}",
            ),
            reply_to=event.reply_to_msg_id or event.id,
        )


@Zbot(pattern="^/get ?(.*)")
async def get(event):
    name = event.pattern_match.group(1)
    if not name:
        return await event.reply(translate("Not enough arguments!", event.chat_id))
    note = db.get_note(event.chat_id, name)
    if not note:
        return await event.reply(translate("No note found!", event.chat_id))
    p_mode = db.get_pnotes(event.chat_id)
    if note["note"] == "Nil":
        caption = None
    else:
        caption = note["note"]
        if "{admin}" in caption:
            caption = caption.replace("{admin}", "")
            if event.is_group:
                if not await is_admin(event.chat_id, event.sender_id):
                    return
        elif "{private}" in caption:
            caption = caption.replace("{private}", "")
            p_mode = True
        elif "{noprivate}" in caption:
            caption = caption.replace("{noprivate}", "")
            p_mode = False
    if p_mode == False:
        file = id_tofile(note["id"], note["hash"], note["ref"], note["mtype"])
        tm = 0
        if caption:
            caption, buttons = button_parser(caption)
            caption = await format_fill(event, caption, tm)
        else:
            buttons = None
        await event.respond(
            caption,
            file=file,
            buttons=buttons,
            parse_mode="md",
            reply_to=event.reply_to_msg_id or event.id,
        )
    else:
        await event.respond(translate(
            "Tap here to view '{name}' in your private chat.", event.chat_id),
            buttons=Button.inline(
                translate("Click me", event.chat_id),
                data=f"t.me/Zaid2_Robot?start=notes_{event.chat_id}|{name}",
            ),
            reply_to=event.reply_to_msg_id or event.id,
        )


@Zbot(pattern="^/clear ?(.*)")
async def clear(event):
    if (
        event.text.startswith("+clearall")
        or event.text.startswith("/clearall")
        or event.text.startswith("?clearall")
        or event.text.startswith("!clearall")
    ):
        return
    if not event.from_id:
        return  # for now
    if event.is_group:
        if not await can_change_info(event, event.sender_id):
            return
    try:
        args = event.text.split(None, 1)[1]
    except IndexError:
        args = None
    if not args:
        return await event.reply(translate("Not enough arguments!", event.chat_id))
    noted = db.get_note(event.chat_id, args)
    if noted:
        kk = translate("Deleted note", event.chat_id)
        await event.reply("{} '{}'".format(kk, args))
        return db.delete_note(event.chat_id, args)
    await event.reply(translate("You haven't saved any notes with this name yet!", event.chat_id))


@Zbot(pattern="^/(saved|Saved|Notes|notes)")
async def alln(event):
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    p_mode = db.get_pnotes(event.chat_id)
    if p_mode:
        await event.respond(translate(
            "Tap here to view all notes in this chat.", event.chat_id),
            buttons=Button.url(
                translate("Click Me!", event.chat_id),
                f"t.me/Missneko_bot?start=allnotes_{event.chat_id}",
            ),
            reply_to=event.reply_to_msg_id or event.id,
        )
    else:
        notes = db.get_all_notes(event.chat_id)
        if not notes:
            return await event.reply(translate(f"No notes in {event.chat.title}!", event.chat_id))
        txt = f"List of notes in {event.chat.title}:"
        for a_note in notes:
            txt += f"\n- `#{a_note}`"
        txt += translate("\nYou can retrieve these notes by using `/get notename`, or `#notename`", event.chat_id)
        await event.respond(txt, reply_to=event.reply_to_msg_id or event.id)


@Zbot(pattern="^/clearall")
async def delallfilters(event):
    if event.is_group:
        if event.from_id:
            if not await is_owner(event, event.sender_id):
                return
    buttons = [
        [Button.inline(translate("Delete all notes", event.chat_id), data="clearall")],
        [Button.inline(translate("Cancel", event.chat_id), data="cancelclearall")],
    ]
    text = translate(f"Are you sure you would like to clear **ALL** notes in {event.chat.title}? This action cannot be undone.", event.chat_id)
    await event.reply(text, buttons=buttons)


@Zinline(pattern="clearall")
async def allcb(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Deleted all chat notes.", event.chat_id), buttons=None)
    db.delete_all_notes(event.chat_id)


@Zinline(pattern="cancelclearall")
async def stopallcb(event):
    if not await cb_is_owner(event, event.sender_id):
        return
    await event.edit(translate("Clearing of all notes has been cancelled.", event.chat_id), buttons=None)


@Zbot(pattern="^/start notes_(.*)")
async def start_notes(event):
    data = event.pattern_match.group(1)
    chat, name = data.split("|", 1)
    chat_id = int(chat.strip())
    name = name.strip()
    note = db.get_note(chat_id, name)
    file = id_tofile(note["id"], note["hash"], note["ref"], note["mtype"])
    caption = note["note"]
    if caption:
        caption, buttons = button_parser(caption)
    else:
        buttons = None
    await event.reply(caption, file=file, buttons=buttons)


@Zbot(pattern="^/start allnotes_(.*)")
async def rr(event):
    chat_id = int(event.pattern_match.group(1))
    all_notes = db.get_all_notes(event.chat_id)
    OUT_STR = translate("**Notes:**\n", event.chat_id)
    for a_note in all_notes:
        luv = f"{chat_id}_{a_note}"
        OUT_STR += f"- [{a_note}](t.me/Zaid2_Robot?start=notes_{luv})\n"
    OUT_STR += "You can retrieve these notes by tapping on the notename."
    await event.reply(OUT_STR, link_preview=False)



__help__ = """
 ❍ /get <notename>*:* get the note with this notename
 ❍ #<notename>*:* same as /get
 ❍ /notes or /saved*:* list all saved notes in this chat
 ❍ /number *:* Will pull the note of that number in the list
If you would like to retrieve the contents of a note without any formatting, use `/get <notename> noformat`. This can \
be useful when updating a current note
*Admins only:*
 ❍ /save <notename> <notedata>*:* saves notedata as a note with name notename
A button can be added to a note by using standard markdown link syntax - the link should just be prepended with a \
`buttonurl:` section, as such: `[somelink](buttonurl:example.com)`. Check `/markdownhelp` for more info
 ❍ /save <notename>*:* save the replied message as a note with name notename
 Separate diff replies by `%%%` to get random notes
 *Example:* 
 `/save notename
 Reply 1
 %%%
 Reply 2
 %%%
 Reply 3`
 ❍ /clear <notename>*:* clear note with this name
 ❍ /clearall*:* removes all notes from the group
 *Note:* Note names are case-insensitive, and they are automatically converted to lowercase before getting saved.
"""

__name__ = "notes"
CMD_HELP.update({__name__: [__name__, __help__]})
