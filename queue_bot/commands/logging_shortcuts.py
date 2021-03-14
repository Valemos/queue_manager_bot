def log_bot_queue(update, bot, message, *args):
    if bot.check_queue_selected():
        bot.logger.log(f"{bot.get_queue()} by {bot.registered_manager.get_user_by_update(update)}: '"
                       + message.format(*args))
    else:
        log_bot_user(update, bot, message, *args)


def log_bot_user(update, bot, message, *args):
    bot.logger.log(f"user {bot.registered_manager.get_user_by_update(update)} :"
                   + message.format(*args))