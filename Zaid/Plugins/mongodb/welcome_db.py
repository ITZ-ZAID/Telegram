from . import db

welcome = db.welcome
goodbye = db.goodbye
clean_service = db.clean_service


def set_welcome(chat_id: int, w_text, id=None, hash=None, ref=None, type=None):
    welcome.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "text": w_text,
                "id": id,
                "hash": hash,
                "ref": ref,
                "mtype": type,
                "mode": True,
            }
        },
        upsert=True,
    )


def get_welcome(chat_id: int):
    _w = welcome.find_one({"chat_id": chat_id})
    if _w:
        return _w
    return None


def get_welcome_mode(chat_id: int):
    _w = welcome.find_one({"chat_id": chat_id})
    if _w:
        return _w["mode"]
    return True


def toggle_welcome(chat_id: int, mode):
    _w = welcome.find_one({"chat_id": chat_id})
    if _w:
        return welcome.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}})
    welcome.insert_one(
        {
            "chat_id": chat_id,
            "text": None,
            "id": None,
            "hash": None,
            "ref": None,
            "mtype": None,
            "mode": mode,
        }
    )


def reset_welcome(chat_id: int):
    _w = welcome.find_one({"chat_id": chat_id})
    if _w:
        welcome.delete_one({"chat_id": chat_id})


def set_goodbye(chat_id: int, w_text, id=None, hash=None, ref=None, type=None):
    goodbye.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "text": w_text,
                "id": id,
                "hash": hash,
                "ref": ref,
                "mtype": type,
                "mode": True,
            }
        },
        upsert=True,
    )


def get_goodbye(chat_id: int):
    _w = goodbye.find_one({"chat_id": chat_id})
    if _w:
        return _w
    return None


def toggle_goodbye(chat_id: int, mode):
    _w = goodbye.find_one({"chat_id": chat_id})
    if _w:
        return goodbye.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}})
    goodbye.insert_one(
        {
            "chat_id": chat_id,
            "text": None,
            "id": None,
            "hash": None,
            "ref": None,
            "mtype": None,
            "mode": mode,
        }
    )


def reset_goodbye(chat_id: int):
    _w = goodbye.find_one({"chat_id": chat_id})
    if _w:
        goodbye.delete_one({"chat_id": chat_id})


def get_goodbye_mode(chat_id: int):
    _w = goodbye.find_one({"chat_id": chat_id})
    if _w:
        return _w["mode"]
    return False


def set_clean_service(chat_id, mode):
    clean_service.update_one(
        {"chat_id": chat_id}, {"$set": {"service": mode}}, upsert=True
    )


def set_clean_welcome(chat_id, mode):
    clean_service.update_one(
        {"chat_id": chat_id}, {"$set": {"welcome": mode}}, upsert=True
    )


def set_clean_goodbye(chat_id, mode):
    clean_service.update_one(
        {"chat_id": chat_id}, {"$set": {"goodbye": mode}}, upsert=True
    )


def set_welcome_id(chat_id, id):
    clean_service.update_one(
        {"chat_id": chat_id}, {"$set": {"welcome_id": id}}, upsert=True
    )


def set_goodbye_id(chat_id, id):
    clean_service.update_one(
        {"chat_id": chat_id}, {"$set": {"goodbye_id": id}}, upsert=True
    )


def get_clean_service(chat_id):
    _c = clean_service.find_one({"chat_id": chat_id})
    if _c:
        try:
            return _c["service"]
        except KeyError:
            return False
    return False


def get_clean_welcome(chat_id):
    _c = clean_service.find_one({"chat_id": chat_id})
    if _c:
        try:
            return _c["welcome"]
        except KeyError:
            return False
    return False


def get_clean_goodbye(chat_id):
    _c = clean_service.find_one({"chat_id": chat_id})
    if _c:
        try:
            return _c["goodbye"]
        except KeyError:
            return False
    return False


def get_welcome_id(chat_id):
    _c = clean_service.find_one({"chat_id": chat_id})
    if _c:
        try:
            return _c["welcome_id"]
        except KeyError:
            return False
    return False


def get_goodbye_id(chat_id):
    _c = clean_service.find_one({"chat_id": chat_id})
    if _c:
        try:
            return _c["goodbye_id"]
        except KeyError:
            return False
    return False
