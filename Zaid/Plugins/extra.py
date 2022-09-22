import re
from os import remove
from random import randint

import bs4
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from geopy.geocoders import Nominatim
from requests import get, post, request
from telethon.tl.types import InputGeoPoint, InputMediaDice, InputMediaGeoPoint

from Zaid import Zaid
from Zaid.Plugins.mongodb.nightmode_db import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)
from Zaid.utils import Zbot

from . import can_change_info

enable = ["enable", "on", "y", "yes"]
disable = ["disable", "off", "n" "no"]


@Zbot(pattern="^/nightmode ?(.*)")
async def lilz(event):
    if event.is_private:
        return
    if not await can_change_info(event, event.sender_id):
        return
    args = event.pattern_match.group(1)
    if not args:
        if is_nightmode_indb(event.chat_id):
            await event.reply("**NightMode** is currently **enabled** for this chat.")
        else:
            await event.reply("**NightMode** is currently **disabled** for this chat.")
    elif args in enable:
        await event.reply(
            "Enabled nightmode for this.\n\nGroup closes at 12Am and opens at 6Am IST"
        )
        add_nightmode(event.chat_id)
    elif args in disable:
        await event.reply("Disabled nightmode for this chat.")
        rmnightmode(event.chat_id)


async def job_close():
    nt_chats = get_all_chat_id()
    if len(nt_chats) == 0:
        return
    for chats in nt_chats:
        try:
            await Zaid.send_message(
                int(chats.chat_id),
                "12:00 Am, Group Is Closing Till 6 Am. Night Mode Started ! \n**Powered By neko**",
            )
            await Zaid.edit_permissions(int(chats.chat_id), send_messages=False)
        except Exception as e:
            logger.info(f"Unable To Close Group {chats.chat_id} - {e}")


scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=58)
scheduler.start()


async def job_open():
    nt_chats = get_all_chat_id()
    if len(nt_chats) == 0:
        return
    for chats in nt_chats:
        try:
            await Zaid.send_message(
                int(chats.chat_id),
                "06:00 Am, Group Is Opening.\n**Powered By neko**",
            )
            await Zaid.edit_permissions(int(chats.chat_id), send_messages=True)
        except Exception as e:
            logger.info(f"Unable To Open Group {chats.chat_id} - {e}")


scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=1)
scheduler.start()


@Zbot(pattern="^/(GitHub|github) ?(.*)")
async def gt(event):
    arg = event.pattern_match.group(2)
    git = get(f"https://api.github.com/users/{arg}").json()
    try:
        fileid = git["avatar_url"]
    except KeyError:
        fileid = None
    try:
        if git["type"] == "User":
            text = "<b>User Info:</b>"
        else:
            text = "<b>Organization Info:</b>"
    except KeyError:
        pass
    try:
        name = git["name"]
        text += f"\n<b>Name:</b> {name}"
    except KeyError:
        pass
    try:
        id = git["id"]
        text += f"\n<b>ID:</b> <code>{id}</code>"
    except KeyError:
        pass
    try:
        nid = git["node_id"]
        text += f"\n<b>Node ID:</b> {nid}"
    except KeyError:
        pass
    try:
        company = git["company"]
        if not company == None:
            text += f"\n<b>Company:</b> {company}"
    except KeyError:
        pass
    try:
        followers = git["followers"]
        if not followers == None:
            text += f"\n<b>Followers:</b> {followers}"
    except KeyError:
        pass
    try:
        blog = git["blog"]
        if not blog == None:
            text += f"\n<b>Blog:</b> <code>{blog}</code>"
    except KeyError:
        pass
    try:
        location = git["location"]
        if not location == None:
            text += f"\n<b>Location:</b> {location}"
    except KeyError:
        pass
    try:
        bio = git["bio"]
        if not bio == None:
            text += f"\n\n<b>Bio:</b> <code>{bio}</code>"
    except KeyError:
        pass
    try:
        twitter = git["twitter_username"]
        if not twitter == None:
            text += f"\n\n<b>Twitter:</b> {twitter}"
    except KeyError:
        pass
    try:
        email = git["email"]
        if not email == None:
            text += f"\n<b>Email:</b> <code>{email}</code>"
    except KeyError:
        pass
    try:
        repo = git["public_repos"]
        text += f"\n<b>Repos:</b> {repo}"
    except KeyError:
        pass
    try:
        url = git["html_url"]
        text += f"\n\n<b>URL:</b> <code>{url}</code>"
    except KeyError:
        pass
    await event.respond(text, parse_mode="html", file=fileid)


@Zbot(pattern="^/math ?(.*)")
async def ss(event):
    input_str = event.pattern_match.group(1)
    if not input_str:
        return await event.reply("Please provide the Mathamatical Equation.")
    url = "https://evaluate-expression.p.rapidapi.com/"
    querystring = {"expression": input_str}
    headers = {
        "x-rapidapi-key": "fef481fee3mshf99983bfc650decp104100jsnbad6ddb2c846",
        "x-rapidapi-host": "evaluate-expression.p.rapidapi.com",
    }
    response = request("GET", url, headers=headers, params=querystring)
    if not response or not response.text:
        return await event.reply("Invalid Mathamatical Equation provided.")
    await event.reply(response.text)


