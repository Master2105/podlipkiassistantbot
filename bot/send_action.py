from telebot import TeleBot
from init_bot import bot
from time import sleep
from functools import wraps


def send_action(action, **kwargs):
    def decorator(func):
        @wraps(func)
        def command_func(m, *args, **kwargs):
            try:
                chat_id = m.chat.id
            except:
                chat_id = m.message.chat.id
            bot.send_chat_action(chat_id=chat_id, action=action)
            sleep(1)
            return func(m, *args, **kwargs)
        return command_func
    return decorator
