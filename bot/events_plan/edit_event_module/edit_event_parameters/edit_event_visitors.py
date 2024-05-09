from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_visitors"))
def visitors_editor(call):
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
    
    bot.set_state(call.from_user.id, States.edit_visitors, call.message.chat.id)
    
    
    button_nope = types.InlineKeyboardButton('Посетителей нет', callback_data='no_visitors')
    
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_nope)
    
    msg = bot.send_message(call.from_user.id, "Количество посетителей. Напишите только число.\nЕсли информация отсутствует - нажмите кнопку ниже", parse_mode='html', reply_markup=keyboard)
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
    
    
@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_visitors
    )
def no_visitors_callback(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'no_visitors':
        bot.set_state(call.from_user.id, States.edit_visitors_confirmation, call.message.chat.id)
        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_visitors')
        button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_visitors')
        keyboard.add(button_yes, button_no)
        
        bot.add_data(call.from_user.id, chat_id, draft_visitors="")
        
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
    state=States.edit_visitors
    )
def count_visitors_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.edit_visitors_confirmation, chat_id)
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
    
    bot.add_data(m.from_user.id, chat_id, draft_visitors=count[0])
    
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
    state=States.edit_visitors_confirmation
    )
def visitors_confirmation(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_visitors':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        visitors_editor(call)
    elif call.data == 'confirm_visitors':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            draft_visitors = data.get("draft_visitors", None)
            
        bot.add_data(call.from_user.id, chat_id, edited_count_visitors=draft_visitors, event_edited=True)
            
        from events_plan.edit_event_module.edit_event import edit_selected_event
        edit_selected_event(call)
