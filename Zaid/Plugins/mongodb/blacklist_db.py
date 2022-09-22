from . import db

blacklist = db.blacklist

CHAT_BLACKLISTS = {}


def add_to_blacklist(chat_id, trigger):
    _bl = blacklist.find_one({"chat_id": chat_id})
    if _bl:
        bl = _bl["blacklists"]
        mode = _bl["mode"]
        time = _bl["time"]
        reason = _bl["reason"]
    else:
        bl = []
        mode = "nothing"
        time = 0
        reason = None
    bl.append(trigger)
    blacklist.update_one(
        {"chat_id": chat_id},
        {"$set": {"blacklists": bl, "mode": mode, "time": time, "reason": reason}},
        upsert=True,
    )
    if CHAT_BLACKLISTS.get(str(chat_id)):
        CHAT_BLACKLISTS[str(chat_id)].append(trigger)
    else:
        CHAT_BLACKLISTS[str(chat_id)] = []
        CHAT_BLACKLISTS[str(chat_id)].append(trigger)


def rm_from_blacklist(chat_id, trigger):
    _bl = blacklist.find_one({"chat_id": chat_id})
    if _bl:
        bl = _bl["blacklists"]
    else:
        return False
    if trigger in bl:
        bl.remove(trigger)
    else:
        return False
    blacklist.update_one(
        {"chat_id": chat_id}, {"$set": {"blacklists": bl}}, upsert=True
    )
    if trigger in CHAT_BLACKLISTS.get(str(chat_id)):
        CHAT_BLACKLISTS[str(chat_id)].remove(trigger)


def remove_all_blacklist(chat_id):
    blacklist.delete_one({"chat_id": chat_id})
    CHAT_BLACKLISTS.pop(str(chat_id))


def get_chat_blacklist(chat_id):
    return CHAT_BLACKLISTS.get(str(chat_id))


def __load_chat_blacklists():
    for x in blacklist.find({}):
        CHAT_BLACKLISTS[str(x.get("chat_id"))] = x.get("blacklists")


def set_mode(chat_id, mode, time=0):
    _bl = blacklist.find_one({"chat_id": chat_id})
    if _bl:
        return blacklist.update_one(
            {"chat_id": chat_id}, {"$set": {"mode": mode, "time": time}}, upsert=True
        )
    blacklist.update_one(
        {"chat_id": chat_id},
        {"$set": {"blacklists": [], "mode": mode, "time": time, "reason": None}},
        upsert=True,
    )


def get_mode(chat_id):
    _bl = blacklist.find_one({"chat_id": chat_id})
    if _bl:
        return _bl.get("mode"), _bl.get("time")
    return "nothing", 0


def set_blocklist_reason(chat_id, reason=None):
    print("#")


__load_chat_blacklists()
