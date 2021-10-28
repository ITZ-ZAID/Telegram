from sqlalchemy import Column, String

from TGNRobot.modules.sql import BASE, SESSION


class Nsfwatch(BASE):
    __tablename__ = "nsfwatch"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Nsfwatch.__table__.create(checkfirst=True)


def add_nsfwatch(chat_id: str):
    nsfws = Nsfwatch(str(chat_id))
    SESSION.add(nsfws)
    SESSION.commit()


def rmnsfwatch(chat_id: str):
    nsfwm = SESSION.query(Nsfwatch).get(str(chat_id))
    if nsfwm:
        SESSION.delete(nsfwm)
        SESSION.commit()


def get_all_nsfw_enabled_chat():
    stark = SESSION.query(Nsfwatch).all()
    SESSION.close()
    return stark


def is_nsfwatch_indb(chat_id: str):
    try:
        s__ = SESSION.query(Nsfwatch).get(str(chat_id))
        if s__:
            return str(s__.chat_id)
    finally:
        SESSION.close()
