from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
from telebot_clock import Clock, CallbackData
import time


clock = Clock()
clock_1_callback = CallbackData("clock_1", "action", "hour", "minute")
telebot_clock = Clock()


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_time"))
def start_time_editor(call):
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
        bot.delete_message(chat_id, call.message.message_id)
    except:
        pass
    
    bot.set_state(call.from_user.id, States.edit_start_time, call.message.chat.id)
    
    start_data = []
    
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
        if data.get("edited_start_time", None) != "":
            start_data.append(data.get("edited_start_time", None).split(':')[0])
            start_data.append(data.get("edited_start_time", None).split(':')[1])
        else:
            start_data.append("12")
            start_data.append("0")
    
    hours = start_data[0]
    minutes = start_data[1]
    
    markup = clock.create_clock(
            name = str(call.from_user.id),
            hour = int(hours),
            minute = int(minutes)
        )
    msg = bot.send_message(
        chat_id,
        "Выберите время начала.\n\nЕсли время отсутствует - нажмите соответствующую кнопку ниже",
        parse_mode='html',
        reply_markup=markup
    )
    
    
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_start_time
)
def start_time_callback(call: CallbackQuery):
    name, action, hour, minute = call.data.split(clock_1_callback.sep)
    date = clock.clock_query_handler(
        bot=bot, call=call, name=name, action=action, hour=int(hour), minute=int(minute)
    )
    if action == "CHOOSE":
        bot.set_state(call.from_user.id, States.edit_start_time_confirmation, call.message.chat.id)
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
        bot.add_data(call.from_user.id, call.message.chat.id, draft_start_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)
    elif action == "NO_TIME":
        bot.set_state(call.from_user.id, States.edit_start_time_confirmation, call.message.chat.id)
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
        bot.add_data(call.from_user.id, call.message.chat.id, draft_start_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_start_time_confirmation
    )
def confirm_start_time(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_start_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        start_time_editor(call)
    elif call.data == 'confirm_start_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        end_time_editor(call)


def end_time_editor(m, *args, **kwargs):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.edit_end_time, chat_id)
    
    start_data = []
    
    with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
        if data.get("edited_end_time", None) != "":
            start_data.append(data.get("edited_end_time", None).split(':')[0])
            start_data.append(data.get("edited_end_time", None).split(':')[1])
        else:
            if data.get("draft_start_time", None) is not None:
                start_data.append(data.get("draft_start_time", None).split(':')[0])
                start_data.append(data.get("draft_start_time", None).split(':')[1])
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
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_end_time
)
def end_time_callback(call: CallbackQuery):
    name, action, hour, minute = call.data.split(clock_1_callback.sep)
    date = clock.clock_query_handler(
        bot=bot, call=call, name=name, action=action, hour=int(hour), minute=int(minute)
    )
    if action == "CHOOSE":
        bot.set_state(call.from_user.id, States.edit_end_time_confirmation, call.message.chat.id)
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
        bot.add_data(call.from_user.id, call.message.chat.id, draft_end_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)
    elif action == "NO_TIME":
        bot.set_state(call.from_user.id, States.edit_end_time_confirmation, call.message.chat.id)
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
        bot.add_data(call.from_user.id, call.message.chat.id, draft_end_time=choosen_time)
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        bot.add_data(call.from_user.id, call.message.chat.id, last_m_id=msg.id)
    
    
@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_end_time_confirmation
    )
def confirm_end_time(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_end_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        end_time_editor(call)
    elif call.data == 'confirm_end_time':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                draft_start_time = data.get("draft_start_time", None)
                draft_end_time = data.get("draft_end_time", None)
                bot.delete_message(call.message.chat.id, last_message)
            bot.add_data(call.from_user.id, chat_id, edited_start_time=draft_start_time, edited_end_time=draft_end_time, event_edited=True)
        except:
            pass
    
    from events_plan.edit_event_module.edit_event import edit_selected_event
    edit_selected_event(call)
