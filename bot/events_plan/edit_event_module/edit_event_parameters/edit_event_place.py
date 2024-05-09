from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_place"))
def place_editor(call):
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
    edit_place(call)
    

@bot.callback_query_handler(func=lambda call: True, state=States.edit_place)
def edit_place(call):    
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    
    bot.set_state(call.from_user.id, States.edit_place, chat_id)
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
            bot.set_state(call.from_user.id, States.edit_another_place, chat_id)
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
            
            bot.set_state(call.from_user.id, States.edit_place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, draft_place=room_event)
            
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

            bot.set_state(call.from_user.id, States.edit_place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, draft_place=room_event)
            
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

            bot.set_state(call.from_user.id, States.edit_place_confirmation, chat_id)
            keyboard = types.InlineKeyboardMarkup()
            button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
            button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
            keyboard.add(button_yes, button_no)
            
            bot.add_data(call.from_user.id, chat_id, draft_place=room_event)
            
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
    state=States.edit_another_place
    )
def edit_another_place(m): 
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
    
    bot.set_state(m.from_user.id, States.edit_place_confirmation, chat_id)
    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton('Подтвердить', callback_data='confirm_place')
    button_no = types.InlineKeyboardButton('Изменить', callback_data='back_to_choose_place')
    keyboard.add(button_yes, button_no)
    
    bot.add_data(m.from_user.id, chat_id, draft_place=room_event)
    
    msg = bot.send_message(
        chat_id=chat_id,
        text=f"<b>Выбранное помещение:</b>\n\n{room_event}", parse_mode='html',
        reply_markup=keyboard,
    )
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)
    
    
@bot.callback_query_handler(
    func=lambda call: True,
    state=States.edit_place_confirmation
    )
def edit_place_confirmation(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    if call.data == 'back_to_choose_place':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except Exception as e:
            print(e)
        edit_place(call)
    elif call.data == 'confirm_place':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
            last_message = data.get("last_m_id", None)
            draft_place = data.get("draft_place", None)
            bot.delete_message(call.message.chat.id, last_message)
        bot.add_data(call.from_user.id, chat_id, edited_place=draft_place, event_edited=True)
    
        from events_plan.edit_event_module.edit_event import edit_selected_event
        edit_selected_event(call)
