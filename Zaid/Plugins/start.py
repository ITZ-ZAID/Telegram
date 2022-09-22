from Zaid import Zaid
from telethon import events, Button
import random
from .language import translate
import re
from telethon.tl.types import Message
from telethon.tl.custom import Button
from telethon.events import NewMessage, CallbackQuery
import asyncio
from telethon.errors.rpcerrorlist import (
    FloodWaitError,
    UserBlockedError,
    ChatWriteForbiddenError,
)
from .. import CMD_HELP
from google_trans_new.constant import LANGUAGES
from google_trans_new import google_translator
translator = google_translator()
from Zaid.utils import Zbot, Zinline
from Zaid.Plugins.sql.language import set_lang as set_langu

IMG = ["https://telegra.ph/file/556e5178cd3a00c1b6cf0.png",
       "https://telegra.ph/file/bf9e7214e0335060e3fa6.png",
       "https://telegra.ph/file/f8e5a40af4a42e15c6895.png",
       "https://telegra.ph/file/3930433d95ab5be1ec662.png",
       "https://telegra.ph/file/6338d96b1c11ffe72f318.png"
]
line = "───────────────────────"

plugins = [
    "Admin",
    "AFK",
    "Approval",
    "AI-Chatbot",
    "Filters",
    "Greetings",
    "Locks",
    "Stickers",
    "Rules",
    "Song",
    "Reports",
    "Quotly",
    "Purges",
    "Pin",
    "Misc",
    "Force-Sub",
    "Extras",
    "Bans",
    "Blocklist",
    "Antiflood",
    "CAPTCHA",
    "Warnings",
]

@Zbot(pattern="^/start ?(.*)")
async def start(event):
    hi = translate("Hello", event.chat_id)
    if event.is_private:
       IMSG = f"{random.choice(IMG)}"
       hj = translate("✘ I am an group management bot with some fun extra ;)", event.chat_id)
       hj2 = translate("✘ I can do a Verity of things, most common of em are:", event.chat_id)
       hj3 = translate("‣ Restrict users with ban permission.", event.chat_id)
       hj4 = translate("‣ Greet users with media + text and buttons, with proper formatting.", event.chat_id)
       hj5 = translate("‣ Warn users according to the options set and restrict them accordingly.", event.chat_id)
       hj6 = translate("‣ Save notes and filters with proper formatting and reply markup.", event.chat_id)
       hj7 = translate("‣ I can play music in your groups voice chat", event.chat_id)
       hj8 = translate("‣ I have many features which you like", event.chat_id)
       hj9 = translate("to change the bot language", event.chat_id)
       hj10 = translate("There's even more! This is just the tip of the iceberg. Do note i need to be promoted with proper admin permission to perform from. else won't be able to perform as said.", event.chat_id)
       await event.reply(
             f"{hi} {event.sender.first_name}\n{line}\n{hj}\n{hj2}\n{hj3}\n{hj4}\n{hj5}\n{hj6}\n{hj7}\n{hj8}\n‣ /setlang {hj9}\n{line}\n{hj10}", 
             buttons=[
        [Button.url(translate("Add me to your group ➕", event.chat_id), url="t.me/Zaid2_Robot?startgroup=true")],
        [Button.url(translate("Channel 📢", event.chat_id), url="t.me/TheUpdatesChannel"), Button.url(translate("Support 🌎", event.chat_id), url="t.me/thesupportchat")],
        [Button.inline(translate("Change language 🌐", event.chat_id), data=f"langs")]])
    if event.is_group:
        IMSG = f"{random.choice(IMG)}"
        await event.client.send_file(event.chat_id,
             IMSG,
             caption="{} {}".format(hi, event.sender.first_name), 
             buttons=[
         [Button.url("Add me to your group ➕", url="t.me/Zaid2_Robot?startgroup=true")]])


JSONDB = None

if not JSONDB:
    JSONDB = {"users": [], "language": {}}


def split_list(lis, index):
    new_ = []
    while lis:
        new_.append(lis[:index])
        lis = lis[index:]
    return new_


