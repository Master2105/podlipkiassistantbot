from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_seniors"))
def seniors_editor(call):
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
    
    bot.set_state(call.from_user.id, States.edit_seniors, call.message.chat.id)
    
    
    msg = bot.send_message(chat_id, "Ответственные лица. Напишите всех ответственных через запятую в формате Фамилия И.О.", parse_mode='html')
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)


@bot.message_handler(
    is_events_plan_menu=False,
    is_back_button_filter=False,
    is_cancel_button_filter=False,
    state=States.edit_seniors
    )
def seniors_callback(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    bot.set_state(m.from_user.id, States.edit_seniors_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_seniors')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_seniors')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, draft_seniors=m.text)
    
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
    state=States.edit_seniors_confirmation
    )
def seniors_confirmation(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_seniors':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        seniors_editor(call)
    elif call.data == 'confirm_seniors':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            draft_seniors = data.get("draft_seniors", None)
    
        bot.add_data(call.from_user.id, chat_id, edited_seniors=draft_seniors)
        
        from events_plan.edit_event_module.edit_event import edit_selected_event
        edit_selected_event(call)
