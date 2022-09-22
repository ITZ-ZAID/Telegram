from . import db

couples = db.couple
votes = db.votes_couple_up
v_otes = db.votes_couple_down


def get_couple(chat_id: int, date: str):
    _lovers = couples.find_one({"chat_id": chat_id})
    if not _lovers:
        lovers = {}
    else:
        lovers = _lovers["couple"]
    if date in lovers:
        return lovers[date]
    else:
        return False


def save_couple(chat_id: int, date: str, couple: dict):
    _lovers = couples.find_one({"chat_id": chat_id})
    if not _lovers:
        lovers = {}
    else:
        lovers = _lovers["couple"]
    lovers[date] = couple
    couples.update_one({"chat_id": chat_id}, {"$set": {"couple": lovers}}, upsert=True)


def add_vote_up(event_id: int, user_id: int):
    _votes = votes.find_one({"event_id": event_id})
    if not _votes:
        users = []
    else:
        users = _votes["users"]
    r = users
    r.append(user_id)
    votes.update_one({"event_id": event_id}, {"$set": {"users": r}}, upsert=True)


def rm_vote_up(event_id: int, user_id: int):
    _votes = votes.find_one({"event_id": event_id})
    if not _votes:
        return False
    else:
        users = _votes["users"]
    r = users
    r.remove(user_id)
    votes.update_one({"event_id": event_id}, {"$set": {"users": r}}, upsert=True)


def voted_up(event_id: int, user_id: int):
    _votes = votes.find_one({"event_id": event_id})
    if not _votes:
        return False
    if user_id in _votes["users"]:
        return True
    return False


def add_vote_down(event_id: int, user_id: int):
    _votes = v_otes.find_one({"event_id": event_id})
    if not _votes:
        users = []
    else:
        users = _votes["users"]
    r = users
    r.append(user_id)
    v_otes.update_one({"event_id": event_id}, {"$set": {"users": r}}, upsert=True)


def rm_vote_down(event_id: int, user_id: int):
    _votes = v_otes.find_one({"event_id": event_id})
    if not _votes:
        return False
    else:
        users = _votes["users"]
    r = users
    r.remove(user_id)
    v_otes.update_one({"event_id": event_id}, {"$set": {"users": r}}, upsert=True)


def voted_down(event_id: int, user_id: int):
    _votes = v_otes.find_one({"event_id": event_id})
    if not _votes:
        return False
    if user_id in _votes["users"]:
        return True
    return False
