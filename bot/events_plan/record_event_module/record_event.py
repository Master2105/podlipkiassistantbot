import datetime
from telebot import types
from telebot.types import CallbackQuery
import gspread
import gspread_formatting
import requests
import secrets
from init_bot import bot
from bot_states import *
from send_action import send_action
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot_clock import Clock, CallbackData
import sqlite3 as sl
from datetime import datetime
import time
from secrets import db


calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


clock = Clock()
clock_1_callback = CallbackData("clock_1", "action", "hour", "minute")
telebot_clock = Clock()


@bot.message_handler(
    is_new_event_confirmed=True,
    state=States.record_new_event
    )
def record_new_event(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    
    bot.set_state(m.from_user.id, States.record_new_event_confirmed, chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    btn2 = types.KeyboardButton("Отменить запись")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(chat_id, "Запись мероприятия начата", parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, rec_msg_id=msg.id, userid=m.from_user.id)
    
    get_title(m)
    
    
def get_title(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    bot.set_state(m.from_user.id, States.record_event_title, chat_id)
    msg = bot.send_message(chat_id, "Напишите полное название мероприятия.\n\n❗️Обратите внимание: если мероприятие длится несколько дней - в конце названия укажите диапазон дат в скобках в формате (с ... по ...)", parse_mode='html')
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, title=None)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.record_event_title
    )
def title_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.title_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_title')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_record_title')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, title=m.text)

    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Название</b>:\n\n{m.text}", parse_mode='html',
        reply_markup=keyboard,
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.title_confirmation
    )
def title_confirmation(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    if m.data == 'back_to_record_title':
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(chat_id, last_message)
        except Exception as e:
            print(e)
        get_title(m)
    elif m.data == 'confirm_title':
        get_date(m)


def get_date(m, *args, **kwargs):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    bot.set_state(m.from_user.id, States.record_event_date, chat_id)
    
    now = datetime.now()
    msg = bot.send_message(
        chat_id,
        "Выберите дату мероприятия.\n\n❗️Обратите внимание: если мероприятие длится несколько дней - укажите начальную дату",
        parse_mode='html',
        reply_markup=calendar.create_calendar(
            name=calendar_1_callback.prefix,
            year=now.year,
            month=now.month,
        ),
    )
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, date=None, day_of_week=None)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=States.record_event_date
    )
def get_choosen_date(call: CallbackQuery):
        
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    
    if action == "DAY":
        if date.strftime('%Y.%m') < datetime.today().strftime("%Y.%m"):
            tmp = bot.send_message(
            call.from_user.id,
            "❗️ Вы пытаетесь выбрать дату прошедшего месяца",
            parse_mode='html'
            )
            time.sleep(3)
            bot.delete_message(call.message.chat.id, tmp.id)
        else:
            bot.set_state(call.from_user.id, States.date_event_confirmation, call.message.chat.id)
            
            week_date_number = datetime(int(date.strftime('%Y')), int(date.strftime('%m')), int(date.strftime('%d'))).weekday()
            
            if week_date_number == 0:
                week_date = "Пн"
            elif week_date_number == 1:
                week_date = "Вт"
            elif week_date_number == 2:
                week_date = "Ср"
            elif week_date_number == 3:
                week_date = "Чт"
            elif week_date_number == 4:
                week_date = "Пт"
            elif week_date_number == 5:
                week_date = "Сб"
            elif week_date_number == 6:
                week_date = "Вс"
                    
            bot.add_data(call.from_user.id, call.message.chat.id, date=date.strftime('%d.%m.%Y'), day_of_week=week_date)
                
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_date')
            button_no = types.InlineKeyboardButton('Выбрать другую', callback_data='back_to_choose_date')
            keyboard.add(button_yes, button_no)
            
            msg = bot.send_message(
                chat_id=call.from_user.id,
                text=f"<b>Выбранная дата</b>:\n\n{date.strftime('%d.%m.%Y')}", parse_mode='html',
                reply_markup=keyboard,
            )
            try:
                with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                    last_message = data.get("last_m_id", None)
                    bot.delete_message(call.message.chat.id, last_message)
            except:
                pass
            bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.date_event_confirmation
    )
