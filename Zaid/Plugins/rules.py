from telethon import Button

import Zaid.Plugins.mongodb.rules_db as db
from Zaid.utils import Zbot, Zinline
from .language import translate

from . import button_parser, can_change_info, cb_can_change_info

anon_db = {}


@Zbot(pattern="^/privaterules ?(.*)")
async def pr(event):
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not event.from_id:
        return await a_rules(event, "privaterules")
    if event.is_group:
        if not await can_change_info(event, event.sender_id):
            return
    args = event.pattern_match.group(1)
    rules = db.get_rules(event.chat_id)
    if not rules:
        return await event.reply(translate(
            "You haven't set any rules yet; how about you do that first?", event.chat_id)
        )
    if not args:
        mode = db.get_private_rules(event.chat_id)
        if mode:
            await event.reply(translate("Use of /rules will send the rules to the user's PM.", event.chat_id))
        else:
            await event.reply(translate(
                f"All /rules commands will send the rules to {event.chat.title}.", event.chat_id)
            )
    elif args in ["on", "yes", "y"]:
        await event.reply(translate("Use of /rules will send the rules to the user's PM.", event.chat_id))
        db.set_private_rules(event.chat_id, True)
    elif args in ["off", "no", "n"]:
        await event.reply(translate(
            f"All /rules commands will send the rules to {event.chat.title}.", event.chat_id)
        )
        db.set_private_rules(event.chat_id, False)
    else:
        await event.reply(translate("I only understand the following: yes/no/on/off", event.chat_id))


@Zbot(pattern="^/setrules ?(.*)")
async def set_r(event):
    if (
        event.text.startswith("+setrulesbutton")
        or event.text.startswith("?setrulesbutton")
        or event.text.startswith("!setrulesbutton")
        or event.text.startswith("/setrulesbutton")
    ):
        return
    if event.is_private:
        return await event.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not event.from_id:
        return await a_rules(event, "setrules")
    if event.is_group and event.from_id:
        if not await can_change_info(event, event.sender_id):
            return
    if not event.reply_to and not event.pattern_match.group(1):
        return await event.reply(translate("You need to give me rules to set!", event.chat_id))
    elif event.reply_to:
        r_text = ""
        r_msg = await event.get_reply_message()
        if r_msg.text:
            r_text = r_msg.text
        if r_msg.reply_markup:
            buttons = get_reply_msg_btns_text(r_msg)
            r_text = r_text + str(buttons)
        if r_msg.media and not r_msg.text:
            return await event.reply(translate("You need to give me rules to set!", event.chat_id))
    elif event.pattern_match.group(1):
        r_text = event.text.split(None, 1)[1]
    await event.reply(translate(f"New rules for {event.chat.title} set successfully!", event.chat_id))
    db.set_rules(event.chat_id, r_text)


@Zbot(pattern="^/resetrules")
async def reset_rules(e):
    event = e
    if (
        e.text.startswith("+resetrulesbutton")
        or e.text.startswith("/resetrulesbutton")
        or e.text.startswith("?resetrulesbutton")
        or e.text.startswith("!resetrulesbutton")
    ):
        return
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await a_rules(e, "resetrules")
    if e.is_group:
        if not await can_change_info(e, e.sender_id):
            return
    await e.reply(translate(f"Rules for {e.chat.title} were successfully cleared!", event.chat_id))
    db.del_rules(e.chat_id)


r_btn = """
The rules button will be called: and
`{}`

To change the button name, try this command again followed by the new name
"""


