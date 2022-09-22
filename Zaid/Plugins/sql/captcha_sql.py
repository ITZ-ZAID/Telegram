import threading

from sqlalchemy import Boolean, Column, Integer, Numeric, UnicodeText

from . import BASE, SESSION


class Captcha(BASE):
    __tablename__ = "cbsa"
    chat_id = Column(Numeric, primary_key=True)
    mode = Column(Boolean)
    time = Column(Integer)
    ctime = Column(Integer)
    style = Column(UnicodeText)

    def __init__(self, chat_id, mode=True, time=0, ctime=0, style="button"):
        self.chat_id = chat_id
        self.mode = mode
        self.time = time
        self.ctime = ctime
        self.style = style

    def __repr__(self):
        return "{}".format(self.chat_id)


Captcha.__table__.create(checkfirst=True)

C_LOCK = threading.RLock()
CAPTCHA_CHAT = {}


def set_captcha(chat_id, style):
    with C_LOCK:
        global CAPTCHA_CHAT
        curr = SESSION.query(Captcha).get(chat_id)
        if not curr:
            curr = Captcha(chat_id, True, 0, 0, style)
        else:
            curr.mode = True
            curr.time = 0
            curr.ctime = 0
            curr.style = style
        SESSION.add(curr)
        SESSION.commit()
        CAPTCHA_CHAT[str(chat_id)] = {
            "mode": True,
            "time": 0,
            "ctime": 0,
            "style": style,
        }


def set_style(chat_id, style):
    with C_LOCK:
        global CAPTCHA_CHAT
        curr = SESSION.query(Captcha).get(chat_id)
        if not curr:
            curr = Captcha(chat_id, True, 0, 0, style)
            CAPTCHA_CHAT[str(chat_id)] = {
                "mode": True,
                "time": 0,
                "ctime": 0,
                "style": style,
            }
        curr.style = style
        SESSION.add(curr)
        SESSION.commit()
        CAPTCHA_CHAT[f"{chat_id}"]["style"] = style


def set_mode(chat_id, mode):
    with C_LOCK:
        global CAPTCHA_CHAT
        curr = SESSION.query(Captcha).get(chat_id)
        if not curr:
            curr = Captcha(chat_id, mode, 0, 0, "button")
            CAPTCHA_CHAT[str(chat_id)] = {
                "mode": mode,
                "time": 0,
                "ctime": 0,
                "style": "button",
            }
        curr.mode = mode
        SESSION.add(curr)
        SESSION.commit()
        CAPTCHA_CHAT[f"{chat_id}"]["mode"] = mode


def set_time(chat_id, time):
    with C_LOCK:
        global CAPTCHA_CHAT
        curr = SESSION.query(Captcha).get(chat_id)
        if not curr:
            curr = Captcha(chat_id, True, 0, 0, style)
            CAPTCHA_CHAT[str(chat_id)] = {
                "mode": True,
                "time": time,
                "ctime": 0,
                "style": "button",
            }
        curr.time = time
        SESSION.add(curr)
        SESSION.commit()
        CAPTCHA_CHAT[f"{chat_id}"]["time"] = time


def set_unmute_time(chat_id, ctime):
    with C_LOCK:
        global CAPTCHA_CHAT
        curr = SESSION.query(Captcha).get(chat_id)
        if not curr:
            curr = Captcha(chat_id, True, 0, ctime, "button")
            CAPTCHA_CHAT[str(chat_id)] = {
                "mode": True,
                "time": 0,
                "ctime": ctime,
                "style": "button",
            }
        curr.ctime = ctime
        SESSION.add(curr)
        SESSION.commit()
        CAPTCHA_CHAT[f"{chat_id}"]["ctime"] = ctime


def get_mode(chat_id):
    get = CAPTCHA_CHAT.get(str(chat_id))
    if get is None:
        return False
    return get["mode"]


def get_style(chat_id):
    get = CAPTCHA_CHAT.get(str(chat_id))
    if get is None:
        return False
    return get["style"]


def get_time(chat_id):
    get = CAPTCHA_CHAT.get(str(chat_id))
    if get is None:
        return False
    return get["time"]


def get_unmute_time(chat_id):
    get = CAPTCHA_CHAT.get(str(chat_id))
    if get is None:
        return False
    return get["ctime"]


def __load_all_chats():
    global CAPTCHA_CHAT
    captcha = SESSION.query(Captcha).all()
    for x in captcha:
        CAPTCHA_CHAT[str(x.chat_id)] = {
            "mode": x.mode,
            "time": x.time,
            "ctime": x.ctime,
            "style": x.style,
        }


__load_all_chats()