def confirm_date(call):
    if call.data == 'back_to_choose_date':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        get_date(call)
    elif call.data == 'confirm_date':
        clear_visitors_message(call)


def get_start_time(m, *args, **kwargs):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    bot.set_state(m.from_user.id, States.record_event_start_time, chat_id)
    
    markup = clock.create_clock(
            name = str(m.from_user.id),
            hour = int(12),
            minute = int(00)
        )
    msg = bot.send_message(
        chat_id,
        "Выберите время начала.\n\nЕсли время отсутствует - нажмите соответствующую кнопку ниже",
        parse_mode='html',
        reply_markup=markup
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, start_time=None)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.record_event_start_time
)
def start_time_callback(call: CallbackQuery):
    name, action, hour, minute = call.data.split(clock_1_callback.sep)
    date = clock.clock_query_handler(
        bot=bot, call=call, name=name, action=action, hour=int(hour), minute=int(minute)
    )
    if action == "CHOOSE":
        bot.set_state(call.from_user.id, States.start_time_event_confirmation, call.message.chat.id)
        hour = int(call.data.split(clock_1_callback.sep)[2])
        minute = int(call.data.split(clock_1_callback.sep)[3])
        if hour < 10:
            hour = f"0{hour}"
        if minute < 10:
            minute = f"0{minute}"
        
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_start_time')
        button_no = types.InlineKeyboardButton('Изменить время', callback_data='back_to_choose_start_time')
        keyboard.add(button_yes, button_no)
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text=f"<b>Выбранное время:</b>\n\n{hour}:{minute}", parse_mode='html',
            reply_markup=keyboard
        )
        choosen_time = f"{hour}:{minute}"
        bot.add_data(call.from_user.id, call.message.chat.id, start_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)
    elif action == "NO_TIME":
        bot.set_state(call.from_user.id, States.start_time_event_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_start_time')
        button_no = types.InlineKeyboardButton('Изменить время', callback_data='back_to_choose_start_time')
        keyboard.add(button_yes, button_no)
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text="<b>Время начала отсутствует</b>", parse_mode='html',
            reply_markup=keyboard,
        )
        choosen_time = None
        bot.add_data(call.from_user.id, call.message.chat.id, start_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.start_time_event_confirmation
    )
def confirm_start_time(call):
    if call.data == 'back_to_choose_start_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        get_start_time(call)
    elif call.data == 'confirm_start_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        get_end_time(call)


def get_end_time(m, *args, **kwargs):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.record_event_end_time, chat_id)
    
    start_data = []
    
    with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
        if data.get("start_time", None) is not None:
            start_data.append(data.get("start_time", None).split(':')[0])
            start_data.append(data.get("start_time", None).split(':')[1])
        else:
            start_data.append("12")
            start_data.append("0")
    
    hours = start_data[0]
    minutes = start_data[1]
        
    markup = clock.create_clock(
            name = str(m.from_user.id),
            hour = int(hours),
            minute = int(minutes)
        )
    
    msg = bot.send_message(
        chat_id,
        "Выберите время окончания.\n\nЕсли время отсутствует - нажмите соответствующую кнопку ниже",
        parse_mode='html',
        reply_markup=markup
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, end_time=None)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.record_event_end_time
)
def end_time_callback(call: CallbackQuery):
    name, action, hour, minute = call.data.split(clock_1_callback.sep)
    date = clock.clock_query_handler(
        bot=bot, call=call, name=name, action=action, hour=int(hour), minute=int(minute)
    )
    if action == "CHOOSE":
        bot.set_state(call.from_user.id, States.end_time_event_confirmation, call.message.chat.id)
        hour = int(call.data.split(clock_1_callback.sep)[2])
        minute = int(call.data.split(clock_1_callback.sep)[3])
        if hour < 10:
            hour = f"0{hour}"
        if minute < 10:
            minute = f"0{minute}"
        
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_end_time')
        button_no = types.InlineKeyboardButton('Изменить время', callback_data='back_to_choose_end_time')
        keyboard.add(button_yes, button_no)
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text=f"<b>Выбранное время:</b>\n\n{hour}:{minute}", parse_mode='html',
            reply_markup=keyboard
        )
        choosen_time = f"{hour}:{minute}"
        bot.add_data(call.from_user.id, call.message.chat.id, end_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)
    elif action == "NO_TIME":
        bot.set_state(call.from_user.id, States.end_time_event_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_end_time')
        button_no = types.InlineKeyboardButton('Изменить время', callback_data='back_to_choose_end_time')
        keyboard.add(button_yes, button_no)
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text="<b>Время окончания отсутствует</b>", parse_mode='html',
            reply_markup=keyboard,
        )
        choosen_time = None
        bot.add_data(call.from_user.id, call.message.chat.id, end_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.end_time_event_confirmation
    )
def confirm_end_time(call):
    if call.data == 'back_to_choose_end_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        get_end_time(call)
    elif call.data == 'confirm_end_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        get_students_number(call)


def get_students_number(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
        
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    
    bot.set_state(m.from_user.id, States.record_count_students, chat_id)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.message.chat.id, last_message)
    except:
        pass
    button_nope = types.InlineKeyboardButton('Учащихся нет', callback_data='no_students')
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_nope)
    
    msg = bot.send_message(m.from_user.id, "Количество учащихся. Напишите только число.\nЕсли информация отсутствует - нажмите кнопку ниже", parse_mode='html', reply_markup=keyboard)
    
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, count_students=None)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.record_count_students
    )
def no_students_callback(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'no_students':
        bot.set_state(call.from_user.id, States.students_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_students')
        button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_students')
        keyboard.add(button_yes, button_no)
        
        bot.add_data(call.from_user.id, chat_id, count_students="")
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text="<b>Учащиеся отсутствуют</b>", parse_mode='html',
            reply_markup=keyboard,
        )
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.record_count_students
    )
def count_students_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.students_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_students')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_students')
    keyboard.add(button_yes, button_no)
    
    string = m.text
    count = []
    
    n = ''
    for char in string:
        if '0' <= char <= '9':
            n += char
        else:
            if n != '':
                count.append (int(n))
                n = ''
    if n != '':
        count.append (int(n))    
    
    bot.add_data(m.from_user.id, chat_id, count_students=count[0])
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Количество учащихся:</b>\n\n{count[0]}", parse_mode='html',
        reply_markup=keyboard,
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.students_confirmation
    )
def students_confirmation(call):
    if call.data == 'back_to_choose_students':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        get_students_number(call)
    elif call.data == 'confirm_students':
        get_visitors_number(call)


def get_visitors_number(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.record_count_visitors, chat_id)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
            bot.delete_message(chat_id, m.message_id)
    except:
        pass
    button_nope = types.InlineKeyboardButton('Посетителей нет', callback_data='no_visitors')
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_nope)
    
    msg = bot.send_message(m.from_user.id, "Количество посетителей. Напишите только число.\nЕсли информация отсутствует - нажмите кнопку ниже", parse_mode='html', reply_markup=keyboard)
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, count_visitors=None)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.record_count_visitors
    )
def no_visitors_callback(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'no_visitors':
        bot.set_state(call.from_user.id, States.visitors_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_visitors')
        button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_visitors')
        keyboard.add(button_yes, button_no)
        
        bot.add_data(call.from_user.id, chat_id, count_visitors="")
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text="<b>Посетители отсутствуют</b>", parse_mode='html',
            reply_markup=keyboard,
        )
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.record_count_visitors
    )
def count_visitors_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.visitors_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_visitors')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_visitors')
    keyboard.add(button_yes, button_no)
    
    string = m.text
    count = []
    
    n = ''
    for char in string:
        if '0' <= char <= '9':
            n += char
        else:
            if n != '':
                count.append (int(n))
                n = ''
    if n != '':
        count.append (int(n)) 
    
    bot.add_data(m.from_user.id, chat_id, count_visitors=count[0])
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Количество посетителей:</b>\n\n{count[0]}", parse_mode='html',
        reply_markup=keyboard,
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.visitors_confirmation
    )
def visitors_confirmation(call):
    if call.data == 'back_to_choose_visitors':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        get_visitors_number(call)
    elif call.data == 'confirm_visitors':
        get_equipment(call)


def clear_visitors_message(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    try:
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, call.message_id)
    except:
        pass
    get_place(call)


@bot.callback_query_handler(func=lambda call: True, state=States.record_place)
def get_place(call):    
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    
    bot.set_state(call.from_user.id, States.record_place, chat_id)
    try:        
        if call.data == 'halls':
            keyboard = types.InlineKeyboardMarkup()
            
            keyboard.row(types.InlineKeyboardButton('Концертный зал', callback_data='hall_concert'))
            keyboard.row(types.InlineKeyboardButton('Органный зал', callback_data='hall_organ'))
            keyboard.row(types.InlineKeyboardButton('Назад', callback_data='to_all_rooms'))

            bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=chat_id, message_id=call.message.message_id)
            
        elif call.data == 'rooms' or call.data == 'to_floors':
            keyboard = types.InlineKeyboardMarkup()
            
            keyboard.row(types.InlineKeyboardButton('Первый этаж', callback_data='floor_1'))
            keyboard.row(types.InlineKeyboardButton('Второй этаж', callback_data='floor_2'))
            keyboard.row(types.InlineKeyboardButton('Назад', callback_data='to_all_rooms'))

            bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=chat_id, message_id=call.message.message_id)
            
        elif call.data == 'floor_1':
            keyboard = types.InlineKeyboardMarkup()
            
            ff_104_button = types.InlineKeyboardButton('104 кабинет', callback_data='room_104')
            ff_105_button = types.InlineKeyboardButton('105 кабинет', callback_data='room_105')
            ff_106_button = types.InlineKeyboardButton('106 кабинет', callback_data='room_106')
            ff_107_button = types.InlineKeyboardButton('107 кабинет', callback_data='room_107')
            ff_108_button = types.InlineKeyboardButton('108 кабинет', callback_data='room_108')
            ff_109_button = types.InlineKeyboardButton('109 кабинет', callback_data='room_109')
            ff_110_button = types.InlineKeyboardButton('110 кабинет', callback_data='room_110')
            ff_111_button = types.InlineKeyboardButton('111 кабинет', callback_data='room_111')
            ff_112_button = types.InlineKeyboardButton('112 кабинет', callback_data='room_112')
            ff_113_button = types.InlineKeyboardButton('113 кабинет', callback_data='room_113')

            keyboard.add(ff_104_button, ff_105_button, ff_106_button, ff_107_button, ff_108_button, ff_109_button, ff_110_button, ff_111_button, ff_112_button, ff_113_button)

            keyboard.row(types.InlineKeyboardButton('Назад', callback_data='to_floors'))

            bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=chat_id, message_id=call.message.message_id)
            
        elif call.data == 'floor_2':
            keyboard = types.InlineKeyboardMarkup()
            
            sf_201_button = types.InlineKeyboardButton('201 кабинет', callback_data='room_201')
            sf_202_button = types.InlineKeyboardButton('202 кабинет', callback_data='room_202')
            sf_203_button = types.InlineKeyboardButton('203 кабинет', callback_data='room_203')
            sf_204_button = types.InlineKeyboardButton('204 кабинет', callback_data='room_204')
            sf_205_button = types.InlineKeyboardButton('205 кабинет', callback_data='room_205')
            sf_206_button = types.InlineKeyboardButton('206 кабинет', callback_data='room_206')
            sf_207_button = types.InlineKeyboardButton('207 кабинет', callback_data='room_207')
            sf_209_button = types.InlineKeyboardButton('209 кабинет', callback_data='room_209')
            sf_210_button = types.InlineKeyboardButton('210 кабинет', callback_data='room_210')
            sf_211_button = types.InlineKeyboardButton('211 кабинет', callback_data='room_211')
            sf_212_button = types.InlineKeyboardButton('212 кабинет', callback_data='room_212')
            sf_213_button = types.InlineKeyboardButton('213 кабинет', callback_data='room_213')
            sf_214_button = types.InlineKeyboardButton('214 кабинет', callback_data='room_214')
            sf_215_button = types.InlineKeyboardButton('215 кабинет', callback_data='room_215')
            sf_216_button = types.InlineKeyboardButton('216 кабинет', callback_data='room_216')

            keyboard.add(sf_201_button, sf_202_button, sf_203_button, sf_204_button, sf_205_button, sf_206_button, sf_207_button, sf_209_button, sf_210_button, sf_211_button, sf_212_button, sf_213_button, sf_214_button, sf_215_button, sf_216_button)
            
            keyboard.row(types.InlineKeyboardButton('Назад', callback_data='to_floors'))

            bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=chat_id, message_id=call.message.message_id)
            
        elif call.data == 'to_all_rooms':
            button_halls = types.InlineKeyboardButton('Залы', callback_data='halls')
            button_rooms = types.InlineKeyboardButton('Кабинеты', callback_data='rooms')
            button_another_place = types.InlineKeyboardButton('Другое место', callback_data='another_place')

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_halls, button_rooms, button_another_place)
            
            bot.edit_message_reply_markup(reply_markup=keyboard, chat_id=chat_id, message_id=call.message.message_id)
            
        elif call.data == 'another_place':
            try:
                chat_id = call.chat.id
            except:
                chat_id = call.message.chat.id
            bot.set_state(call.from_user.id, States.another_place, chat_id)
            try:
                with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
                    last_message = data.get("last_m_id", None)
                    bot.delete_message(call.message.chat.id, last_message)
            except:
                pass
            msg = bot.send_message(chat_id, "Напишите место", parse_mode='html')
            bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
            
        elif call.data == 'hall_concert':
            room_event = 'Концертный зал'
            
            bot.set_state(call.from_user.id, States.place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, place=room_event)
            
            msg = bot.send_message(
                chat_id=chat_id,
                text=f"<b>Выбранное помещение:</b>\n\n{room_event}", parse_mode='html',
                reply_markup=keyboard,
            )
            try:
                with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
                    last_message = data.get("last_m_id", None)
                    bot.delete_message(chat_id, last_message)
            except:
                pass
            bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
            
        elif call.data == 'hall_organ':
            room_event = 'Органный зал'

            bot.set_state(call.from_user.id, States.place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, place=room_event)
            
            msg = bot.send_message(
                chat_id=chat_id,
                text=f"<b>Выбранное помещение:</b>\n\n{room_event}", parse_mode='html',
                reply_markup=keyboard,
            )
            try:
                with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
                    last_message = data.get("last_m_id", None)
                    bot.delete_message(chat_id, last_message)
            except:
                pass
            bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
            
        elif call.data.split('_')[0] == 'room':
            room_event = str('Кабинет ') + call.data.split('_')[1]

            bot.set_state(call.from_user.id, States.place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, place=room_event)
            
            msg = bot.send_message(
                chat_id=chat_id,
                text=f"<b>Выбранное помещение:</b>\n\n{room_event}", parse_mode='html',
                reply_markup=keyboard,
            )
            try:
                with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
                    last_message = data.get("last_m_id", None)
                    bot.delete_message(chat_id, last_message)
            except:
                pass
            bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
            
        else:
            button_halls = types.InlineKeyboardButton('Залы', callback_data='halls')
            button_rooms = types.InlineKeyboardButton('Кабинеты', callback_data='rooms')
            button_another_place = types.InlineKeyboardButton('Другое место', callback_data='another_place')

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(button_halls, button_rooms, button_another_place)

            msg = bot.send_message(chat_id, "Выберите помещение", parse_mode='html', reply_markup=keyboard)
            bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
    except:
        keyboard = types.InlineKeyboardMarkup()
        
        keyboard.add(types.InlineKeyboardButton('Залы', callback_data='halls'))
        keyboard.add(types.InlineKeyboardButton('Кабинеты', callback_data='rooms'))
        keyboard.add(types.InlineKeyboardButton('Другое место', callback_data='another_place'))

        msg = bot.send_message(chat_id, "Выберите помещение", parse_mode='html', reply_markup=keyboard)
        bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id, place=None)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.another_place
    )
