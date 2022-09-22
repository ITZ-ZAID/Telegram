import sys
import logging
import importlib
from pathlib import Path
from Zaid import Zaid
from config import OWNER_ID
from telethon import events

def load_plugins(plugin_name):
    path = Path(f"Zaid/Plugins/{plugin_name}.py")
    name = "Zaid.Plugins.{}".format(plugin_name)
    spec = importlib.util.spec_from_file_location(name, path)
    load = importlib.util.module_from_spec(spec)
    load.logger = logging.getLogger(plugin_name)
    spec.loader.exec_module(load)
    sys.modules["Zaid.Plugins." + plugin_name] = load
    print("Bot has Started " + plugin_name)



def Zbot(**args):
    pattern = args.get("pattern", None)
    r_pattern = r"^[/?!.]"
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern
    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        async def wrapper(check):
            if check.sender_id and check.sender_id != OWNER_ID:
                pass
            try:
                await func(check)
            except BaseException:
                return
            else:
                pass

        Zaid.add_event_handler(wrapper, events.NewMessage(**args))
        return wrapper

    return decorator


def Zquery(**args):
    pattern = args.get("pattern", None)

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    def decorator(func):
        Zaid.add_event_handler(func, events.InlineQuery(**args))
        return func

    return decorator


def Zinline(**args):
    def decorator(func):
        Zaid.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator
