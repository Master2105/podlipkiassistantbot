from telebot import types
from accepted_ids import IDs
import gspread
import dramatiq
import requests
import secrets
from secrets import events_sheet_id
from init_bot import bot
from record_event import *
import array as arr 


@bot.message_handler(func=lambda message: message.text.lower() == "план мероприятий")
def get_calendar(message):
    print("get_calendar")
    if message.chat.id in IDs.admins or message.chat.id in IDs.roots:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Посмотреть план")
        btn2 = types.KeyboardButton("Создать мероприятие")
        # btn3 = types.KeyboardButton("Редактировать мероприятие")
        # btn4 = types.KeyboardButton("Удалить мероприятие")
        btn5 = types.KeyboardButton("В главное меню")
        markup.add(btn1, btn2, btn5)
        bot.send_message(message.chat.id, "Выберите действие", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, plan_redactor)
    elif message.chat.id in IDs.preps:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Посмотреть план")
        btn2 = types.KeyboardButton("Создать мероприятие")
        # btn3 = types.KeyboardButton("Редактировать мероприятие")
        # btn4 = types.KeyboardButton("Удалить мероприятие")
        btn5 = types.KeyboardButton("В главное меню")
        markup.add(btn1, btn2, btn5)
        bot.send_message(message.chat.id, "Выберите действие", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, plan_redactor)
    # else:
    #     bot.send_message(message.chat.id, f'''Что-то пошло не так. Выберите один из вариантов меню ниже''', parse_mode='html')
    #     bot.register_next_step_handler(message, get_calendar)



def plan_redactor(message):
    print("plan_redactor")
    if message.text.lower() == "посмотреть план":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        open_plan = types.InlineKeyboardButton('Посмотреть план', url='')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(open_plan)
        bot.send_message(message.chat.id, "В данный момент план доступен для просмотра в виде таблицы по ссылке", parse_mode='html', reply_markup=keyboard)
        get_calendar(message)
    elif message.text.lower() == "создать мероприятие":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Подтверждаю")
        btn2 = types.KeyboardButton("Ознакомиться")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Подтвердите, что ознакомились с планом", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, confirmation)
    elif message.text.lower() == "редактировать мероприятие":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Функция скоро будет доступна", parse_mode='html', reply_markup=markup)
        # bot.register_next_step_handler(message, go_back)
    elif message.text.lower() == "удалить мероприятие":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Назад")
        markup.add(btn1)
        bot.send_message(message.chat.id, "Функция скоро будет доступна", parse_mode='html', reply_markup=markup)
        # bot.register_next_step_handler(message, go_back)
    elif message.text.lower() == "в главное меню":
        from __main__ import send_welcome
        send_welcome(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        from __main__ import check_access
        check_access(message)
    else:
        bot.send_message(message.chat.id, f'''Что-то пошло не так. Выберите один из вариантов меню ниже''', parse_mode='html')
        bot.register_next_step_handler(message, plan_redactor)


def confirmation(message):
    print("confirmation")
    if message.text.lower() == "подтверждаю":
        from record_event import event_data
        if event_data == []:
            user_id = message.chat.id
            event_data.append(user_id)
            print(f"{user_id} started record")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Назад к плану")
            markup.add(btn1)
            bot.send_message(message.chat.id, "Напишите полное название мероприятия", parse_mode='html', reply_markup=markup)
            bot.register_next_step_handler(message, get_name)
        else:
            bot.send_message(message.chat.id, "План заполняется другим пользователем. Попробуйте через несколько минут", parse_mode='html')
            get_calendar(message)
    elif message.text.lower() == "ознакомиться":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        open_plan = types.InlineKeyboardButton('Посмотреть план', url='')
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(open_plan)
        bot.send_message(message.chat.id, "В данный момент план доступен для просмотра в виде таблицы по ссылке", parse_mode='html', reply_markup=keyboard)
        get_calendar(message)
    else:
        bot.send_message(message.chat.id, f'''Пожалуйста, используйте кнопки''', parse_mode='html')
        bot.register_next_step_handler(message, confirmation)


@bot.message_handler(func=lambda message: message.text.lower() == "в главное меню")
def go_to_main(message):
    print("go_to_main in events_plan")
    from __main__ import send_welcome
    send_welcome(message)