def another_place_record(m): 
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
        
    room_event = m.text
    
    bot.set_state(m.from_user.id, States.place_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, place=room_event)
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Выбранное помещение:</b>\n\n{room_event}", parse_mode='html',
        reply_markup=keyboard,
    )
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.place_confirmation
    )
def place_confirmation(call):
    if call.data == 'back_to_choose_place':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        get_place(call)
    elif call.data == 'confirm_place':
        get_start_time(call)


def get_equipment(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.record_equipment, chat_id)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    button_nope = types.InlineKeyboardButton('Оборудование не требуется', callback_data='no_equipment')
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_nope)
    
    msg = bot.send_message(chat_id, "Требуемое оборудование. Напишите всё необходимое через запятую\nЕсли оборудование не требуется, нажмите соответствующую кнопку ниже", parse_mode='html', reply_markup=keyboard)
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, equipment=None)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.record_equipment
    )
def no_equipment_callback(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'no_equipment':
        bot.set_state(call.from_user.id, States.eqipment_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_equipment')
        button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_equipment')
        keyboard.add(button_yes, button_no)
        
        bot.add_data(call.from_user.id, chat_id, equipment="")
        
        msg = bot.send_message(
            chat_id=call.from_user.id,
            text="<b>Оборудование не требуется</b>", parse_mode='html',
            reply_markup=keyboard,
        )
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.record_equipment
    )
def equipment_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.eqipment_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_equipment')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_equipment')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, equipment=m.text)
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Оборудование:</b>\n\n{m.text}", parse_mode='html',
        reply_markup=keyboard,
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.eqipment_confirmation
    )
