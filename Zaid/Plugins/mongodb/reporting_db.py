from . import db

report = db.reporting


def chat_should_report(chat_id):
    chat_setting = report.find_one({"chat_id": chat_id})
    if chat_setting:
        return chat_setting.get("mode")
    return False


def set_chat_setting(chat_id, setting):
    report.update_one({"chat_id": chat_id}, {"$set": {"mode": setting}}, upsert=True)