@Zbot(pattern="^/setrulesbutton ?(.*)")
async def set_rules_button(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await a_rules(e, "setrulesbutton")
    rg = e.pattern_match.group(1)
    if not rg:
        x = db.get_rules_button(e.chat_id)
        await e.reply(r_btn.format(x))
    elif len(rg) > 100:
        r_over = translate("Your new rules button name is too long; please make it shorter (under 100 characters).", event.chat_id)
        await e.reply(r_over)
    elif rg:
        r_g = e.text.split(None, 1)[1]
        db.set_rules_button(e.chat_id, r_g)
        await e.reply(translate("Updated the rules button name!", event.chat_id))


@Zbot(pattern="^/resetrulesbutton")
async def p(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    if not e.from_id:
        return await a_rules(e, "resetrulesbutton")
    if e.is_group:
        if not await can_change_info(e, e.sender_id):
            return
    await e.reply(translate("Reset the rules button name to default", event.chat_id))
    db.set_rules_button(e.chat_id, "Rules")


@Zbot(pattern="^/(rules|rule|Rules)")
async def rules(e):
    event = e
    if e.is_private:
        return await e.reply(translate(
            "This command is made to be used in group chats, not in pm!", event.chat_id)
        )
    rules = db.get_rules(e.chat_id)
    pr = db.get_private_rules(e.chat_id)
    if not rules:
        return await e.reply(translate(
            "The group admins haven't set any rules for this chat yet. This probably doesn't mean it's lawless though...!", event.chat_id)
        )
    elif pr:
        button_name = db.get_rules_button(e.chat_id)
        str(e.chat_id)
        x = Button.url(
            button_name, "t.me/Zaid2_Robot?start=_rules_{}".format(e.chat_id)
        )
        await e.reply(translate("Click on the button to see the chat rules!", event.chat_id), buttons=x)
    elif not pr:
        x_rules, buttons = button_parser(rules)
        await e.reply(translate(f"The Rules for {e.chat.title} are:\n", event.chat_id) + x_rules, buttons=buttons)


@Zbot(pattern="^/start _rules(.*)")
async def private_r_trigger(e):
    event = e
    if not e.is_private:
        return
    chat_id = int((e.pattern_match.group(1)).split("_", 1)[1])
    rules = (
        db.get_rules(chat_id)
        or translate("The group admins haven't set any rules for this chat yet. This probably doesn't mean it's lawless though...!", event.chat_id)
    )
    await e.reply(translate("Rules are:\n", event.chat_id) + rules)


async def a_rules(event, mode):
    global anon_db
    if event.reply_to:
        anon_db[event.id] = (await event.get_reply_message()).text or "None"
    else:
        try:
            anon_db[event.id] = event.text.split(None, 1)[1]
        except IndexError:
            anon_db[event.id] = "None"
    cb_data = str(event.id) + "|" + str(mode)
    a_buttons = Button.inline(translate("Click to prove admin", event.chat_id), data="ranon_{}".format(cb_data))
    await event.reply(translate(
        "It looks like you're anonymous. Tap this button to confirm your identity.", event.chat_id),
        buttons=a_buttons,
    )


@Zinline(pattern=r"ranon(\_(.*))")
async def rules_anon(e):
    d_ata = ((e.pattern_match.group(1)).decode()).split("_", 1)[1]
    da_ta = d_ata.split("|", 1)
    event_id = int(da_ta[0])
    event = e
    mode = da_ta[1]
    if not await cb_can_change_info(e, e.sender_id):
        return
    try:
        cb_data = anon_db[event_id]
    except KeyError:
        return await e.edit(translate("This requests has been expired.", event.chat_id))
    if mode == "setrules":
        if cb_data == "None":
            await e.edit("You need to give me rules to set!")
        else:
            await e.edit(translate(f"New rules for {e.chat.title} set successfully!", event.chat_id))
            db.set_rules(e.chat_id, cb_data)
    elif mode == "privaterules":
        rules = db.get_rules(e.chat_id)
        if not rules and cb_data != "None":
            return await e.edit(translate(
                "You haven't set any rules yet; how about you do that first?", event.chat_id)
            )
        elif cb_data == "None":
            mode = db.get_private_rules(e.chat_id)
            if mode:
                await e.edit(translate("Use of /rules will send the rules to the user's PM.", event.chat_id))
            else:
                await e.edit(translate(
                    f"All /rules commands will send the rules to {e.chat.title}.", event.chat_id)
                )
        elif cb_data in ["on", "yes"]:
            await e.edit(translate("Use of /rules will send the rules to the user's PM.", event.chat_id))
            db.set_private_rules(e.chat_id, True)
        elif cb_data in ["off", "no"]:
            await e.edit(translate(f"All /rules commands will send the rules to {e.chat.title}.", event.chat_id))
            db.set_private_rules(e.chat_id, False)
        else:
            await e.edit(translate("I only understand the following: yes/no/on/off", event.chat_id))
    elif mode == "resetrules":
        await e.reply(translate(f"Rules for {event.chat.title} were successfully cleared!", event.chat_id))
        db.del_rules(event.chat_id)
    elif mode == "setrulesbutton":
        if not cb_data:
            x = db.get_rules_button(e.chat_id)
            await e.edit(r_btn.format(x))
        elif len(rg) > 100:
            r_over = translate("Your new rules button name is too long; please make it shorter (under 100 characters).", event.chat_id)
            await e.edit(r_over)
        elif rg:
            r_g = e.text.split(None, 1)[1]
            db.set_rules_button(e.chat_id, r_g)
            await e.edit(translate("Updated the rules button name!", event.chat_id))
    elif mode == "resetrulesbutton":
        await e.edit(translate("Reset the rules button name to default", event.chat_id))
        db.set_rules_button(e.chat_id, "Rules")
