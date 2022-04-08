from .helper_funcs.misc import upload_text
from telegram import Update
from telegram.ext import CallbackContext
from Telegram.modules.helper_funcs.decorators import zaid
from io import BytesIO

@zaid(command='paste', pass_args=True)
def paste(update: Update, context: CallbackContext):
    args = context.args
    message = update.effective_message

    if message.reply_to_message:
        data = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.document:
            file_info = context.bot.get_file(message.reply_to_message.document.file_id)
            with BytesIO() as file:
                file_info.download(out=file)
                file.seek(0)
                data = file.read().decode()

    elif len(args) >= 1:
        data = message.text.split(None, 1)[1]
    else:
        message.reply_text("What am I supposed to do with this?")
        return
    
    txt = ""
    paste_url = upload_text(data)
    if not paste_url:
        txt = "Failed to paste data"
    else:
        txt = "Successfully uploaded to Privatebin: {}".format(paste_url)

    message.reply_text(txt, disable_web_page_preview=True)
