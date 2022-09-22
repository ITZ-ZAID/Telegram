"""Why On Ptb?
Because in telethon it's response
Two times
"""

import re
import asyncio

from google_trans_new.constant import LANGUAGES
from google_trans_new import google_translator
translator = google_translator()
from Zaid.Plugins.sql.language import get_chat_lang, set_lang as set_language
from Zaid import Zaid, dispatcher

from Zaid.utils import Zinline
from typing import Union, List, Dict, Callable, Generator, Any
import itertools
from collections.abc import Iterable
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from cachetools import TTLCache
from telegram import Chat, ChatMember, ParseMode, Update, TelegramError, User
from telegram.ext import CallbackContext
from functools import wraps


DEL_CMDS = True
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10)


def is_user_admin(update: Update, user_id: int, member: ChatMember = None) -> bool:
    chat = update.effective_chat
    msg = update.effective_message
    if (
            chat.type == "private"
            or chat.all_members_are_administrators
            or (msg.reply_to_message and msg.reply_to_message.sender_chat is not None and
                msg.reply_to_message.sender_chat.type != "channel")
    ):
        return True

    if not member:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except KeyError:
            # KeyError happened means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future usage...
            chat_admins = dispatcher.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            if user_id in admin_list:
                return True
            return False

def user_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        # bot = context.bot
        user = update.effective_user
        # chat = update.effective_chat

        if user and is_user_admin(update, user.id):
            return func(update, context, *args, **kwargs)
        elif not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except TelegramError:
                pass
        else:
            update.effective_message.reply_text(
                "Who dis non-admin telling me what to do?"
            )

    return is_admin

def user_admin_no_reply(func):
    @wraps(func)
    def is_not_admin_no_reply(
            update: Update, context: CallbackContext, *args, **kwargs
    ):
        # bot = context.bot
        user = update.effective_user
        # chat = update.effective_chat

        if user and is_user_admin(update, user.id):
            return func(update, context, *args, **kwargs)
        elif not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except TelegramError:
                pass

    return is_not_admin_no_reply


def split_list(lis, index):
    new_ = []
    while lis:
        new_.append(lis[:index])
        lis = lis[index:]
    return new_


Buttons = [InlineKeyboardButton(text=LANGUAGES[lang].upper(), callback_data=f"st-{lang}") for lang in LANGUAGES]
# 2 Rows
Buttons = split_list(Buttons, 2)
# 5 Columns
Buttons = split_list(Buttons, 5)


def translate(text, sender, to_bing=False):
    if to_bing:
        return translator.translate(text, lang_tgt="en")
    get_ = get_chat_lang(sender)
    if get_:
        try:
            return translator.translate(text, lang_tgt=get_)
        except Exception as er:
            LOG.exception(er)
    return text





@user_admin_no_reply
def button_next(update: Update, _) -> None:
    query = update.callback_query
    chat = update.effective_chat
    data = query.data.split("-")[1]
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
        bt.append([InlineKeyboardButton(text="Next ▶", callback_data=f"btsh-"), InlineKeyboardButton(text="Cancel ❌", callback_data=f"cncl")])
    else:
        bt.extend(
            [
                [
                    InlineKeyboardButton(text="◀ Prev", callback_data=f"btsh-p{val}"),
                    InlineKeyboardButton(text="Next ▶", callback_data=f"btsh-n{val}"),
                ],
                [InlineKeyboardButton(text="Cancel ❌", callback_data=f"cncl")],
            ]
        )
    query.message.edit_text("Choose your desired language..", reply_markup=InlineKeyboardMarkup(bt))


@Zinline(pattern=r"cncl")
async def maggie(event):
    await event.delete()

@user_admin
def set_lang(update: Update, _) -> None:
    chat = update.effective_chat
    msg = update.effective_message
    keyb = Buttons[0].copy()
    keyb.append([InlineKeyboardButton(text="Next ▶", callback_data=f"btsh-"), InlineKeyboardButton(text="Cancel ❌", callback_data=f"cncl")])
    msg.reply_text("Choose your desired language..", reply_markup=InlineKeyboardMarkup(keyb))

@user_admin_no_reply
def cl_lang(update: Update, _) -> None:
    chat = update.effective_chat
    query = update.callback_query
    keyb = Buttons[0].copy()
    keyb.append([InlineKeyboardButton(text="Next ▶", callback_data=f"btsh-"), InlineKeyboardButton(text="Cancel ❌", callback_data=f"cncl")])
    query.message.edit_text("Choose your desired language..", reply_markup=InlineKeyboardMarkup(keyb))

@user_admin_no_reply
def lang_button(update: Update, _) -> None:
    query = update.callback_query
    chat = update.effective_chat

    query.answer()
    lang = query.data.split("-")[1]
    set_language(chat.id, lang)
    query.message.edit_text(f"Language successfully changed to {lang} !")



SETLANG_HANDLER = CommandHandler(["set_lang", "setlang", "language", "setlanguage"], set_lang)
SETLANG_BUTTON_HANDLER = CallbackQueryHandler(lang_button, pattern=r"st-")
UP_NEXT = CallbackQueryHandler(button_next, pattern=r"btsh-")
CL_LANG = CallbackQueryHandler(cl_lang, pattern=r"language")
dispatcher.add_handler(SETLANG_HANDLER)
dispatcher.add_handler(SETLANG_BUTTON_HANDLER)
dispatcher.add_handler(UP_NEXT)
dispatcher.add_handler(CL_LANG)
