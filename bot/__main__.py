import os
import datetime
import telebot
from telebot import types
import gspread
# import dramatiq
import requests
import time
from time import sleep
from functools import wraps
from accepted_ids import IDs
import events_plan
from events_plan import *
from bot_management import *
import bot_management
import secrets
from secrets import events_sheet_id, users_sheet_id, googledoc_id
from init_bot import bot
import array as arr


FILENAME = "/data/todo.json" if "AMVERA" in os.environ else "todo.json"

gc = gspread.service_account(filename=secrets.path_to_service_json)


def send_action(action):
    def decorator(func):
        @wraps(func)
        def command_func(message, *args, **kwargs):
            bot.send_chat_action(chat_id=message.chat.id, action=action)
            sleep(1)
            return func(message, *args, **kwargs)
        return command_func
    return decorator

@bot.message_handler(commands=['start'])
@send_action('typing')
def check_access(message):
    print("Checking access")
    if message.text == "/start":
        if message.chat.id in IDs.massive or message.chat.id in IDs.roots:
            bot.send_message(message.chat.id, '''Привет! На связи бот-ассистент хоровой школы. Я способен помочь в решении различных повседневных задач. На данный момент доступна только функция управления планом мероприятий. Кнопку перехода к функции Вы можете видеть ниже''', parse_mode='html')
            send_welcome(message)
        else:
            pass
    else:
        bot.send_message(message.chat.id, f'''Нажмите /start''', parse_mode='html')


def send_welcome(message):
    print("Sending welcome message")
    if message.chat.id in IDs.massive:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("План мероприятий")
        markup.add(btn1)
        bot.send_message(message.chat.id, '''Выберите действие''', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, get_calendar)
    elif message.chat.id in IDs.roots:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("План мероприятий")
        btn2 = types.KeyboardButton("Управление ботом")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, '''Выберите действие''', parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, management_fork)


try:
    bot.enable_save_next_step_handlers(delay=2)
    bot.load_next_step_handlers()
except:
    pass
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
