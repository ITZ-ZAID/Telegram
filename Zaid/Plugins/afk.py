import random
import re
import sre_constants
import time

from telethon.tl.types import MessageEntityMention, MessageEntityMentionName, User

from .. import CMD_HELP
from .. import Zaid
from ..utils import Zbot
from . import get_readable_time
from .mongodb import afk_db as db

options = [
    "**{}** is here!, Was afk for {}",
    "**{}** is back!, Been away for {}",
    "**{}** is now in the chat!, Back after {}",
    "**{}** is awake!, Was afk for {}",
    "**{}** is back online!, Been away for {}",
    "**{}** is finally here!, Was afk for {}",
    "Welcome back! **{}**, Was afk for {}",
    "Where is **{}**?\nIn the chat!, Was afk for {}",
    "Pro **{}**, is back alive!, Was afk for {}",
]


@Zbot(pattern=r"(.*?)")
async def afk(e):
    if not e.sender:
        return
    for x in ["+afk", "/afk", "!afk", "?afk", "brb", "i go away"]:
        if (e.text.lower()).startswith(x):
            try:
                reason = e.text.split(None, 1)[1]
            except IndexError:
                reason = ""
            if (e.text.lower()).startswith("i go away"):
                reason = reason.replace("go away", "")
            _x = await e.reply(
                "<b>{}</b> is now AFK !".format(e.sender.first_name), parse_mode="html"
            )
            return db.set_afk(e.sender_id, e.sender.first_name, reason)
    afk = db.get_afk(e.sender_id)
    if afk:
        xp = get_readable_time(time.time() - int(afk.get("time")))
        await e.reply((random.choice(options)).format(e.sender.first_name, xp))
        db.unset_afk(e.sender_id)


@Zbot(pattern=r"(.*?)")
async def afk_check(e):
    if e.is_private:
        return
    if not e.from_id:
        return
    user_id = None
    if e.reply_to:
        r = await e.get_reply_message()
        if r:
            if r.sender:
                if isinstance(r.sender, User):
                    user_id = r.sender_id
                else:
                    return
            else:
                return
    else:
        try:
            for (ent, txt) in e.get_entities_text():
                if ent.offset != 0:
                    break
                if isinstance(ent, MessageEntityMention):
                    pass
                elif isinstance(ent, MessageEntityMentionName):
                    pass
                else:
                    return
                a = txt.split()[0]
                user = await tbot.get_input_entity(a)
                user_id = user.user_id
        except:
            return
    if not user_id:
        return
    if e.sender_id == user_id or not user_id:
        return
    x_afk = db.get_afk(user_id)
    if x_afk:
        time_seen = get_readable_time(time.time() - int(x_afk["time"]))
        reason = ""
        if x_afk["reason"]:
            r_eson = x_afk["reason"]
            reason = f"Reason: <code>{r_eson}</code>"
        await e.reply(
            "<b>{} is AFK !</b>\nLast Seen: {} ago.\n{}".format(
                x_afk["first_name"], time_seen, reason
            ),
            parse_mode="html",
        )


def infinite_checker(repl):
    regex = [
        r"\((.{1,}[\+\*]){1,}\)[\+\*].",
        r"[\(\[].{1,}\{\d(,)?\}[\)\]]\{\d(,)?\}",
        r"\(.{1,}\)\{.{1,}(,)?\}\(.*\)(\+|\* |\{.*\})",
    ]
    for match in regex:
        status = re.search(match, repl)
        return bool(status)


DELIMITERS = ("/", ":", "|", "_")


def seperate_sed(sed_string):
    if (
        len(sed_string) >= 3
        and sed_string[1] in DELIMITERS
        and sed_string.count(sed_string[1]) >= 2
    ):
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == "\\":
                counter += 1

            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break

            counter += 1

        else:
            return None
        while counter < len(sed_string):
            if (
                sed_string[counter] == "\\"
                and counter + 1 < len(sed_string)
                and sed_string[counter + 1] == delim
            ):
                sed_string = sed_string[:counter] + sed_string[counter + 1 :]

            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break

            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()


@Zbot(pattern=r"^s([/:|_]).*?\1.*")
async def reg_x__se_dd(e):
    if not e.text:
        return
    if e.reply_to_msg_id:
        r = await e.get_reply_message()
        if not r.text:
            return
        fix = r.text
        try:
            x, y, z = seperate_sed(e.text)
        except:
            return
        if not x:
            return await e.reply(
                "You're trying to replace... " "nothing with something?"
            )
        try:
            if infinite_checker(x):
                return await e.reply("Nice try -_-")

            if "i" in z and "g" in z:
                text = re.sub(x, y, fix, flags=re.I).strip()
            elif "i" in z:
                text = re.sub(x, y, fix, count=1, flags=re.I).strip()
            elif "g" in z:
                text = re.sub(x, y, fix).strip()
            else:
                text = re.sub(x, y, fix, count=1).strip()
        except sre_constants.error as xc:
            return await e.reply("f off, " + str(xc))
        if len(text) >= 4096:
            await e.reply(
                "The result of the sed command was too long for \
                                                 telegram!"
            )
        elif text:
            await e.respond(text, reply_to=e.reply_to_msg_id or e.id)


__name__ = "afk"
__help__ = """
Here is the help for **AFK** module:

- /afk :mark yourself as AFK(away from keyboard).
- brb `<reason>`: same as the afk command - but not a command.
When marked as **AFK**, any mentions will be replied to with a message to say you're not Available!
"""
CMD_HELP.update({__name__: [__name__, __help__]})
