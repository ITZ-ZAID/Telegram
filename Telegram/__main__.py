import importlib
import re
import threading
from sys import argv
from typing import Optional

from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import (
    CallbackContext,
    Filters
)
from telegram.ext.dispatcher import DispatcherHandlerStop
from telegram.utils.helpers import escape_markdown

from Telegram import (
    ZInit,
    dispatcher,
    updater,
    TOKEN,
    WEBHOOK,
    OWNER_ID,
    OWNER_USERNAME,
    CERT_PATH,
    PORT,
    URL,
    log,
    telethn,
    AnieINIT
)
from config import Config
CHANNEL = Config.CHANNEL
SUPPORT = Config.SUPPORT

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from Telegram.modules import ALL_MODULES
from Telegram.modules.helper_funcs.chat_status import is_user_admin
from Telegram.modules.helper_funcs.decorators import zaid, zaidcallback, zaidmsg
from Telegram.modules.helper_funcs.misc import paginate_modules
from Telegram.modules.language import gs

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Telegram.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "get_help") and imported_module.get_help:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    """#TODO

    Params:
        chat_id  -
        text     -
        keyboard -
    """

    if not keyboard:
        kb = paginate_modules(0, HELPABLE, "help")
        # kb.append([InlineKeyboardButton(text='Support', url='https://t.me/TheSupportChat'),
        #           InlineKeyboardButton(text='Back', callback_data='start_back'),
        #           InlineKeyboardButton(text="Try inline", switch_inline_query_current_chat="")])
        keyboard = InlineKeyboardMarkup(kb)
    dispatcher.bot.send_message(
        chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard
    )


@zaid(command='text')
def test(update: Update, _: CallbackContext):
    """#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    """
    # pprint(ast.literal_eval(str(update)))
    # update.effective_message.reply_text("Hola tester! _I_ *have* `markdown`", parse_mode=ParseMode.MARKDOWN)
    update.effective_message.reply_text("This person edited a message")
    print(update.effective_message)


@zaidcallback(pattern=r'start_back')
@zaid(command='start', pass_args=True)
def start(update: Update, context: CallbackContext):  # sourcery no-metrics
    """#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    """
    chat = update.effective_chat
    args = context.args

    if hasattr(update, 'callback_query'):
        query = update.callback_query
        if hasattr(query, 'id'):
            first_name = update.effective_user.first_name
            update.effective_message.edit_text(
                text=gs(chat.id, "pm_start_text").format(
                    escape_markdown(context.bot.first_name),
                    escape_markdown(first_name),
                    escape_markdown(OWNER_USERNAME),
                    OWNER_ID,
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [ 
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "add_bot_to_group_btn").format(context.bot.first_name),
                                url="t.me/{}?startgroup=true".format(
                                    context.bot.username
                                ),
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "owner_btn"),
                                url=f'https://t.me/{OWNER_USERNAME}',
                            ),
                            InlineKeyboardButton(
                                text=gs(chat.id, "source_btn"),
                                url="https://github.com/ITZ-ZAID/Telegram",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "support_chat_link_btn"),
                                url=f'https://t.me/{SUPPORT}',
                            ),
                            InlineKeyboardButton(
                                text="Help",
                                callback_data="help_back",
                            ),
                            InlineKeyboardButton(
                                text=gs(chat.id, "updates_channel_link_btn"),
                                url=f"https://t.me/{CHANNEL}",
                            ),
                        ],
                    ]
                ),
            )

            context.bot.answer_callback_query(query.id)
            return

    if update.effective_chat.type == "private":
        if args and len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, (gs(chat.id, "pm_help_text")))
            elif args[0].lower().startswith("ghelp_"):
                query = update.callback_query
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                help_list = HELPABLE[mod].get_help(chat.id)
                help_text = []
                help_buttons = []
                if isinstance(help_list, list):
                    help_text = help_list[0]
                    help_buttons = help_list[1:]
                elif isinstance(help_list, str):
                    help_text = help_list
                text = "Here is the help for the *{}* module:\n".format(HELPABLE[mod].__mod_name__) + help_text
                help_buttons.append(
                    [InlineKeyboardButton(text="Back", callback_data="help_back")]
                )
                send_help(
                    chat.id,
                    text,
                    InlineKeyboardMarkup(help_buttons),
                )

                if hasattr(query, "id"):
                    context.bot.answer_callback_query(query.id)
            elif args[0].lower() == "markdownhelp":
                IMPORTED["extras"].markdown_help_sender(update)
            elif args[0].lower() == "nations":
                IMPORTED["nations"].send_nations(update)
            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(update, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_text(
                text=gs(chat.id, "pm_start_text").format(
                    escape_markdown(context.bot.first_name),
                    escape_markdown(first_name),
                    escape_markdown(OWNER_USERNAME),
                    OWNER_ID,
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "add_bot_to_group_btn").format(context.bot.first_name),
                                url="t.me/{}?startgroup=true".format(
                                    context.bot.username
                                ),
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "owner_btn"),
                                url=f'https://t.me/{OWNER_USERNAME}',
                            ),
                            InlineKeyboardButton(
                                text=gs(chat.id, "source_btn"),
                                url="https://github.com/ITZ-ZAID/Telegram",
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text=gs(chat.id, "support_chat_link_btn"),
                                url=f'https://t.me/{SUPPORT}',
                            ),
                            InlineKeyboardButton(
                                text="Help",
                                callback_data="help_back",
                            ),
                            InlineKeyboardButton(
                                text=gs(chat.id, "updates_channel_link_btn"),
                                url=f"https://t.me/{CHANNEL}",
                            ),
                        ],
                    ]
                ),
            )

    else:
        update.effective_message.reply_text(gs(chat.id, "grp_start_text"))

    if hasattr(update, 'callback_query'):
        query = update.callback_query
        if hasattr(query, 'id'):
            context.bot.answer_callback_query(query.id)