def eqipment_confirmation(call):
    if call.data == 'back_to_choose_equipment':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        get_equipment(call)
    elif call.data == 'confirm_equipment':
        get_seniors(call)
    
    
def get_seniors(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.record_seniors, chat_id)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    
    msg = bot.send_message(chat_id, "Ответственные лица. Напишите всех ответственных через запятую в формате Фамилия И.О.", parse_mode='html')
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, seniors=None)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.record_seniors
    )
def seniors_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.seniors_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_seniors')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_seniors')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, seniors=m.text)
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Ответственные:</b>\n\n{m.text}", parse_mode='html',
        reply_markup=keyboard,
    )
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.seniors_confirmation
    )
def seniors_confirmation(call):
    if call.data == 'back_to_choose_seniors':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        get_seniors(call)
    elif call.data == 'confirm_seniors':
        record(call)


@send_action('typing')
def record(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    
    # Запись в бд. ИЗМЕНИТЬ
    with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
        user_id = data.get("userid", None)
        title = data.get("title", None)
        day_of_week = data.get("day_of_week", None)
        date = data.get("date", None)
        if data.get("start_time", None) != None:
            start_time = data.get("start_time", None)
        else:
            start_time = ""
        if data.get("end_time", None) != None:
            end_time = data.get("end_time", None)
        else:
            end_time = ""
        count_students = data.get("count_students", None)
        count_visitors = data.get("count_visitors", None)
        place = data.get("place", None)
        equipment = data.get("equipment", None)
        seniors = data.get("seniors", None)
        operation_type = "INSERT"
        
        con = sl.connect(db)
        sql_rec = 'INSERT INTO events (user_id, record_datetime, title, day_of_week, date, start_time, end_time, count_students, count_visitors, place, equipment, seniors, operation_type) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING *;'
        with con:
            try:
                cursor = con.cursor()
                cursor.execute(sql_rec, (user_id, datetime.now(), title, day_of_week, date, start_time, end_time, count_students, count_visitors, place, equipment, seniors, operation_type))
                row = cursor.fetchone()
            except Exception as e:
                print(e)
        
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
                rec_message = data.get("rec_msg_id", None)
                bot.delete_message(chat_id, rec_message)
        except:
            pass
        
        if start_time is None:
            start_time = ""
        if end_time is None:
            end_time = ""
        if equipment is None:
            equipment = ""
        
        
            
        try:
            # # добавление записи в таблицу
            # sh = gc.open_by_key(events_sheet_id)
            # next_row = len(sh.sheet1.get_all_values()) + 1

            # sh.sheet1.update(f'A{next_row}:L{next_row}', [[event_data[0], f"{datetime.datetime.now()}", event_data[2], event_data[2], event_data[3], event_data[4], event_data[1], event_data[5], event_data[6], event_data[7], event_data[8], event_data[9]]])
            
            
            #Текущий юзер
            try:
                bot.send_message(chat_id, f"<b>Мероприятие добавлено</b>\n\n<b>Дата:</b> <code>{date}</code>\n<b>Время:</b> <code>{start_time}</code> - <code>{end_time}</code>\n\n<b>Мероприятие:</b> <code>{title}</code>\n\n<b>Место:</b> <code>{place}</code>\n\n<b>Оборудование:</b> <code>{equipment}</code>\n\n<b>Количество учащихся:</b> <code>{count_students}</code>\n\n<b>Количество посетителей:</b> <code>{count_visitors}</code>\n\n<b>Ответственные:</b> <code>{seniors}</code>", parse_mode='html')
                
                sql = ""
                data = ()
                msg_text = ""
                
                msg_text += f"<b>Мероприятия {date}</b>\n\n\n"
                sql = """SELECT * FROM events WHERE date = ? ORDER BY date, start_time"""
                data = (date, )
                cursor.execute(sql, data)
                events = cursor.fetchall()
                
                if len(events) == 0:
                    pass
                else:
                    bot.send_message(chat_id, "Проверьте план на день на наличие задвоений:")
                    
                    for event in events:
                        msg_text += f"<b>Мероприятие:</b> {event[7]}\n<b>Время:</b> {event[5]} - {event[6]}\n<b>Место:</b> {event[10]}\n\n\n\n"
                        
                    keyboard = types.InlineKeyboardMarkup()
                    keyboard.add(types.InlineKeyboardButton('Закрыть', callback_data='close_message'))
                    
                    msg = bot.send_message(chat_id, text=msg_text, parse_mode='html', reply_markup=keyboard)
                    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)
                
            except Exception as e:
                print(e)
                print(f"Невозможно отправить сообщение юзеру {chat_id}")
                bot.send_message(chat_id, f"Не удалось сформировать для Вас подтверждение записи", parse_mode='html')
                bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {user_id}
                <pre> <code class="language-python">   
                {e}
                </code> </pre>""", parse_mode='html')
            
            # Отправка уведомлений администрации
            cursor = con.cursor()
            cursor.execute("""SELECT telegram_id, full_name FROM staff WHERE notifications = 'ALL'""")
            notifications_all = cursor.fetchall()
            for id in notifications_all:
                if chat_id != id[0]:
                    try:
                        bot.send_message(id[0], f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> <code>{date}</code>\n<b>Время:</b> <code>{start_time}</code> - <code>{end_time}</code>\n\n<b>Мероприятие:</b> <code>{title}</code>\n\n<b>Место:</b> <code>{place}</code>\n\n<b>Оборудование:</b> <code>{equipment}</code>\n\n<b>Количество учащихся:</b> <code>{count_students}</code>\n\n<b>Количество посетителей:</b> <code>{count_visitors}</code>\n\n<b>Ответственные:</b> <code>{seniors}</code>", parse_mode='html')
                    except Exception as e:
                        print(e)
                        print(f"Невозможно отправить сообщение пользователю {id[1]}")
                        bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {id[1]}
                        <pre> <code class="language-python">   
                        {e}
                        </code> </pre>""", parse_mode='html')

        except Exception as e:
            print(e)
            print(f"При записи мероприятия {title} в таблицу возникла ошибка {e}")
            bot.send_message(chat_id, f"<b>Возникла непредвиденная ошибка. Информация уже передана разработчикам. Скоро всё поправят</b>", parse_mode='html')
            bot.send_message(102452736, f"При записи мероприятия {title} в таблицу возникла ошибка {e}", parse_mode='html')

    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)