Buttons = [Button.inline(LANGUAGES[lang].upper(), f"stt-{lang}") for lang in LANGUAGES]
# 2 Rows
Buttons = split_list(Buttons, 2)
# 5 Columns
Buttons = split_list(Buttons, 5)





@Zinline(pattern=r"langs")
async def set_language(event):
    if not event.is_private:
       try:
           _s = await event.client.get_permissions(event.chat_id, event.sender_id)
           if not _s.is_admin:
              return
       except Exception:
           pass
    bts = Buttons[0].copy()
    bts.append([Button.inline("Next ▶", "btshh"), Button.inline("Cancel ❌", "cncll")])
    await event.edit("Choose your desired language..", buttons=bts)


@Zinline(pattern=r"btshh(.*)")
async def click_next(event):
    if not event.is_private:
       try:
           _s = await event.client.get_permissions(event.chat_id, event.sender_id)
           if not _s.is_admin:
              return
       except Exception:
           pass
    data = event.data_match.group(1).decode("utf-8")
    if not data:
        val = 1
    else:
        prev_or_next = data[0]
        val = int(data[1:])
        if prev_or_next == "p":
            val -= 1
        else:
            val += 1
    try:
        bt = Buttons[val].copy()
    except IndexError:
        val = 0
        bt = Buttons[0].copy()
    if val == 0:
        bt.append([Button.inline("Next ▶", "btshh"), Button.inline("Cancel ❌", "cncll")])
    else:
        bt.extend(
            [
                [
                    Button.inline("◀ Prev", f"btshhp{val}"),
                    Button.inline("Next ▶", f"btshhn{val}"),
                ],
                [Button.inline("Cancel ❌", "cncll")],
            ]
        )
    await event.edit(buttons=bt)


@Zinline(pattern=r"cncll")
async def maggie(event):
    if not event.is_private:
       try:
           _s = await event.client.get_permissions(event.chat_id, event.sender_id)
           if not _s.is_admin:
              return
       except Exception:
           pass
    await event.delete()



@Zinline(pattern=r"stt-(.*)")
async def set_lang(event):
    match = event.data_match.group(1).decode("utf-8")
    if not event.is_private:
       try:
           _s = await event.client.get_permissions(event.chat_id, event.sender_id)
           if not _s.is_admin:
              return
       except Exception:
           pass
    set_langu(event.chat_id, match)
    code_lang = {code: name for code, name in LANGUAGES.items()}
    name = code_lang[match]
    name = name[0].upper() + name[1:]
    await event.edit(f"Language successfully changed to {name} !")



@Zbot(pattern="^/help ?(.*)")
async def help(event):
    if event.is_group:
        buttons = [
            [Button.url("❔ Help", "https://t.me/Zaid2_Robot?start=_help")],
        ]
        await event.reply(
            "Contact me in PM to get the list of possible commands.",
            buttons=buttons,
        )
    elif event.is_private:
        buttons = paginate_help()
        await event.reply("Read all the useful commands", buttons=buttons)


@Zinline(pattern=r"us_plugin_(.*)")
async def us_0(event):
    pl_name = (event.pattern_match.group(1)).decode()
    try:
        pl_help = CMD_HELP[pl_name][1]
    except KeyError:
        pl_help = "The help menu for this module will be provided soon!"
    await event.edit(
        pl_help,
        buttons=[
            Button.inline("Close", data="cncll"),
            Button.inline("Back", data="help_menu"),
        ],
    )

@Zinline(pattern=r"help_menu")
async def help_menu(event):
    buttons = paginate_help()
    await event.edit(help_caption, buttons=buttons)

@Zbot(pattern="^/start _help")
async def st_help(e):
    buttons = paginate_help()
    await e.respond(help_caption, buttons=buttons)


def paginate_help():
    helpable_plugins = sorted(plugins)
    modules = [
        Button.inline(x, data=f"us_plugin_{x.lower()}") for x in helpable_plugins
    ]
    pairs = list(
        zip(
            modules[::3],
            modules[1::3],
            modules[2::3],
        )
    )
    modulo_page = 0 % 1
    pairs = pairs[modulo_page * 8 : 8 * (modulo_page + 1)] + [
        (Button.inline("Close", data="cncll"),)
    ]
    return pairs
