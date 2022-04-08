import threading

from sqlalchemy import Boolean
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import Column

from Telegram.modules.sql import BASE, SESSION


class AntiChannelSettings(BASE):
    __tablename__ = "anti_channel_settings"

    chat_id = Column(String(14), primary_key=True)
    setting = Column(Boolean, default=False, nullable=False)

    def __init__(self, chat_id: int, disabled: bool):
        self.chat_id = str(chat_id)
        self.setting = disabled

    def __repr__(self):
        return "<Antiflood setting {} ({})>".format(self.chat_id, self.setting)


AntiChannelSettings.__table__.create(checkfirst=True)
ANTICHANNEL_SETTING_LOCK = threading.RLock()


def enable_antichannel(chat_id: int):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiChannelSettings(chat_id, True)

        chat.setting = True
        SESSION.add(chat)
        SESSION.commit()


def disable_antichannel(chat_id: int):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiChannelSettings(chat_id, False)

        chat.setting = False
        SESSION.add(chat)
        SESSION.commit()


def antichannel_status(chat_id: int) -> bool:
    with ANTICHANNEL_SETTING_LOCK:
        d = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not d:
            return False
        return d.setting


def migrate_chat(old_chat_id, new_chat_id):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(old_chat_id))
        if chat:
            chat.chat_id = new_chat_id
            SESSION.add(chat)

        SESSION.commit()
