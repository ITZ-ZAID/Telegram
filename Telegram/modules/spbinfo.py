from Telegram.modules.helper_funcs.extraction import extract_user
from Telegram.modules.helper_funcs.decorators import zaid
import requests, telegram, datetime, time


@zaid(command="spbinfo")
def lookup(update, context):
    message = update.effective_message
    args = context.args
    user_id = extract_user(message, args)
    if user_id is None:
        user_id = update.effective_user.id
    url = f"https://api.intellivoid.net/spamprotection/v1/lookup?query={user_id}"
    #print(url)
    r = requests.get(url)
    a = r.json()
    #print(a)
    response = a.get('success')
    if response is True:
        date = a.get("results").get("last_updated")
        stats = '**◢ Intellivoid• SpamProtection Info**:\n'
        stats += f' • **Updated on**: `{datetime.datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S %p")}`\n'
        stats += (
            f" • **Chat Info**: [Link](t.me/SpamProtectionBot/?start=00_{user_id})\n"
        )

        if a.get("results").get("attributes").get("is_potential_spammer") is True:
            stats += ' • *User*: `USERxSPAM`\n'
        elif a.get("results").get("attributes").get("is_operator") is True:
            stats += ' • *User*: `USERxOPERATOR`\n'
        elif a.get("results").get("attributes").get("is_agent") is True:
            stats += ' • *User*: `USERxAGENT`\n'
        elif a.get("results").get("attributes").get("is_whitelisted") is True:
            stats += ' • *User*: `USERxWHITELISTED`\n'

        stats += f' • *Type*: `{a.get("results").get("entity_type")}`\n'
        stats += (
            f' • *Language*: `{a.get("results").get("language_prediction").get("language")}`\n'
        )
        stats += f' • *Language Probability*: `{a.get("results").get("language_prediction").get("probability")}`\n'
        stats += '*Spam Prediction*:\n'
        stats += f' • *Ham Prediction*: `{a.get("results").get("spam_prediction").get("ham_prediction")}`\n'
        stats += f' • *Spam Prediction*: `{a.get("results").get("spam_prediction").get("spam_prediction")}`\n'
        stats += f'*Blacklisted*: `{a.get("results").get("attributes").get("is_blacklisted")}`\n'
        if a.get("results").get("attributes").get("is_blacklisted") is True:
            stats += (
                f' • *Reason*: `{a.get("results").get("attributes").get("blacklist_reason")}`\n'
            )
            stats += f' • *Flag*: `{a.get("results").get("attributes").get("blacklist_flag")}`\n'
        stats += f'*PTID*:\n`{a.get("results").get("private_telegram_id")}`\n'
        message.reply_text(stats, parse_mode=telegram.ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
        message.reply_text("`cannot reach SpamProtection API`", parse_mode=telegram.ParseMode.MARKDOWN)
        time.sleep(3)
