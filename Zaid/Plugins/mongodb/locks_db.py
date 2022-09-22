from . import db

locks = db.locks

lock_1 = ["all", "album", "audio", "media", "bot", "button", "card"]
lock_2 = ["command", "comment", "contact", "document", "email", "emojigame"]
lock_3 = [
    "forward",
    "forwardchannel",
    "forwardbot",
    "forwarduser",
    "game",
    "gif",
    "inline",
    "invitelink",
]
lock_4 = ["invoice", "location", "phone", "photo", "poll", "preview", "sticker"]
lock_5 = ["text", "url", "video", "videonote", "voice"]

all_locks = lock_1 + lock_2 + lock_3 + lock_4 + lock_5


def add_lock(chat_id, type):
    _locks = locks.find_one({"chat_id": chat_id})
    if _locks:
        _lock = _locks["locked"]
    else:
        _lock = []
    _lock.append(type)
    new_lock = list(set(_lock))
    locks.update_one({"chat_id": chat_id}, {"$set": {"locked": new_lock}}, upsert=True)


def get_locks(chat_id):
    _locks = locks.find_one({"chat_id": chat_id})
    if _locks:
        return _locks["locked"]
    return None


def remove_lock(chat_id, type):
    _locks = locks.find_one({"chat_id": chat_id})
    if _locks:
        _lock = _locks["locked"]
    else:
        return
    if type in _lock:
        _lock.remove(type)
        locks.update_one({"chat_id": chat_id}, {"$set": {"locked": _lock}}, upsert=True)


def lock_all(chat_id):
    locks.update_one({"chat_id": chat_id}, {"$set": {"locked": all_locks}}, upsert=True)


def unlock_all(chat_id):
    locks.update_one({"chat_id": chat_id}, {"$set": {"locked": []}}, upsert=True)


def get_total_locks():
    _chats = locks.find({})
    _total = 0
    for x in _chats:
        _total += len(x["locked"])
    return _total
