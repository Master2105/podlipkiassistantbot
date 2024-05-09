import telebot
import secrets
from telebot.storage import StateMemoryStorage, StateRedisStorage


state_storage = StateRedisStorage(
            host='localhost',
            port=6381,
            db=0,
            password=None,
            prefix='telebot_',
        )


bot = telebot.TeleBot(secrets.bot_token, state_storage=state_storage, use_class_middlewares=True)