@Zbot(pattern="^/gps ?(.*)")
async def gps(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.reply("Enter some location to get its position!")
    try:
        geolocator = Nominatim(user_agent="SkittBot")
        location = args
        geoloc = geolocator.geocode(location)
        longitude = geoloc.longitude
        latitude = geoloc.latitude
        gm = "https://www.google.com/maps/search/{},{}".format(latitude, longitude)
        await event.respond(
            "Open with: [Google Maps]({})".format(gm),
            file=InputMediaGeoPoint(InputGeoPoint(float(latitude), float(longitude))),
            link_preview=False,
        )
    except Exception as e:
        await event.reply("Unable to locate that place. " + str(e))


"""
@tbot.on.utils.InlineQuery)
async def handler(event):
                        builder = event.builder
                        rev_text = event.text[::-1]
                        await event.answer([
                            builder.article('Reverse text', text=rev_text)], switch_pm="hi babe", switch_pm_param="help")
"""


@Zbot(pattern="^/pypi ?(.*)")
async def pi(event):
    args = event.pattern_match.group(1)
    if not args:
        return await event.reply(
            "Please input the name of a pypi library to gather it's info."
        )
    url = f"https://pypi.org/pypi/{args}/json"
    response = get(url)
    if not response:
        return await event.reply("Invalid pypi package provided!")
    result = response.json()
    name = (result["info"]["name"]).capitalize()
    author = result["info"]["author"]
    version = result["info"]["version"]
    summary = result["info"]["summary"]
    release_url = result["info"]["release_url"]
    requires_dist = result["info"]["requires_dist"]
    py = f"<b><h1>{name}</h1></b>"
    py += f"\n\n<b>Author:</b> {author}"
    py += f"\n<b>Latest Version:</b> <code>{version}</code>"
    if summary:
        py += f"\n\n<b>Summary:</b> <i>{summary}</i>"
    if release_url:
        py += f"\n\n<b>URL:</b> <code>{release_url}</code>"
    if requires_dist:
        py += f"\n<b>Dependencies:</b>\n{requires_dist}"
    await event.respond(py, parse_mode="htm")


@Zbot(pattern="^/(jackpot|dice|dart|goal|football|basketball|bowling)$")
async def dart(event):
    args = event.pattern_match.group(1)
    if not args:
        return
    if args == "jackpot":
        await event.respond(file=InputMediaDice("🎰"))
    elif args == "dice":
        await event.respond(file=InputMediaDice("🎲"))
    elif args == "dart":
        await event.respond(file=InputMediaDice("🎯"))
    elif args in ["goal", "football"]:
        await event.respond(file=InputMediaDice("⚽"))
    elif args == "basketball":
        await event.respond(file=InputMediaDice("🏀"))
    elif args == "bowling":
        await event.respond(file=InputMediaDice("🎳"))



@Zbot(pattern="^/stt$")
async def b(event):
    if event.reply_to_msg_id:
        reply_msg = await event.get_reply_message()
        if not reply_msg.media:
            return await event.reply(
                "Reply to a voice message, to get the text out of it."
            )
    else:
        return await event.reply("Reply to a voice message, to get the text out of it.")
    audio = await tbot.download_media(reply_msg, "./")
    kek = await event.reply("Starting Analysis...")
    headers = {
        "Content-Type": reply_msg.media.document.mime_type,
    }
    data = open(audio, "rb").read()
    response = post(
        "https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/d5d8fabf-bbc8-4c2d-8575-36638227a70e"
        + "/v1/recognize",
        headers=headers,
        data=data,
        auth=("apikey", "04WmiAo7b-cDJvAimSLMlnWGiyl1OPoRCOeE_wiS2WAz"),
    )
    response = response.json()
    if "results" in response:
        results = response["results"]
        transcript_response = ""
        transcript_confidence = ""
        for alternative in results:
            alternatives = alternative["alternatives"][0]
            transcript_response += " " + str(alternatives["transcript"])
            transcript_confidence += " " + str(alternatives["confidence"]) + " + "
        if transcript_response != "":
            string_to_show = "TRANSCRIPT: __{}__\nConfidence: `{}`".format(
                transcript_response, transcript_confidence
            )
        else:
            string_to_show = "TRANSCRIPT: `Nil`\n\n**No Results Found**"
        await kek.edit(string_to_show)
    else:
        await event.reply(response["error"])
    remove(required_file_name)


@Zbot(pattern="^/stickerid ?(.*)")
async def Sid(event):
    if not event.reply_to_msg_id and not event.pattern_match.group(1):
        return await event.reply("Please reply to a sticker message to get its id.")
    elif event.reply_to_msg_id:
        msg = await event.get_reply_message()
        if not msg.sticker:
            return await event.reply(
                "That's not a sticker! Reply to a sticker to obtain it's ID."
            )
        file_id = msg.file.id
        await event.reply(
            f"<b>Sticker ID:</b> <code>{file_id}</code>", parse_mode="html"
        )
    elif event.pattern_match.group(1):
        sticker_id = event.pattern_match.group(1)
        try:
            sticker = await event.reply(file=sticker_id)
        except ValueError:
            await event.reply(
                "Invalid BOT_FILE_ID provided, failed to convert given id to a media."
            )


__help__ = """
*Admin only:*
 ❍ /nightmode <on/off>: Automatically lock your chat after 23:59 Indian Standard time.
 ❍ /stickerid : Reply to get Any Sticker Id.
 ❍ /stt : Reply to a voice message, to get the text out of it.
 ❍ /jackpot|dice|dart|goal|football|basketball|bowling : Fun Commands.
 ❍ /math : Calculate anything.
 ❍ /gps : Get a Location. Ex: /gps New Delhi.
"""

__name__ = "extras"
from .. import CMD_HELP
CMD_HELP.update({__name__: [__name__, __help__]})
