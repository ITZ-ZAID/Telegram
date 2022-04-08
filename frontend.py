from dearpygui.core import *
from dearpygui.simple import *
from platform import python_version
from Telegram.__main__ import STATS

try:
    from telegram import __version__ as pver
except ImportError:
    pver = "N/A"

with window("About"):
    add_text("Kigyo telegram bot")
    add_text("Maintained with <3 by Dank-del (github.com/Dank-del)")
    add_text("Enviroment:")
    add_text(f"Bot lib: python-telegram-bot v{pver}.", bullet=True)
    add_text(f"Python version: {python_version()}.", bullet=True)
    add_text("Source:")
    add_text("GitHub: github.com/Dank-del/EnterpriseALRobot", bullet=True)
    add_text("GitLab: gitlab.com/Dank-del/EnterpriseALRobot", bullet=True)

with window("stats"):
    add_text("\n*Bot statistics*:\n"+ "\n".join([mod.__stats__() for mod in STATS]))



start_dearpygui(primary_window="About")
