from . import db

filters = db.filters


def save_filter(chat_id, name, reply, id=None, hash=None, reference=None, type=None):
    name = name.lower().strip()
    _filter = filters.find_one({"chat_id": chat_id})
    if not _filter:
        _filters = {}
    else:
        _filters = _filter["filters"]
        if _filters == None:
            _filters = {}
    _filters[name] = {
        "reply": reply,
        "id": id,
        "hash": hash,
        "ref": reference,
        "mtype": type,
    }
    filters.update_one(
        {"chat_id": chat_id}, {"$set": {"filters": _filters}}, upsert=True
    )


def delete_filter(chat_id, name):
    name = name.strip().lower()
    _filters = filters.find_one({"chat_id": chat_id})
    if not _filters:
        _filter = {}
    else:
        _filter = _filters["filters"]
    if name in _filter:
        del _filter[name]
        filters.update_one(
            {"chat_id": chat_id}, {"$set": {"filters": _filter}}, upsert=True
        )


def get_filter(chat_id, name):
    name = name.strip().lower()
    _filters = filters.find_one({"chat_id": chat_id})
    if not _filters:
        _filter = {}
    else:
        _filter = _filters["filters"]
    if name in _filter:
        return _filter[name]
    return False


def get_all_filters(chat_id):
    _filters = filters.find_one({"chat_id": chat_id})
    if _filters:
        return _filters["filters"]
    return None


def delete_all_filters(chat_id):
    _filters = filters.find_one({"chat_id": chat_id})
    if _filters:
        filters.delete_one({"chat_id": chat_id})
        return True
    return False


def get_total_filters():
    _chats = filters.find({})
    _total = 0
    for x in _chats:
        _total += len(x["filters"])
    return _total
