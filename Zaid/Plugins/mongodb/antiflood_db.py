from . import db

antiflood = db.antiflood

CHAT_FLOOD = {}


def set_flood(chat_id, amount=3):
    _flood = antiflood.find_one({"chat_id": chat_id})
    if _flood:
        mode = _flood["mode"]
        time = _flood["time"]
    else:
        mode = "ban"
        time = 0
    antiflood.update_one(
        {"chat_id": chat_id},
        {"$set": {"value": amount, "mode": mode, "time": time}},
        upsert=True,
    )
    if CHAT_FLOOD.get(chat_id):
        CHAT_FLOOD[chat_id] = (CHAT_FLOOD[chat_id][0], CHAT_FLOOD[chat_id][1], amount)


def update_flood(chat_id, user_id):
    if not CHAT_FLOOD.get(chat_id):
        old_id = None
        c = 0
        f = antiflood.find_one({"chat_id": chat_id})
        if f:
            limit = f.get("value")
        else:
            limit = 3
    else:
        c = CHAT_FLOOD.get(chat_id)[1]
        old_id = CHAT_FLOOD.get(chat_id)[0]
        limit = CHAT_FLOOD.get(chat_id)[2]
    if user_id != old_id:
        CHAT_FLOOD[chat_id] = (user_id, 1, limit)
        return False
    else:
        c += 1
        if c >= limit:
            CHAT_FLOOD[chat_id] = (user_id, 0, limit)
            return True
        CHAT_FLOOD[chat_id] = (user_id, c, limit)
        return False


def get_flood_limit(chat_id):
    _flood = antiflood.find_one({"chat_id": chat_id})
    if _flood:
        return _flood.get("value")
    return 0


def set_flood_strength(chat_id, mode, time=0):
    _flood = antiflood.find_one({"chat_id": chat_id})
    if _flood:
        value = _flood["value"]
    else:
        value = 0
    antiflood.update_one(
        {"chat_id": chat_id},
        {"$set": {"value": value, "mode": mode, "time": time}},
        upsert=True,
    )


def get_flood_settings(chat_id):
    _flood = antiflood.find_one({"chat_id": chat_id})
    if _flood:
        return _flood.get("mode"), _flood.get("time")
    return "ban", 0