# for test purposes
def error_callback(_, context: CallbackContext):
    """#TODO

    Params:
        update  -
        context -
    """

    try:
        raise context.error
    except (Unauthorized, BadRequest):
        pass
        # remove update.message.chat_id from conversation list
    except TimedOut:
        pass
        # handle slow connection problems
    except NetworkError:
        pass
        # handle other connection problems
    except ChatMigrated:
        pass
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        pass
        # handle all other telegram related errors


@zaidcallback(pattern=r'help_')
def help_button(update: Update, context: CallbackContext):
    """#TODO

    Params:
        update  -
        context -
    """

    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    chat = update.effective_chat
    # print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            module = module.replace("_", " ")
            help_list = HELPABLE[module].get_help(update.effective_chat.id)
            if isinstance(help_list, list):
                help_text = help_list[0]
                help_buttons = help_list[1:]
            elif isinstance(help_list, str):
                help_text = help_list
                help_buttons = []
            text = (
                    "Here is the help for the *{}* module:\n".format(
                        HELPABLE[module].__mod_name__
                    )
                    + help_text
            )
            help_buttons.append(
                [InlineKeyboardButton(text="Back", callback_data="help_back")]
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(help_buttons),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            kb = paginate_modules(curr_page - 1, HELPABLE, "help")
            # kb.append([InlineKeyboardButton(text='Go Back', callback_data='start_back'')])
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            kb = paginate_modules(next_page + 1, HELPABLE, "help")
            # kb.append([InlineKeyboardButton(text='Go Back', callback_data='start_back')])
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )

        elif back_match:
            kb = paginate_modules(0, HELPABLE, "help")
            # kb.append([InlineKeyboardButton(text='Go Back', callback_data='start_back')])
            query.message.edit_text(
                text=gs(chat.id, "pm_help_text"),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(kb),
            )

        # ensure no spinny white circle
        context.bot.answer_callback_query(query.id)
        # query.message.delete()

    except BadRequest:
        pass


