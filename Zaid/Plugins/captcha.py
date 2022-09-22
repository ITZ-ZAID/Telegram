from random import randint, shuffle

from telethon import Button

import Zaid.Plugins.sql.captcha_sql as sql
from Zaid.utils import Zbot, Zinline

from . import can_change_info, db, extract_time, g_time, gen_captcha, generate_captcha

check = db.bot_check

# CONSTANTS
onn = """
Users will be asked to complete a CAPTCHA before being allowed to speak in the chat.

To change this setting, try this command again followed by one of yes/no/on/off
"""
offf = """
Users will NOT be muted when joining the chat.

To change this setting, try this command again followed by one of yes/no/on/off
"""
ca_on = """
I am currently kicking users that haven't completed the CAPTCHA after {}.

To change this setting, try this command again followed by one of yes/no/on/off
"""
ca_off = """
Users that don't complete their CAPTCHA are allowed to stay in the chat, muted, and can complete the CAPTCHA whenever.

To change this setting, try this command again followed by one of yes/no/on/off
"""
smdd = """
Users will stay muted until they use the CAPTCHA.

To change the CAPTCHA mute time, try this command again with a time value.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.
"""
sudd = """
If users haven't unmuted themselves after {}, they will be unmuted automatically.

To change the CAPTCHA mute time, try this command again with a time value.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.
"""
ca_ot = """
Users that don't complete their CAPTCHA are allowed to stay in the chat, muted, and can complete the CAPTCHA whenever.

To change the CAPTCHA kick time, try this command again with a time value.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.
"""
ca_time = """
I am currently kicking users that haven't completed the CAPTCHA after {}.

To change the CAPTCHA kick time, try this command again with a time value.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.
"""
caut = """
That isn't a valid time - '{}' does not follow the expected time patterns.
Example time values: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.
"""
bu_h = """
The current CAPTCHA mode is: button
Button CAPTCHAs simply require a user to press a button in their welcome message to confirm they're human.

Available CAPTCHA modes are: button/math/text
"""
tx_h = """
The current CAPTCHA mode is: text
Text CAPTCHAs require the user to answer a CAPTCHA containing letters and numbers.

Available CAPTCHA modes are: button/math/text
"""
mt_h = """
The current CAPTCHA mode is: math
Math CAPTCHAs require the user to solve a basic maths question. Please note that this may discriminate against users with little maths knowledge.

Available CAPTCHA modes are: button/math/text
"""

pos = ["on", "y", "yes"]
neg = ["off", "n", "no"]


@Zbot(pattern="^/captcha ?(.*)")
async def _(event):
    if (
        event.text.startswith("!captchakick")
        or event.text.startswith("/captchakick")
        or event.text.startswith("?captchakick")
        or event.text.startswith("!captchakicktime")
        or event.text.startswith("/captchakicktime")
        or event.text.startswith("?captchakicktime")
        or event.text.startswith("!captchatime")
        or event.text.startswith("?captchatime")
        or event.text.startswith("/captchatime")
        or event.text.startswith("/captchamode")
        or event.text.startswith("?captchamode")
        or event.text.startswith("!captchamode")
        or event.text == "!captchamode"
        or event.text == "?captchamode"
        or event.text == "/captchamode"
    ):
        return
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    settings = sql.get_mode(event.chat_id)
    args = event.pattern_match.group(1)
    if not args:
        if settings == True:
            await event.reply(onn)
        elif settings == False:
            await event.reply(offf)
    elif args in pos:
        await event.reply(
            "CAPTCHAs have been enabled. I will now mute people when they join."
        )
        sql.set_mode(event.chat_id, True)
    elif args in neg:
        await event.reply("CAPTCHAs have been disabled. Users can join normally.")
        sql.set_mode(event.chat_id, False)
    else:
        await event.reply(
            "That isn't a boolean - expected one of y/yes/on or n/no/off; got: {}".format(
                args
            )
        )


@Zbot(pattern="^/captchakick ?(.*)")
async def _(event):
    if (
        event.text.startswith("!captchakicktime")
        or event.text.startswith("?captchakicktime")
        or event.text.startswith("/captchakicktime")
    ):
        return
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    settings = sql.get_time(event.chat_id)
    if not args:
        if settings == False or settings == 0:
            await event.reply(ca_off)
        else:
            synctime = g_time(settings)
            await event.reply(ca_on.format(synctime))
    elif args in pos:
        if settings:
            synctime = g_time(settings)
        else:
            synctime = "5 Minutes"
            settings = 300
        await event.reply(
            f"I will now kick people that haven't solved the CAPTCHA after {synctime}."
        )
        sql.set_time(event.chat_id, settings)
    elif args in neg:
        await event.reply(
            "I will no longer kick people that haven't solved the CAPTCHA."
        )
        sql.set_time(event.chat_id, 0)
    else:
        await event.reply(
            "That isn't a boolean - expected one of y/yes/on or n/no/off; got: {args}"
        )


