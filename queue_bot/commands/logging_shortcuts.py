
def log_queue(update, bot, message):
    return f"Queue> {bot.get_queue()} User> {bot.registered.get_user_by_update(update)}: '{message}'"


def log_user(update, bot, message):
    return f"user {bot.registered.get_user_by_update(update)} : {message}"
