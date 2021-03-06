from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
from job import set_reminders

SET_USERNAME, SET_USERPASS = range(2)
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"


def start(update, context):
    update.message.reply_sticker(_start_sticker)
    update.message.reply_markdown(
        "Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to identify yourself?"
        "\n\nPlease key in your Habitica username or email:",
    )
    return SET_USERNAME


# Function linked to SET_USERNAME or redirect if login fails
def get_username(update, context):
    username = update.message.text
    update.message.reply_markdown(
        "Username / Email set: *"
        + username
        + "*\n\nNext, please key in your Habitica Password:"
        "\n\nTo restart: /restart",
    )
    context.chat_data["username"] = username
    return SET_USERPASS


# Function linked to SET_USERPASS
def get_userpass(update, context):
    password = update.message.text
    update.message.delete()
    update.message.reply_text("Password entered successfully. Logging you in...",)
    res = api.login(context.chat_data["username"], password)
    # res will return in the following formats:
    # 1. False - Server Error
    # 2. {'success': True, 'data': {...}} for correct logins
    # 3. {'success': False} for incorrect auth

    if res == False:
        update.message.reply_text(
            "The server encountered an error. Please try again later.",
        )
        return ConversationHandler.END
    elif res["success"] == True:
        update.message.reply_sticker(_reward_sticker)
        update.message.reply_markdown(
            "*Welcome to Rhabbitica*, _"
            + res["data"]["username"]
            + "_\nYou may start enjoying Rhabbitica's functions now!"
            "\n\nTo get started: /help",
        )
        # Init the hourly reminders
        set_reminders(update, context)
        return ConversationHandler.END
    else:
        update.message.reply_markdown(
            "*Your email address / username or password is incorrect. Please try again.*"
            "\n\nPlease key in your Habitica username or email",
        )
        return SET_USERNAME


# Add conversation for init basic data using start
start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SET_USERNAME: [MessageHandler(Filters.text, get_username)],
        SET_USERPASS: [MessageHandler(Filters.text, get_userpass)],
    },
    fallbacks=[CommandHandler("restart", start)],
    allow_reentry=True,
)