@zaid(command='help')
def get_help(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update  -
        context -
    '''

    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:

        if len(args) >= 2:
            if any(args[1].lower() == x for x in HELPABLE):
                module = args[1].lower()
                update.effective_message.reply_text(
                    f"Contact me in PM to get help of {module.capitalize()}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Help",
                                    url="t.me/{}?start=ghelp_{}".format(
                                        context.bot.username, module
                                    ),
                                )
                            ]
                        ]
                    ),
                )
            else:
                update.effective_message.reply_text(
                    f"<code>{args[1].lower()}</code> is not a module",
                    parse_mode=ParseMode.HTML,
                )
            return

        update.effective_message.reply_text(
            "Contact me in PM to get the list of possible commands.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Help",
                            url="t.me/{}?start=help".format(context.bot.username),
                        )
                    ]
                ]
            ),
        )
        return

    if len(args) >= 2:
        if any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            help_list = HELPABLE[module].get_help(chat.id)
            help_text = []
            help_buttons = []
            if isinstance(help_list, list):
                help_text = help_list[0]
                help_buttons = help_list[1:]
            elif isinstance(help_list, str):
                help_text = help_list
            text = "Here is the available help for the *{}* module:\n".format(HELPABLE[module].__mod_name__) + help_text
            help_buttons.append(
                [InlineKeyboardButton(text="Go Back", callback_data="help_back")]
            )
            send_help(
                chat.id,
                text,
                InlineKeyboardMarkup(help_buttons),
            )
        else:
            update.effective_message.reply_text(
                f"<code>{args[1].lower()}</code> is not a module",
                parse_mode=ParseMode.HTML,
            )
    else:
        send_help(chat.id, (gs(chat.id, "pm_help_text")))


def send_settings(chat_id: int, user_id: int, user=False):
    '''#TODO

    Params:
        chat_id -
        user_id -
        user    -
    '''

    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    elif CHAT_SETTINGS:
        chat_name = dispatcher.bot.getChat(chat_id).title
        dispatcher.bot.send_message(
            user_id,
            text="Which module would you like to check {}'s settings for?".format(
                chat_name
            ),
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
            ),
        )
    else:
        dispatcher.bot.send_message(
            user_id,
            "Seems like there aren't any chat settings available :'(\nSend this "
            "in a group chat you're admin in to find its current settings!",
            parse_mode=ParseMode.MARKDOWN,
        )


@zaidcallback(pattern=r"stngs_")
def settings_button(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Back",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                     "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            'Message is not modified',
            'Query_id_invalid',
            "Message can't be deleted",
        ]:
            log.exception('Exception in settings buttons. %s', str(query.data))


@zaid(command='settings')
def get_settings(update: Update, context: CallbackContext):
    '''#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    '''

    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type == chat.PRIVATE:
        send_settings(chat.id, user.id, True)

    elif is_user_admin(update, user.id):
        text = "Click here to get this chat's settings, as well as yours."
        msg.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Settings",
                            url="t.me/{}?start=stngs_{}".format(
                                context.bot.username, chat.id
                            ),
                        )
                    ]
                ]
            ),
        )
    else:
        text = "Click here to check your settings."


@zaid(command='donate')
def donate(update: Update, _: CallbackContext):
    """#TODO

    Params:
        update: Update           -
        context: CallbackContext -
    """

    update.effective_message.reply_text("can Donate Via \n Razorpay 👉 https://pages.razorpay.com/GODFATHERDONATIONS \n PayPal 👉 https://www.paypal.com/paypalme/mrakki58 for more Contact in @Godfatherakki!  >_<")


@zaidmsg(Filters.status_update.migrate)
def migrate_chats(update: Update, context: CallbackContext):
    """#TODO
    Params:
        update: Update           -
        context: CallbackContext -
    """

    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    log.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    log.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():
    dispatcher.add_error_handler(error_callback)
    # dispatcher.add_error_handler(error_handler)

    if WEBHOOK:
        log.info("Using webhooks.")
        updater.start_webhook(listen="127.0.0.1", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        log.info(f"Using long polling. | BOT: [@{dispatcher.bot.username}]")
        AnieINIT.bot_id = dispatcher.bot.id
        AnieINIT.bot_username = dispatcher.bot.username
        AnieINIT.bot_name = dispatcher.bot.first_name
        updater.start_polling(timeout=15, read_latency=4, allowed_updates=Update.ALL_TYPES, drop_pending_updates=ZInit.DROP_UPDATES)
    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()
    updater.idle()


if __name__ == "__main__":
    log.info("[TELEGRAM] Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    main()
