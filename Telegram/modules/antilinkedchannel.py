import html

from telegram import Update, TelegramError
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters
from Telegram.modules.helper_funcs.chat_status import bot_admin, bot_can_delete

from Telegram.modules.helper_funcs.decorators import zaid, zaidmsg
from ..modules.helper_funcs.anonymous import user_admin, AdminPerms
import Telegram.modules.sql.antilinkedchannel_sql as sql


@zaid(command="antilinkedchan", group=112)
@bot_can_delete
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antilinkedchannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            if sql.status_pin(chat.id):
                sql.disable_pin(chat.id)
                sql.enable_pin(chat.id)
                message.reply_html("Enabled Linked channel deletion and Disabled anti channel pin in {}".format(html.escape(chat.title)))
            else:
                sql.enable_linked(chat.id)
                message.reply_html("Enabled anti linked channel in {}".format(html.escape(chat.title)))
        elif s in ["off", "no"]:
            sql.disable_linked(chat.id)
            message.reply_html("Disabled anti linked channel in {}".format(html.escape(chat.title)))
        else:
            message.reply_text("Unrecognized arguments {}".format(s))
        return
    message.reply_html(
        "Linked channel deletion is currently {} in {}".format(sql.status_linked(chat.id), html.escape(chat.title)))


@zaidmsg(Filters.is_automatic_forward, group=111)
def eliminate_linked_channel_msg(update: Update, _: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    if not sql.status_linked(chat.id):
        return
    try:
        message.delete()
    except TelegramError:
        return

@zaid(command="antichannelpin", group=114)
@bot_admin
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antipinchannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            if sql.status_linked(chat.id):
                sql.disable_linked(chat.id)
                sql.enable_pin(chat.id)
                message.reply_html("Disabled Linked channel deletion and Enabled anti channel pin in {}".format(html.escape(chat.title)))
            else:
                sql.enable_pin(chat.id)
                message.reply_html("Enabled anti channel pin in {}".format(html.escape(chat.title)))
        elif s in ["off", "no"]:
            sql.disable_pin(chat.id)
            message.reply_html("Disabled anti channel pin in {}".format(html.escape(chat.title)))
        else:
            message.reply_text("Unrecognized arguments {}".format(s))
        return
    message.reply_html(
        "Linked channel message unpin is currently {} in {}".format(sql.status_pin(chat.id), html.escape(chat.title)))


@zaidmsg(Filters.is_automatic_forward | Filters.status_update.pinned_message, group=113)
def eliminate_linked_channel_msg(update: Update, _: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    if not sql.status_pin(chat.id):
        return
    try:
        message.unpin()
    except TelegramError:
        return