@Zbot(pattern="^/captchakicktime ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    settings = sql.get_time(event.chat_id)
    if not args:
        if settings == False or settings == 0:
            await event.reply(ca_ot)
        else:
            synctime = g_time(settings)
            await event.reply(ca_time.format(synctime))
    elif args:
        if len(args) == 1:
            return await event.reply(caut.format(args))
        time = await extract_time(event, args)
        if not time:
            return
        if time < 300 or time > 86400:
            return await event.reply(
                "The welcome kick time can only be between 5 minutes, and 1 day. Please choose another time."
            )
        await event.reply(f"Welcome kick time has been set to {args}.")
        sql.set_time(event.chat_id, time)


@Zbot(pattern="^/captchatime ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    settings = sql.get_unmute_time(event.chat_id)
    if not args:
        if settings == 0 or settings == False:
            await event.reply(smdd)
        else:
            value = g_time(settings)
            await event.reply(sudd.format(value))
    elif args:
        if len(args) == 1:
            return await event.reply(caut.format(args))
        time = await extract_time(event, args)
        if not time:
            return
        await event.reply(
            f"I will now mute people for {g_time(time)} when they join - or until they solve the CAPTCHA in the welcome message."
        )
        sql.set_unmute_time(event.chat_id, time)


@Zbot(pattern="^/captchamode ?(.*)")
async def _(event):
    if event.is_private:
        return  # connect
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    settings = sql.get_style(event.chat_id)
    if not args:
        if settings == False or settings == "button":
            await event.reply(bu_h)
        elif settings == "text":
            await event.reply(tx_h)
        elif settings == "math":
            await event.reply(mt_h)
    else:
        if not args in ["button", "math", "text"]:
            await event.reply(
                f"'{args}' is not a recognised CAPTCHA mode! Try one of: button/math/text"
            )
        else:
            text = f"CAPTCHA set to **{args}**\n"
            if args == "button":
                text += "\nButton CAPTCHAs simply require a user to press a button in their welcome message to confirm they're human."
            elif args == "math":
                text += "\nMath CAPTCHAs require the user to solve a basic maths question. Please note that this may discriminate against users with little maths knowledge."
            elif args == "text":
                text += "\nText CAPTCHAs require the user to answer a CAPTCHA containing letters and numbers."
            await event.reply(text)
            sql.set_style(event.chat_id, args)


async def captcha_to_welcome(event, welcome_text, file, buttons, chat_id):
    style = sql.get_style(chat_id)
    if buttons == None:
        buttons = []
    try:
        await tbot.edit_permissions(chat_id, event.user_id, send_messages=False)
    except:
        pass
    if style == "button":
        buttons.append(
            [
                Button.inline(
                    "Click to prove human",
                    data="humanv_{}".format(event.user_id),
                )
            ]
        )
    await event.client.send_message(
        chat_id, welcome_text, file=file, buttons=buttons, parse_mode="html"
    )


@Zinline(pattern=r"humanv(\_(.*))")
async def dcfd_fed(event):
    user_id = int(((event.pattern_match.group(1)).decode()).split("_", 1)[1])
    if not event.sender_id == user_id:
        return await event.answer(
            "You are the not the user to be verified.", alert=True
        )
    try:
        await event.client.edit_permissions(event.chat_id, event.sender_id, send_messages=True)
    except:
        pass
    await event.answer("Verified.")


@Zbot(pattern="^/start captcha_(.*)")
async def kek(event):
    chat_id = int(event.pattern_match.group(1))
    if check.find_one({"chat_id": chat_id, "user_id": event.sender_id}):
        if (check.find_one({"chat_id": chat_id, "user_id": event.sender_id}))[
            "passed"
        ] == True:
            return await event.reply("You have already completed the captcha!")
    style = sql.get_style(chat_id)
    if style == "math":
        await math_captcha(event, chat_id)
    elif style == "text":
        await text_captcha(event, chat_id)


async def text_captcha(event, chat_id):
    captcha_pic, sol, wrong = generate_captcha()
    ans = []
    ans.append(sol)
    for x in wrong:
        ans.append(x)
    shuffle(ans)
    btns = []
    bt = []
    for x in ans:
        cb_data = str(chat_id) + "|" + str(x) + "|" + str(sol)
        bt.append(Button.inline(x, data=f"txtc_{cb_data}"))
        if len(bt) == 3:
            btns.append(bt)
            bt = []
    check.update_one(
        {"chat_id": chat_id, "user_id": event.sender_id},
        {"$set": {"chance": 3, "passed": False}},
        upsert=True,
    )
    await event.respond(
        f"Choose the correct text from the image to get verified, you have 3 chances left!",
        file=captcha_pic,
        buttons=btns,
    )
    os.remove(captcha_pic)


@Zinline(pattern=r"txtc(\_(.*))")
async def txtc(event):
    cb_data = (((event.pattern_match.group(1)).decode()).split("_", 1)[1]).split("|")
    chat_id = int(cb_data[0])
    option = cb_data[1]
    ans = cb_data[2]
    if option != ans:
        captcha_pic, character, wrong = generate_captcha()
        ans = []
        ans.append(character)
        for x in wrong:
            ans.append(x)
        shuffle(ans)
        btns = []
        bt = []
        for x in ans:
            cb_data = str(chat_id) + "|" + str(x) + "|" + str(character)
            bt.append(Button.inline(x, data=f"txtc_{cb_data}"))
            if len(bt) == 3:
                btns.append(bt)
                bt = []
        chance = check.find_one({"chat_id": chat_id, "user_id": event.sender_id})
        if not chance:
            chance = 3
        else:
            chance = int(chance["chance"]) - 1
        if chance == 0:
            check.update_one(
                {"chat_id": chat_id, "user_id": event.sender_id},
                {"$set": {"chance": 3}},
                upsert=True,
            )
            return await event.edit(
                "Verification failed, You have ran out of chances", buttons=None
            )
        check.update_one(
            {"chat_id": chat_id, "user_id": event.sender_id},
            {"$set": {"chance": chance, "passed": False}},
            upsert=True,
        )
        await event.edit(
            f"Choose the correct text from the image to get verified, you have {chance} chances left!",
            file=captcha_pic,
            buttons=btns,
        )
        os.remove(captcha_pic)
    else:
        channel_id = int((str(chat_id)).replace("-100", ""))
        await event.edit(
            "You have been verified sucessfully✅!",
            buttons=Button.url("Return to chat.", "t.me/c/{}/1".format(channel_id)),
        )
        check.update_one(
            {"chat_id": chat_id, "user_id": event.sender_id},
            {"$set": {"chance": 3, "passed": True}},
            upsert=True,
        )
        try:
            await event.client.edit_permissions(chat_id, event.sender_id, send_messages=True)
        except:
            pass


async def math_captcha(event, chat_id):
    captcha_pic, solution = gen_captcha("math")
    ans = []
    ans.append(solution)
    for x in range(8):
        ans.append(randint(0, 999))
    shuffle(ans)
    btns = []
    bt = []
    for x in ans:
        cb_data = str(chat_id) + "|" + str(x) + "|" + str(solution)
        bt.append(Button.inline(str(x), data=f"mathc_{cb_data}"))
        if len(bt) == 3:
            btns.append(bt)
            bt = []
    check.update_one(
        {"chat_id": chat_id, "user_id": event.sender_id},
        {"$set": {"chance": 3, "passed": False}},
        upsert=True,
    )
    await event.respond(
        f"Choose the correct answer to get verified, you have 3 chances left!",
        file=captcha_pic,
        buttons=btns,
    )


@Zinline(pattern=r"mathc(\_(.*))")
async def txtc(event):
    cb_data = (((event.pattern_match.group(1)).decode()).split("_", 1)[1]).split("|")
    chat_id = int(cb_data[0])
    option = cb_data[1]
    ans = cb_data[2]
    if option != ans:
        captcha_pic, solution = gen_captcha("math")
        ans = []
        ans.append(solution)
        for x in range(8):
            ans.append(randint(0, 999))
        shuffle(ans)
        btns = []
        bt = []
        for x in ans:
            cb_data = str(chat_id) + "|" + str(x) + "|" + str(character)
            bt.append(Button.inline(str(x), data=f"txtc_{cb_data}"))
            if len(bt) == 3:
                btns.append(bt)
                bt = []
        chance = check.find_one({"chat_id": chat_id, "user_id": event.sender_id})
        if not chance:
            chance = 3
        else:
            chance = int(chance["chance"]) - 1
        if chance == 0:
            check.update_one(
                {"chat_id": chat_id, "user_id": event.sender_id},
                {"$set": {"chance": 3}},
                upsert=True,
            )
            return await event.edit(
                "Verification failed, You have ran out of chances", buttons=None
            )
        check.update_one(
            {"chat_id": chat_id, "user_id": event.sender_id},
            {"$set": {"chance": chance, "passed": False}},
            upsert=True,
        )
        await event.edit(
            f"Choose the correct answer to get verified, you have {chance} chances left!",
            file=captcha_pic,
            buttons=btns,
        )
    else:
        channel_id = int((str(chat_id)).replace("-100", ""))
        await event.edit(
            "You have been verified sucessfully✅!",
            buttons=Button.url("Return to chat.", "t.me/c/{}/1".format(channel_id)),
        )
        check.update_one(
            {"chat_id": chat_id, "user_id": event.sender_id},
            {"$set": {"chance": 3, "passed": True}},
            upsert=True,
        )
        try:
            await event.client.edit_permissions(chat_id, event.sender_id, send_messages=True)
        except:
            pass
