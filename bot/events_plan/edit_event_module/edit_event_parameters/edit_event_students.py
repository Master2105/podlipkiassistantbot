from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_students"))
def students_editor(call):
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
    
    bot.set_state(call.from_user.id, States.edit_students, call.message.chat.id)
    
    
    button_nope = types.InlineKeyboardButton('Учащихся нет', callback_data='no_students')
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_nope)
    
    msg = bot.send_message(call.from_user.id, "Количество учащихся. Напишите только число.\nЕсли информация отсутствует - нажмите кнопку ниже", parse_mode='html', reply_markup=keyboard)
    
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)


@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_students
    )
def no_students_callback(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'no_students':
        bot.set_state(call.from_user.id, States.edit_students_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_students')
        button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_students')
        keyboard.add(button_yes, button_no)
        
        bot.add_data(call.from_user.id, chat_id, draft_students="")
        
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
    state=States.edit_students
    )
def count_students_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.edit_students_confirmation, chat_id)
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
    
    bot.add_data(m.from_user.id, chat_id, draft_students=count[0])
    
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
    state=States.edit_students_confirmation
    )
def students_confirmation(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_students':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        students_editor(call)
    elif call.data == 'confirm_students':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            draft_students = data.get("draft_students", None)
    
        bot.add_data(call.from_user.id, chat_id, edited_count_students=draft_students, event_edited=True)
        
        from events_plan.edit_event_module.edit_event import edit_selected_event
        edit_selected_event(call)
