import datetime

from .. import dt_delta
from . import db

warns = db.warn_s
settings = db.warn_settings


def warn_user(user_id, chat_id, reason=""):
    _warn = warns.find_one({"chat_id": chat_id, "user_id": user_id})
    if _warn:
        reasons = _warn.get("reasons") or []
        reasons.append(reason)
        num_warns = _warn["num_warns"] + 1
    else:
        reasons = [reason]
        num_warns = 1
    rr = reasons
    p = settings.find_one({"chat_id": chat_id})
    if p and p.get("expire"):
        h, m = dt_delta(p.get("expiretime"))
        expire = True
        expireafter = datetime.datetime.now() + datetime.timedelta(hours=h, minutes=m)
    else:
        expire = False
        expireafter = 0
    num_w = num_warns
    if p and num_warns == p.get("limit"):
        num_w = 0
        reasons = []
    elif not p and num_warns == 3:
        num_w = 0
        reasons = []
    warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {
            "$set": {
                "reasons": reasons,
                "num_warns": num_w,
                "expire": expire,
                "expireafter": expireafter,
            }
        },
        upsert=True,
    )
    if p and num_warns == p.get("limit"):
        return (
            True,
            p.get("strength"),
            p.get("time"),
            p.get("limit"),
            num_warns,
            rr or [],
        )
    elif not p and num_warns == 3:
        return (True, "ban", 0, 3, num_warns, rr or [])
    else:
        if p and num_warns == p.get("limit"):
            return (False, "ban", 0, p.get("limit"), num_warns, rr or [])
        else:
            return (False, "ban", 0, 3, num_warns, rr or [])


def remove_warn(user_id, chat_id):
    _warn = warns.find_one({"chat_id": chat_id, "user_id": user_id})
    if _warn and _warn["num_warns"] > 0:
        warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"num_warns": _warn["num_warns"] - 1}},
            upsert=True,
        )
        return True
    return False


def reset_warns(user_id, chat_id):
    _warn = warns.find_one({"chat_id": chat_id, "user_id": user_id})
    if _warn and _warn["num_warns"] > 0:
        warns.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"num_warns": 0}},
            upsert=True,
        )
        return True
    return False


def get_warns(user_id, chat_id):
    _warn = warns.find_one({"chat_id": chat_id, "user_id": user_id})
    if _warn:
        return _warn["num_warns"], _warn["reasons"]
    return None


def reset_all_warns(chat_id):
    warns.delete_one({"chat_id": chat_id})


def set_warn_limit(chat_id, limit=3):
    _settings = settings.find_one({"chat_id": chat_id})
    if _settings:
        warn_strength = _settings.get("strength")
        warn_time = _settings.get("time")
        expire = _settings.get("expire")
        expiretime = _settings.get("expiretime")
    else:
        warn_strength = "ban"
        warn_time = 0
        expire = False
        expiretime = 0
    settings.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "limit": limit,
                "strength": warn_strength,
                "time": warn_time,
                "expire": expire,
                "expiretime": expiretime,
            }
        },
        upsert=True,
    )


def set_warn_strength(chat_id, mode, time=0):
    _settings = settings.find_one({"chat_id": chat_id})
    if _settings:
        limit = _settings.get("limit")
        expire = _settings.get("expire")
        expiretime = _settings.get("expiretime")
    else:
        limit = 3
        expire = False
        expiretime = 0
    settings.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "limit": limit,
                "strength": mode,
                "time": time,
                "expire": expire,
                "expiretime": expiretime,
            }
        },
        upsert=True,
    )


def get_warn_strength(chat_id):
    _s = settings.find_one({"chat_id": chat_id})
    if _s:
        return _s.get("strength"), _s.get("time")
    return "ban", 0


def get_warn_limit(chat_id):
    _s = settings.find_one({"chat_id": chat_id})
    if _s:
        return _s.get("limit")
    return 3


def get_warn_settings(chat_id):
    _s = settings.find_one({"chat_id": chat_id})
    if _s:
        return _s.get("limit"), _s.get("strength"), _s.get("time"), _s.get("expiretime")
    return 3, "ban", 0, 0


def set_warn_expire(chat_id, time):
    _s = settings.find_one({"chat_id": chat_id})
    if _s:
        strength = _s.get("strength")
        warntime = _s.get("time")
        limit = _s.get("limit")
    else:
        strength = "ban"
        limit = 3
        warntime = 0
    if time != 0:
        mode = True
    else:
        mode = False
    settings.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "limit": limit,
                "strength": strength,
                "time": warntime,
                "expire": mode,
                "expiretime": time,
            }
        },
        upsert=True,
    )


def get_warn_expire(chat_id):
    _s = settings.find_one({"chat_id": chat_id})
    if _s:
        return _s.get("expire"), _s.get("expiretime")
    return False, 0
