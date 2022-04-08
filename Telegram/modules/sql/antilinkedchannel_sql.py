import threading

from sqlalchemy import Boolean
from sqlalchemy.sql.sqltypes import String
from sqlalchemy import Column

from Telegram.modules.sql import BASE, SESSION


class AntiLinkedChannelSettings(BASE):
    __tablename__ = "anti_linked_channel_settings"

    chat_id = Column(String(14), primary_key=True)
    setting = Column(Boolean, default=False, nullable=False)

    def __init__(self, chat_id: int, disabled: bool):
        self.chat_id = str(chat_id)
        self.setting = disabled

    def __repr__(self):
        return "<Antilinked setting {} ({})>".format(self.chat_id, self.setting)

class AntiPinChannelSettings(BASE):
    __tablename__ = "anti_pin_channel_settings"

    chat_id = Column(String(14), primary_key=True)
    setting = Column(Boolean, default=False, nullable=False)

    def __init__(self, chat_id: int, disabled: bool):
        self.chat_id = str(chat_id)
        self.setting = disabled

    def __repr__(self):
        return "<Antipin setting {} ({})>".format(self.chat_id, self.setting)


AntiLinkedChannelSettings.__table__.create(checkfirst=True)
ANTI_LINKED_CHANNEL_SETTING_LOCK = threading.RLock()

AntiPinChannelSettings.__table__.create(checkfirst=True)
ANTI_PIN_CHANNEL_SETTING_LOCK = threading.RLock()


def enable_linked(chat_id: int):
    with ANTI_LINKED_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiLinkedChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiLinkedChannelSettings(chat_id, True)

        chat.setting = True
        SESSION.add(chat)
        SESSION.commit()

def enable_pin(chat_id: int):
    with ANTI_PIN_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiPinChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiPinChannelSettings(chat_id, True)

        chat.setting = True
        SESSION.add(chat)
        SESSION.commit()


def disable_linked(chat_id: int):
    with ANTI_LINKED_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiLinkedChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiLinkedChannelSettings(chat_id, False)

        chat.setting = False
        SESSION.add(chat)
        SESSION.commit()

def disable_pin(chat_id: int):
    with ANTI_PIN_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiPinChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiPinChannelSettings(chat_id, False)

        chat.setting = False
        SESSION.add(chat)
        SESSION.commit()


def status_linked(chat_id: int) -> bool:
    with ANTI_LINKED_CHANNEL_SETTING_LOCK:
        d = SESSION.query(AntiLinkedChannelSettings).get(str(chat_id))
        if not d:
            return False
        return d.setting

def status_pin(chat_id: int) -> bool:
    with ANTI_PIN_CHANNEL_SETTING_LOCK:
        d = SESSION.query(AntiPinChannelSettings).get(str(chat_id))
        if not d:
            return False
        return d.setting


def migrate_chat(old_chat_id, new_chat_id):
    with ANTI_LINKED_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiLinkedChannelSettings).get(str(old_chat_id))
        if chat:
            chat.chat_id = new_chat_id
            SESSION.add(chat)

        SESSION.commit()
    with ANTI_PIN_CHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiPinChannelSettings).get(str(old_chat_id))
        if chat:
            chat.chat_id = new_chat_id
            SESSION.add(chat)

        SESSION.commit()
