import asyncio
import json
import math
import os
import random
import re
import shlex
import time
from random import choice, randint
from typing import Tuple
from urllib.parse import quote

from multicolorcaptcha import CaptchaGenerator
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pymongo import MongoClient
from requests import Request, Session
from telethon import Button, custom, events, types
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantRequest
from telethon.tl.functions.messages import GetInlineBotResultsRequest

from config import BOT_ID, MONGO_DB_URI, OWNER_ID
from Zaid import Zaid
from Zaid.Plugins.mongodb.chats_db import add_chat, is_chat
from .language import translate


ubot = None

SUDO_USERS = []
ELITES = []
DEVS = []
tbd = []
DEVS.append(OWNER_ID)

# DB
client = MongoClient(MONGO_DB_URI)
db = client["Melody"]

x_users = db.x_users



async def can_promote_users(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.add_admins:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanPromoteMembers.", event.chat_id)
            )
            return False
        return True


async def cb_can_promote_users(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.answer(translate("You have to be an admin to do this!", event.chat_id), alert=True)
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.add_admins:
            await event.edit(translate(
                "You are missing the following rights to use this command: CanPromoteMembers.", event.chat_id)
            )
            return False
        return True


async def cb_can_ban_users(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.answer(translate("You have to be an admin to do this!", event.chat_id), alert=True)
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.ban_users:
            await event.edit(translate(
                "You are missing the following rights to use this command: CanRestrictUsers.", event.chat_id)
            )
            return False
        else:
            return True


async def warn_button_perms(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.answer(translate("You have to be an admin to do this!", event.chat_id), alert=True)
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.ban_users:
            await event.answer(translate(
                "You are missing the following rights to use this command: CanRestrictMembers.", event.chat_id)
            )
            return False
        else:
            return True


async def can_change_info(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.change_info:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanChangeInfo.", event.chat_id)
            )
            return False
        return True


async def cb_can_change_info(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.change_info:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanChangeInfo.", event.chat_id)
            )
            return False
        return True


async def can_pin_messages(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.pin_messages:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanPinMessages.", event.chat_id)
            )
            return False
        return True


async def can_ban_users(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.ban_users:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanRestrictUsers.", event.chat_id)
            )
            return False
        return True


async def is_owner(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        await event.reply(translate(
            f"You need to be the chat owner of {event.chat.title} to do this.", event.chat_id)
        )
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True


async def cb_is_owner(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.answer(translate("You have to be an admin to do this!", event.chat_id), alert=True)
        return False
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        await event.edit(translate(
            f"You need to be the chat owner of {event.chat.title} to do this.", event.chat_id)
        )
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True


async def check_owner(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    else:
        return False


async def can_del_msg(event, user_id):
    try:
        p = await event.client(GetParticipantRequest(event.chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipant):
        await event.reply(translate("You have to be an admin to do this!", event.chat_id))
        return False
    elif isinstance(p.participant, types.ChannelParticipantCreator):
        return True
    elif isinstance(p.participant, types.ChannelParticipantAdmin):
        if not p.participant.admin_rights.delete_messages:
            await event.reply(translate(
                "You are missing the following rights to use this command: CanDeleteMessages.", event.chat_id)
            )
            return False
        return True


async def is_admin(chat_id, user_id):
    try:
        p = await Zaid(GetParticipantRequest(chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipantAdmin) or isinstance(
        p.participant, types.ChannelParticipantCreator
    ):
        return True
    else:
        return False


async def get_user(event):
    try:
        args = event.text.split(" ", 1)[1].split(" ", 1)
    except IndexError:
        args = None
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.sender_id)
        extra = "".join(args) if args else ""
    elif args:
        extra = None
        user = args[0]
        if len(args) == 2:
            extra = args[1]
        if user.isnumeric():
            user = int(user)
        if not user:
            await event.reply(translate("I don't know who you're talking about, you're going to need to specify a user...!", event.chat_id))
            return
        try:
            user_obj = await event.client.get_entity(user)
        except (TypeError, ValueError):
            await event.reply(translate("Looks like I don't have control over that user, or the ID isn't a valid one. If you reply to one of their messages, I'll be able to interact with them.", event.chat_id))
            return
    else:
        await event.reply(translate("I don't know who you're talking about, you're going to need to specify a user...!", event.chat_id))
        return
    return user_obj, extra


async def extract_time(message, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await message.reply(translate("Invalid time amount specified.", message.chat_id))
            return ""
        if unit == "m":
            bantime = int(time_num) * 60
        elif unit == "h":
            bantime = int(time_num) * 60 * 60
        elif unit == "d":
            bantime = int(time_num) * 24 * 60 * 60
        else:
            return
        return bantime
    else:
        await message.reply(translate(
            f"Invalid time type specified. Expected m,h, or d, got: {time_val[-1]}", message.chat_id)
        )
        return False


def g_time(time: int):
    if time >= 86400:
        time = int(time / (60 * 60 * 24))
        unit = "days"
    elif time >= 3600 < 86400:
        time = int(time / (60 * 60))
        unit = "hours"
    elif time >= 60 < 3600:
        time = int(time / 60)
        unit = "minutes"
    return " {} {}".format(time, unit)


BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((btnurl|buttonurl):(?:/{0,2})(.+?)(:same)?\))"
)


def button_parser(text):
    if "buttonalert" in text:
        text = text.replace("\n", "\\n").replace("\t", "\\t")
    buttons = []
    note_data = ""
    prev = 0
    for match in BTN_URL_REGEX.finditer(text):
        # Check if btnurl is escaped
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        # if even, not escaped -> create button
        if n_escapes % 2 == 0:
            note_data += text[prev : match.start(1)]
            prev = match.end(1)
            if bool(match.group(5)) and buttons:
                buttons[-1].append(
                    Button.url(match.group(2), match.group(4).replace(" ", ""))
                )
            else:
                buttons.append(
                    [Button.url(match.group(2), match.group(4).replace(" ", ""))]
                )

        # if odd, escaped -> move along
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]
    if str(buttons) == "[]":
        buttons = None
    try:
        return note_data, buttons
    except:
        return note_data


BUTTONS = {}


def get_reply_msg_btns_text(message):
    text = ""
    for column in message.reply_markup.rows:
        btn_num = 0
        for btn in column.buttons:
            btn_num += 1
            btn.text
            if btn.url:
                btn.url
                text += f"\n[{btn.text}](btnurl:{btn.url}*!repl!*)"
                if btn_num > 1:
                    text = text.replace("*!repl!*", ":same")
                else:
                    text = text.replace("*!repl!*", "")
    return text


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )


def resize_image(image):
    im = Image.open(image)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(maxsize)
    os.remove(image)
    im.save("sticker.webp")


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


async def format_fill(event, text, tm):
    if not event.sender:
        return text
    first_name = last_name = ""
    if event.sender.first_name:
        first_name = ((event.sender.first_name).replace("<", "&lt;")).replace(
            ">", "&gt;"
        )
    if event.sender.last_name:
        last_name = ((event.sender.last_name).replace("<", "&lt;")).replace(">", "&gt;")
    if last_name:
        full_name = first_name + last_name
    else:
        full_name = first_name
    user_id = event.sender_id
    title = event.chat.title
    chat_id = event.chat_id
    chat_username = event.chat.username
    username = event.sender.username
    mention = f'<a href="tg://user?id={user_id}">{full_name}</a>'
    tt = get_readable_time(time.time() - tm)
    try:
        text = text.format(
            first=first_name,
            last=last_name,
            fullname=full_name,
            id=user_id,
            chattitle=title,
            chat_id=chat_id,
            chat_username=chat_username,
            username=username,
            mention=mention,
            time=tt,
        )
    except KeyError:
        return text
    return text


# -----CAPTCHA-----
number_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
alphabet_uppercase = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]


def gen_captcha_text(max_limit=4):
    captcha_string_list = []
    base_char = alphabet_uppercase + number_list
    for i in range(max_limit):
        char = choice(base_char)
        captcha_string_list.append(char)
    captcha_string = ""
    for item in captcha_string_list:
        captcha_string += str(item)
    return captcha_string


def gen_captcha(mode="text"):
    generator = CaptchaGenerator(13)
    if mode == "text":
        captcha_total = generator.gen_captcha_image(2, "hex", choice([True, False]))
        captcha = captcha_total["image"]
        captcha.save("captcha.png")
        return "captcha.png", captcha_total["characters"]
    elif mode == "math":
        captcha_total = generator.gen_math_captcha_image(2, False, True, False)
        (captcha_total["image"]).save("captcha.png")
        return "captcha.png", captcha_total["equation_result"]


def generate_captcha():
    def gen_letter():
        return chr(randint(65, 90))

    def rndColor():
        return (randint(64, 255), randint(64, 255), randint(64, 255))

    def rndColor2():
        return (randint(32, 127), randint(32, 127), randint(32, 127))

    def gen_wrong_answer():
        word = ""
        for _ in range(4):
            word += gen_letter()
        return word

    wrong_answers = []
    for _ in range(8):
        wrong_answers.append(gen_wrong_answer())

    width = 80 * 4
    height = 100
    correct_answer = ""
    font = ImageFont.truetype("./Zaid/Plugins/extra/DroidSans.ttf", 55)
    file = f"{randint(1000, 9999)}.jpg"
    image = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rndColor())

    for t in range(4):
        letter = gen_letter()
        correct_answer += letter
        draw.text((60 * t + 50, 15), letter, font=font, fill=rndColor2())
    image = image.filter(ImageFilter.BLUR)
    image.save(file, "jpeg")
    return [file, correct_answer, wrong_answers]


def human_format(num, precision=2, suffixes=["", "K", "M", "G", "T", "P"]):
    m = sum([abs(num / 1000.0**x) >= 1 for x in range(1, len(suffixes))])
    return f"{num/1000.0**m:.{precision}f}{suffixes[m]}"


async def inline_query(bot, query):
    return custom.InlineResults(
        ubot,
        await ubot(
            GetInlineBotResultsRequest(
                bot=bot,
                peer="me",
                query=query,
                offset="",
                geo_point=types.InputGeoPointEmpty(),
            )
        ),
    )


def translater(text, lang_de="auto", lang_to="en", p=False):
    url = "https://translate.google.cn/_/TranslateWebserverUi/data/batchexecute"
    TTS = "MkEWBc"
    parameter = [[text, lang_de, lang_to, True], [1]]
    e_p = json.dumps(parameter, separators=(",", ":"))
    rpc = [[[TTS, e_p, None, "generic"]]]
    espaced_rpc = json.dumps(rpc, separators=(",", ":"))
    freq = "f.req={}&".format(quote(espaced_rpc))
    headers = {
        "Referer": "http://translate.google.cn",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/47.0.2526.106 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    r = Request(
        method="POST",
        url=url,
        data=freq,
        headers=headers,
    )
    with Session() as s:
        r = s.send(request=r.prepare(), verify=True, timeout=30)
    for line in r.iter_lines(chunk_size=1024):
        decoded_line = line.decode()
        if "MkEWBc" in decoded_line:
            json_line = list(json.loads(decoded_line))
            json_ltd = list(json.loads(json_line[0][2]))
            js = json_ltd[1][0]
            if len(js) == 1:
                if len(js[0]) > 5:
                    js = js[0][5]
                else:
                    if not p:
                        return js[0][0]
                    else:
                        return [js[0][0], None, None]
                translate_tt = ""
                for x in js:
                    x = x[0]
                    translate_tt += x.strip() + " "
                if not p:
                    return translate_tt
                else:
                    p_src = json_ltd[0][0]
                    p_tgt = json_ltd[1][0][0][1]
                    return [translate_tt, p_src, p_tgt]
            elif len(js) == 2:
                sentences = []
                for i in js:
                    sentences.append(i[0])
                if not p:
                    return sentences
                else:
                    p_src = json_ltd[0][0]
                    p_tgt = json_ltd[1][0][0][1]
                    return [sentences, p_src, p_tgt]


def dt_delta(dt):
    return int(dt / (60 * 60)), int((dt / (60 * 60) - int(dt / (60 * 60))) * 60)
