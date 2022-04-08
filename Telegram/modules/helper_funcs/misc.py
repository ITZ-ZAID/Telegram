from typing import Dict, List
import typing
from uuid import uuid4
from Telegram import NO_LOAD
from telegram import MAX_MESSAGE_LENGTH, Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, InlineQueryResultArticle, InputTextMessageContent
from telegram.error import TelegramError
import requests
import json
import zlib
import base64
from urllib.parse import urlparse, urljoin, urlunparse
import base58
from Crypto import Random, Hash, Protocol
from Crypto.Cipher import AES
from math import ceil


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    if len(msg) < MAX_MESSAGE_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MAX_MESSAGE_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    # Else statement at the end of the for loop, so append the leftover string.
    result.append(small_msg)

    return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
            modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.replace(" ", "_").lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
            modules = sorted(
                 [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.replace(" ", "_").lower()
                    ),
                )
                for x in module_dict.values()
            ]
             )

    pairs = list(zip(modules[::3], modules[1::3], modules[2::3]))
    i = 0
    for m in pairs:
        for _ in m:
            i += 1
    if len(modules) - i == 1:
        pairs.append((modules[-1],))
    elif len(modules) - i == 2:
        pairs.append(
            (
                modules[-2],
                modules[-1],
            )
        )

    COLUMN_SIZE = 7

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[
            modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)
        ] + [
            (
                EqInlineKeyboardButton(
                    "☜",
                    callback_data="{}_prev({})".format(prefix, modulo_page),
                ),
                EqInlineKeyboardButton(
                    "Go Home",
                    callback_data="start_back",
                ),
                EqInlineKeyboardButton(
                    "☞",
                    callback_data="{}_next({})".format(prefix, modulo_page),
                ),
            )
        ]

    return pairs

def article(
    title: str = "",
    description: str = "",
    message_text: str = "",
    thumb_url: str = None,
    reply_markup: InlineKeyboardMarkup = None,
    disable_web_page_preview: bool = False,
) -> InlineQueryResultArticle:

    return InlineQueryResultArticle(
        id=uuid4(),
        title=title,
        description=description,
        thumb_url=thumb_url,
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            disable_web_page_preview=disable_web_page_preview,
        ),
        reply_markup=reply_markup,
    )

def send_to_list(
    bot: Bot, send_to: list, message: str, markdown=False, html=False
) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    return "".join(
        "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        if btn.same_line
        else "\n[{}](buttonurl://{})".format(btn.name, btn.url)
        for btn in buttons
    )


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def is_module_loaded(name):
    return name not in NO_LOAD

def upload_text(data: str) -> typing.Optional[str]:
    passphrase = Random.get_random_bytes(32)
    salt = Random.get_random_bytes(8)
    key = Protocol.KDF.PBKDF2(passphrase, salt, 32, 100000, hmac_hash_module=Hash.SHA256)
    compress = zlib.compressobj(wbits=-15)
    paste_blob = compress.compress(json.dumps({'paste': data}, separators=(',', ':')).encode()) + compress.flush()
    cipher = AES.new(key, AES.MODE_GCM)
    paste_meta = [[base64.b64encode(cipher.nonce).decode(), base64.b64encode(salt).decode(), 100000, 256, 128, 'aes', 'gcm', 'zlib'], 'syntaxhighlighting', 0, 0]
    cipher.update(json.dumps(paste_meta, separators=(',', ':')).encode())
    ct, tag = cipher.encrypt_and_digest(paste_blob)
    resp = requests.post('https://bin.nixnet.services', headers={'X-Requested-With': 'JSONHttpRequest'}, data=json.dumps({'v': 2, 'adata': paste_meta, 'ct': base64.b64encode(ct + tag).decode(), 'meta': {'expire': '1week'}}, separators=(',', ':')))
    data = resp.json()
    url = list(urlparse(urljoin('https://bin.nixnet.services', data['url'])))
    url[5] = base58.b58encode(passphrase).decode()
    return urlunparse(url)
