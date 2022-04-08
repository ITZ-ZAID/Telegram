import threading

from sqlalchemy import Column, String, UnicodeText
from Telegram.modules.sql import SESSION, BASE


class ChatLangs(BASE):
    __tablename__ = "chatlangs"
    chat_id = Column(String(14), primary_key=True)
    language = Column(UnicodeText)

    def __init__(self, chat_id, language):
        self.chat_id = str(chat_id)  # ensure string
        self.language = language

    def __repr__(self):
        return "Language {} chat {}".format(self.language, self.chat_id)


CHAT_LANG = {}
LANG_LOCK = threading.RLock()
ChatLangs.__table__.create(checkfirst=True)


def set_lang(chat_id: str, lang: str) -> None:
    with LANG_LOCK:
        curr = SESSION.query(ChatLangs).get(str(chat_id))
        if not curr:
            curr = ChatLangs(str(chat_id), lang)
            SESSION.add(curr)
            SESSION.flush()
        else:
            curr.language = lang

        CHAT_LANG[str(chat_id)] = lang
        SESSION.commit()


def get_chat_lang(chat_id: str) -> str:
    lang = CHAT_LANG.get(str(chat_id))
    if lang is None:
        lang = "en"
    return lang


def __load_chat_language() -> None:
    global CHAT_LANG
    try:
        allchats = SESSION.query(ChatLangs).all()
        CHAT_LANG = {x.chat_id: x.language for x in allchats}
    finally:
        SESSION.close()


__load_chat_language()
