from . import db

notes = db.note_s
pnotes = db.private_notes


def save_note(chat_id, name, note, id=None, hash=None, reference=None, type=None):
    name = name.lower().strip()
    _note = notes.find_one({"chat_id": chat_id})
    if not _note:
        _notes = {}
    else:
        _notes = _note["notes"]
    _notes[name] = {
        "note": note,
        "id": id,
        "hash": hash,
        "ref": reference,
        "mtype": type,
    }
    notes.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)


def delete_note(chat_id, name):
    name = name.strip().lower()
    _note = notes.find_one({"chat_id": chat_id})
    if not _note:
        _notes = {}
    else:
        _notes = _note["notes"]
    if name in _notes:
        del _notes[name]
        notes.update_one({"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True)


def get_note(chat_id, name):
    name = name.strip().lower()
    _note = notes.find_one({"chat_id": chat_id})
    if not _note:
        _notes = {}
    else:
        _notes = _note["notes"]
    if name in _notes:
        return _notes[name]
    return False


def get_all_notes(chat_id):
    _note = notes.find_one({"chat_id": chat_id})
    if _note:
        return _note["notes"]
    return None


def delete_all_notes(chat_id):
    _note = notes.find_one({"chat_id": chat_id})
    if _note:
        notes.delete_one({"chat_id": chat_id})
        return True
    return False


def change_pnotes(chat_id, mode):
    _p = pnotes.find_one({"chat_id": chat_id})
    if not _p:
        return pnotes.insert_one({"chat_id": chat_id, "mode": mode})
    pnotes.update_one({"chat_id": chat_id}, {"$set": {"mode": mode}})


def get_pnotes(chat_id: int):
    _p = pnotes.find_one({"chat_id": chat_id})
    if _p:
        return _p["mode"]
    return False


def get_total_notes():
    _notes = notes.find({})
    _total = 0
    for x in _notes:
        _total += len(x["notes"])
    return _total
