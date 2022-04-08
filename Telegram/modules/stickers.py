import math
import urllib.request as urllib
from html import escape
from io import BytesIO
from urllib.error import HTTPError

from PIL import Image
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode,
                      TelegramError, Update)
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html
from Telegram.modules.helper_funcs.decorators import zaid


@zaid(command='stickerid')
def stickerid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", The sticker id you are replying is :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "Hello "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", Please reply to sticker message to get id sticker",
            parse_mode=ParseMode.HTML,
        )


@zaid(command='getsticker')
def getsticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.effective_message
    chat_id = update.effective_chat.id
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        # Check if it's an animated file
        is_animated = msg.reply_to_message.sticker.is_animated
        # Get the file and put it into a memory buffer
        new_file = bot.get_file(file_id)
        sticker_data = new_file.download(out=BytesIO())
        # go back to the start of the buffer
        sticker_data.seek(0)
        # Reply with the document. Telegram INSISTS on making anything
        # that ends in .tgs become an animated sticker so we'll have to
        # rename it to something the user should know how to handle.
        filename = "sticker.png"
        if is_animated:
            filename = "animated_sticker.tgs.rename_me"
        # Send the document
        bot.send_document(chat_id,
            document=sticker_data,
            filename=filename,
            disable_content_type_detection=True
        )
    else:
        update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG."
        )


@zaid(command=["steal", "kang"])
def kang(update: Update, context: CallbackContext):  # sourcery no-metrics
    global ppref
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    is_animated = False
    is_video = False
    file_id = None
    sticker_emoji = "🤔"
    sticker_data = None

    # The kang syntax is as follows:
    # /kang 🤔 <as reply to document>
    # /kang http://whatever.com/sticker.png 🤔
    # It can be animated or not.

    # first check if we're syntactically correct.
    if not msg.reply_to_message and not args:
        # this is quite a bit more difficult, we need to get all their packs managed by us.
        packs = ""
        # start with finding non-animated packs.
        packnum = 0
        # Initial pack name for non-animated
        packname = f"a{user.id}_by_{context.bot.username}"
        # Max non-animated stickers in a pack
        max_stickers = 120

        # Find the packs
        while True:
            last_set = False
            try:
                stickerset = context.bot.get_sticker_set(packname)
                if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    if is_animated:
                        packname = f"animated{packnum}_{user.id}_by_{context.bot.username}"
                        ppref = "animated"
                    elif is_video:
                        packname = f"vid{packnum}_{user.id}_by_{context.bot.username}"
                        ppref = "vid"
                    else:
                        packname = f"a{packnum}_{user.id}_by_{context.bot.username}"
                        ppref = ""
                else:
                    last_set = True
                packs += f"[{ppref}pack{packnum if packnum != 0 else ''}](t.me/addstickers/{packname})\n"
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    last_set = True
                else:
                    print(e)
                    break  # something went wrong, leave the loop and send what we have.

            # If we're done checking bot animated and non-animated packs
            # exit the loop and send our pack message.
            if last_set and is_animated:
                break
            elif last_set:
                # move to checking animated packs. Start with the first pack
                packname = f"animated_{user.id}_by_{context.bot.username}"
                # reset our counter
                packnum = 0
                # Animated packs have a max of 50 stickers
                max_stickers = 50
                # tell the loop we're looking at animated stickers now
                is_animated = True

        # if they have no packs, change our message
        if not packs:
            packs = "Looks like you don't have any packs! Please reply to a sticker, or image to kang it and create a new pack!"
        else:
            packs = "Please reply to a sticker, or image to kang it!\nOh, by the way, here are your packs:\n" + packs

        # Send our list as a reply
        msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)
        # Don't continue processing the command.
        return

    # User sent /kang in reply to a message
    if rep := msg.reply_to_message:
        if rep.sticker:
            is_animated = rep.sticker.is_animated
            is_video = rep.sticker.is_video
            file_id = rep.sticker.file_id
            # also grab the emoji if the user wishes
            if not args:
                sticker_emoji = rep.sticker.emoji
        elif rep.photo:
            file_id = rep.photo[-1].file_id
        elif rep.video:
            file_id = rep.video.file_id
            is_video = True
        elif rep.animation:
            file_id = rep.animation.file_id
            is_video = True
        elif doc := rep.document:
            file_id = rep.document.file_id
            if doc.mime_type == 'video/webm':
                is_video = True
        else:
            msg.reply_text("Yea, I can't steal that.")
            return

        # Check if they have an emoji specified.
        if args:
            sticker_emoji = args[0]

        # Download the data
        kang_file = context.bot.get_file(file_id)
        sticker_data = kang_file.download(out=BytesIO())
        # move to the front of the buffer.
        sticker_data.seek(0)
    else:  # user sent /kang with url
        url = args[0]
        # set the emoji if they specify it.
        if len(args) >= 2:
            sticker_emoji = args[1]
        # open the URL, downlaod the image and write to
        # a buffer object we can use elsewhere.
        sticker_data = BytesIO()
        try:
            resp = urllib.urlopen(url)

            # check the mime-type first, you can't kang a .html file.
            mime = resp.getheader('Content-Type')
            if mime not in ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'application/x-tgsticker']:
                msg.reply_text("I can only kang images m8.")
                return

            # check if it's an animated sticker type
            if mime == "application/x-tgsticker":
                is_animated = True
            # write our sticker data to a buffer object
            sticker_data.write(resp.read())
            # move to the front of the buffer.
            sticker_data.seek(0)
        except ValueError:
            # If they gave an invalid URL
            msg.reply_text("Yea, that's not a URL I can download from.")
            return
        except HTTPError as e:
            # if we're not allowed there for some reason
            msg.reply_text(f"Error downloading the file: {e.code} {e.msg}")
            return

    packnum = 0
    packname_found = False
    invalid = False

    # now determine the pack name we should use by default
    if is_animated:
        packname = f"animated_{user.id}_by_{context.bot.username}"
        max_stickers = 50
    elif is_video:
        packname = f"vid_{user.id}_by_{context.bot.username}"
        max_stickers = 50
    else:
        packname = f"a{user.id}_by_{context.bot.username}"
        max_stickers = 120

    # Find if the pack is full already
    while not packname_found:
        try:
            stickerset = context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                if is_animated:
                    packname = f"animated{packnum}_{user.id}_by_{context.bot.username}"
                elif is_video:
                    packname = f"vid{packnum}_{user.id}_by_{context.bot.username}"
                else:
                    packname = f"a{packnum}_{user.id}_by_{context.bot.username}"
            else:
                packname_found = True
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = True
                # we will need to create the sticker pack
                invalid = True

    # if the image isn't animated, ensure it's the right size/format with PIL
    if not is_animated and not is_video:
        # handle non-animated stickers.
        try:
            im = Image.open(sticker_data)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if size1 > size2:
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
                maxsize = (512, 512)
                im.thumbnail(maxsize)
            # Saved the resized sticker in memory
            sticker_data = BytesIO()
            im.save(sticker_data, 'PNG')
            # seek to start of the image data
            sticker_data.seek(0)
        except OSError as e:
            msg.reply_text("I can only steal images m8.")
            return

    # actually add the damn sticker to the pack, animated or not.
    try:
        # Add the sticker to the pack if it doesn't exist already
        if invalid:
            # Since Stickerset_invalid will also try to create a pack we might as
            # well just reuse that code and avoid typing it all again.
            raise TelegramError("Stickerset_invalid")
        context.bot.add_sticker_to_set(
            user_id=user.id,
            name=packname,
                tgs_sticker = sticker_data if is_animated else None,
                webm_sticker = sticker_data if is_video else None,
                png_sticker = sticker_data if not is_animated and not is_video else None,
            emojis=sticker_emoji,
        )
        msg.reply_text(
            f"Sticker successfully added to [pack](t.me/addstickers/{packname})"
            + f"\nEmoji is: {sticker_emoji}",
            parse_mode=ParseMode.MARKDOWN,
        )
    except TelegramError as e:
        if e.message == "Stickerset_invalid":
            # if we need to make a sticker pack, make one and make this the
            # first sticker in the pack.
            makepack_internal(
                update,
                context,
                msg,
                user,
                sticker_emoji,
                packname,
                packnum,
                tgs_sticker=sticker_data if is_animated else None,
                webm_sticker=sticker_data if is_video else None,
                png_sticker=sticker_data if not is_animated and not is_video else None,
            )
        elif e.message == "Stickers_too_much":
            msg.reply_text("Max packsize reached. Press F to pay respecc.")
        elif e.message == "Invalid sticker emojis":
            msg.reply_text("I can't kang with that emoji!")
        elif e.message == "Sticker_video_nowebm":
            msg.reply_text(
                "This media format isn't supported, I need it in a webm format, "
                "[see this guide](https://core.telegram.org/stickers/webm-vp9-encoding).",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview = True,
            )
        elif e.message == "Internal Server Error: sticker set not found (500)":
            msg.reply_text(
                f"Sticker successfully added to [pack](t.me/addstickers/{packname})\n"
                + f"Emoji is: {sticker_emoji}", parse_mode=ParseMode.MARKDOWN
            )
        else:
            msg.reply_text(f"Oops! looks like something happened that shouldn't happen! ({e.message})")
            raise

