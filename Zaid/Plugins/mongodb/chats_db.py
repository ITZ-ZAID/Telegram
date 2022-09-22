from . import db

chats = db.chats


def add_chat(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    if _chats:
        c = _chats["chats"]
    else:
        c = []
    c.append(chat_id)
    chats.update_one({"type": "main"}, {"$set": {"chats": c}}, upsert=True)


def rm_chat(chat_id: int):
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


def is_chat(chat_id: int):
    _chats = chats.find_one({"type": "main"})
    if not _chats:
        return False
    elif chat_id in _chats["chats"]:
        return True
    else:
        return False



def get_total_chats():
    _chats = chats.find({})
    _total = 0
    for x in _chats:
        _total += len(x["notes"])
    return _total
