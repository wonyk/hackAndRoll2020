def help(update, context):
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="I can help you create, view and manage your Habitica account.\n\nYou can use these commands:"
        + "\n\n*Core functionalities*"
        + "\n/create - create a new habit, todo, daily or reward\n"
        + "/view - view details of your habits, todos, dailies or rewards\n"
        + "/stats - view your Habitica stats"
        + "\n\n*User Profile*"
        + "\n/start - Reset user profile",
        parse_mode="Markdown",
    )