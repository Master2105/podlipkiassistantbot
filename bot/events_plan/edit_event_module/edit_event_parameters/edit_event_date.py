from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time


calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_date"))
def date_editor(call):
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
    
    bot.set_state(call.from_user.id, States.edit_date, call.message.chat.id)
    
    
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
    
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id)
    

@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=States.edit_date
    )
def get_choosen_date(call: CallbackQuery):
        
    name, action, year, month, day = call.data.split(calendar_1_callback.sep)
    
    date = calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    
    if action == "DAY":
        bot.set_state(call.from_user.id, States.edit_date_confirmation, call.message.chat.id)
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
                
        bot.add_data(call.from_user.id, call.message.chat.id, draft_date=date.strftime('%d.%m.%Y'), draft_day_of_week=week_date)
            
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
    state=States.edit_date_confirmation
    )
def confirm_date(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
        
    if call.data == 'back_to_choose_date':
        try:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=call.message.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(call.message.chat.id, last_message)
        except:
            pass
        date_editor(call)
    elif call.data == 'confirm_date':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            draft_date = data.get("draft_date", None)
            draft_day_of_week = data.get("draft_day_of_week", None)
        bot.add_data(call.from_user.id, chat_id, edited_date=draft_date, edited_day_of_week=draft_day_of_week, event_edited=True)
        from events_plan.edit_event_module.edit_event import edit_selected_event
        edit_selected_event(call)