def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    webm_sticker=None,
    tgs_sticker=None,
):
    name = user.first_name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = f" {packnum}"
        success = context.bot.create_new_sticker_set(
            user.id,
            packname,
            f"{name}s {'animated ' if tgs_sticker else 'video ' if webm_sticker else ''}kang pack{extra_version}",
            tgs_sticker=tgs_sticker or None,
            webm_sticker=webm_sticker or None,
            png_sticker=png_sticker or None,
            emojis=emoji,
        )

    except TelegramError as e:
        print(e)
        if e.message == 'Sticker set name is already occupied':
            msg.reply_text(
                'Your pack can be found [here](t.me/addstickers/%s)'
                % packname,
                parse_mode=ParseMode.MARKDOWN,
            )

            return
        elif e.message in ('Peer_id_invalid', 'bot was blocked by the user'):
            msg.reply_text(
                'Contact me in PM first.',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text='Start',
                                url=f't.me/{context.bot.username}',
                            )
                        ]
                    ]
                ),
            )

            return
        elif (
            e.message
            == 'Internal Server Error: created sticker set not found (500)'
        ):
            success = True
        elif e.message == 'Sticker_video_nowebm':
            msg.reply_text(
                "This media format isn't supported, I need it in a webm format, "
                "[see this guide](https://core.telegram.org/stickers/webm-vp9-encoding).",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview = True,
            )
            return
        else:
            success = False
    if success:
        msg.reply_text(
            f"Sticker pack successfully created. Get it [here](t.me/addstickers/{packname})",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")
