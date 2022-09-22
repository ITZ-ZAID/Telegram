from . import db

chats = db.nightmode


def add_nightmode(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    if _chats:
        c = _chats["chats"]
    else:
        c = []
    c.append(chat_id)
    chats.update_one({"type": "main"}, {"$set": {"chats": c}}, upsert=True)


def rmnightmode(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    if _chats:
        c = _chats["chats"]
    else:
        c = []
    if chat_id in c:
        c.remove(chat_id)
    chats.update_one({"type": "main"}, {"$set": {"chats": c}}, upsert=True)


def get_all_chat_id():
    _chats = chats.find_one({"type": "main"})
    if _chats:
        return _chats["chats"]
    return None


def is_nightmode_indb(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    if not _chats:
        return False
    elif chat_id in _chats["chats"]:
        return True
    else:
        return False
