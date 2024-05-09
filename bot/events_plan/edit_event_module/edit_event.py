from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time
from secrets import db
from events_plan.edit_event_module.edit_event_parameters.edit_event_date import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_equipment import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_place import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_seniors import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_students import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_time import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_title import * 
from events_plan.edit_event_module.edit_event_parameters.edit_event_visitors import *


calendar = Calendar(language=RUSSIAN_LANGUAGE)
calendar_1_callback = CallbackData("calendar_1", "action", "year", "month", "day")


def admin_check(m):        
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    con = sl.connect(db)
    
    with con:
        try:
            info = con.execute('SELECT telegram_id FROM staff WHERE role IN ("root", "admin")').fetchall()
            if any(chat_id == item[0] for item in info):
                return True
            else:
                return False
        except Exception as e:
            print(e)


# Функция получения общего количества мероприятий
def get_count(target_id, target_date):
    con = sl.connect(db)
    cursor = con.cursor()
    sql = ""
    data = ()
    # if target_date == "%":
    # sql = f"""SELECT * FROM events WHERE user_id LIKE ? AND strftime('%m.%Y', date) >= strftime('%m.%Y', date('now', 'localtime')) ORDER BY date, start_time"""
    # data = (target_id)
    # else:
    sql = f"""SELECT * FROM events WHERE user_id LIKE ? AND date LIKE ? ORDER BY date, start_time"""
    data = (target_id, target_date)
    cursor.execute(sql, data, )
    result = cursor.fetchall()
    return result


# Функция для получения данных из базы данных
def get_data(page, items_per_page, target_id, target_date):
    con = sl.connect(db)
    cursor = con.cursor()
    offset = (page - 1) * items_per_page
    # if target_date == "%":
    # sql = f"""SELECT * FROM events WHERE user_id LIKE ? AND strftime('%m.%Y', date) >= date('now', 'localtime') ORDER BY date, start_time LIMIT ? OFFSET ?"""
    # data = (target_id, items_per_page, offset)
    # else:
    sql = f"""SELECT * FROM events WHERE user_id LIKE ? AND date LIKE ? ORDER BY date, start_time LIMIT ? OFFSET ?"""
    data = (target_id, target_date, items_per_page, offset)
    cursor.execute(sql, data)
    result = cursor.fetchall()
    return result


# Функция для создания кнопок навигации
def create_navigation_buttons(page, total_pages, event_index, events, target_date=None):
    
    if target_date == None:
        target_date = "%"
    
    markup = types.InlineKeyboardMarkup()
    numbers = []
    buttons = []
    index = event_index
    for buttonss in enumerate(events):
        numbers.append(types.InlineKeyboardButton(f"[{index}]", callback_data=f"event_{index}_{target_date}"))
        index += 1
    if page > 1:
        buttons.append(types.InlineKeyboardButton("<<", callback_data=f"prev_{page}_{event_index}_{target_date}"))
    if page < total_pages:
        buttons.append(types.InlineKeyboardButton(">>", callback_data=f"next_{page}_{event_index}_{target_date}"))
    markup.row(*numbers)
    markup.row(*buttons)
    if target_date != "%":
        prevous_day_btn = types.InlineKeyboardButton("Предыдущий день", callback_data=f"prevday_{page}_{event_index}_{target_date}")
        next_day_btn = types.InlineKeyboardButton("Следующий день", callback_data=f"nextday_{page}_{event_index}_{target_date}")
        markup.row(prevous_day_btn, next_day_btn)
    return markup

# Обработчик сообщений
@bot.message_handler(is_admin=False, is_edit_event=True, state=States.events_plan)
def look_events_no_admin(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    
    bot.set_state(m.from_user.id, States.choose_looking_period_for_edit, chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    btn2 = types.KeyboardButton("План мероприятий")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(chat_id, "Редактирование мероприятия", parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, edit_msg_id=msg.id, userid=m.from_user.id)
    
    show_events(m)


def show_events(m, date: str = None, *args, **kwargs):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    is_admin_check = admin_check(m)
            
    if is_admin_check==True:
        target_id = "%"
    else:
        target_id = chat_id
        
    if date == None:
        target_date = "%"
    else:
        target_date = date
        
    bot.set_state(m.from_user.id, States.get_events_for_edit, chat_id)
        
    page = 1 # Начальная страница
    items_per_page = 5 # Количество элементов на странице
    event_index = 1

    count = get_count(target_id, target_date)
    
    if len(count) == 0:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Закрыть', callback_data='close_message'))
        
        bot.send_message(chat_id, '''Мероприятия не найдены''', parse_mode='html', reply_markup=keyboard)
    
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
                last_message = data.get("last_m_id", None)
                edit_message = data.get("edit_msg_id", None)
                bot.delete_message(chat_id, last_message)
                bot.delete_message(chat_id, edit_message)
        except:
            pass
        
        try:
            bot.delete_message(chat_id, m.message_id)
        except:
            pass
        
        from events_plan.events_plan_menu import get_calendar
        get_calendar(m)
        return
    
    events = get_data(page, items_per_page, target_id, target_date)
    total_pages = len(count) // items_per_page + (1 if len(count) % items_per_page > 0 else 0)
    markup = create_navigation_buttons(page, total_pages, event_index, events, target_date)
    msg_text = ""
    if date != None:
        msg_text += f"<b>Мероприятия {target_date}</b>\n\n"
    if len(events) != 0:
        msg_text += "<b>Выберите мероприятие для редактирования</b>:\n\n\n"
    for event in events:
        msg_text += f"[{event_index}]\n<b>Мероприятие:</b> {event[7]}\n<b>Дата:</b> {event[4]}\n<b>Время:</b> {event[5]} - {event[6]}\n<b>Помещение:</b> {event[10]}\n<b>Ответственные:</b> {event[12]}\n\n\n"
        event_index += 1
    if len(events) == 0:
        msg_text += "Мероприятий нет"
    msg = bot.send_message(chat_id, text=msg_text, parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(state=States.get_events_for_edit, func=lambda call: call.data.startswith("prev_") or call.data.startswith("next_") or call.data.startswith("prevday_") or call.data.startswith("nextday_"))
def handle_navigation(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
        
    is_admin_check = admin_check(call)
    
    if is_admin_check==True:
        target_id = "%"
    else:
        target_id = chat_id
    
    bot.set_state(call.from_user.id, States.get_events_for_edit, chat_id)
        
    items_per_page = 5 # Количество элементов на странице
    event_index = int(call.data.split("_")[2])

    page = int(call.data.split("_")[1])
    
    target_date = str(call.data.split("_")[3])
        
    if call.data.startswith("prev_"):
        page -= 1
        event_index -= 5
    elif call.data.startswith("next_"):
        page += 1
        event_index += 5
    elif call.data.startswith("prevday_"):
        date = str(call.data.split("_")[3])
        target_date = f"""{int(date.split(".")[0])-1}.{date.split(".")[1]}.{date.split(".")[2]}"""
    elif call.data.startswith("nextday_"):
        date = str(call.data.split("_")[3])
        target_date = f"""{int(date.split(".")[0])+1}.{date.split(".")[1]}.{date.split(".")[2]}"""
    count = get_count(target_id, target_date)
    events = get_data(page, items_per_page, target_id, target_date)
    total_pages = len(count) // items_per_page + (1 if len(count) % items_per_page > 0 else 0)
    markup = create_navigation_buttons(page, total_pages, event_index, events, target_date)
    msg_text = ""
    if target_date != None:
        msg_text += f"<b>Мероприятия {target_date}</b>\n\n"
    if len(events) != 0:
        msg_text += "<b>Выберите мероприятие для редактирования</b>:\n\n\n"
    for event in events:
        msg_text += f"[{event_index}]\n<b>Мероприятие:</b> {event[7]}\n<b>Дата:</b> {event[4]}\n<b>Время:</b> {event[5]} - {event[6]}\n<b>Помещение:</b> {event[10]}\n<b>Ответственные:</b> {event[12]}\n\n\n"
        event_index += 1
    if len(events) == 0:
        msg_text += "Мероприятий нет"
    bot.edit_message_text(text=msg_text, chat_id=chat_id, message_id=call.message.message_id, parse_mode='html', reply_markup=markup)



@bot.message_handler(is_admin=True, is_edit_event=True, state=States.events_plan)
def look_events_admin(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    
    bot.set_state(m.from_user.id, States.choose_looking_period_for_edit, chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    btn2 = types.KeyboardButton("План мероприятий")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(chat_id, "Редактирование мероприятия", parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, edit_msg_id=msg.id, userid=m.from_user.id)
    
    get_events_date_admin(m)



def get_events_date_admin(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
        
    bot.set_state(m.from_user.id, States.get_looking_date_for_edit, chat_id)
    
    now = datetime.now()
    msg = bot.send_message(
        chat_id,
        "Выберите дату для просмотра",
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
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, date_to_edit=None)
    


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=States.get_looking_date_for_edit
    )
def get_looking_date_info(call: CallbackQuery):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
        
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
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.set_state(call.from_user.id, States.get_looking_date_info_for_edit, call.message.chat.id)
            bot.add_data(call.from_user.id, chat_id, date_to_edit=date.strftime('%d.%m.%Y'))
            show_events(call, date.strftime('%d.%m.%Y'))



# Обработчик выбора конкретного результата
@bot.callback_query_handler(state=States.get_events_for_edit, func=lambda call: call.data.startswith("event_"))
def handle_event_selection(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    
    is_admin_check = admin_check(call)

    if is_admin_check==True:
        target_id = "%"
    else:
        target_id = chat_id
    
    bot.set_state(call.from_user.id, States.editing_event, call.message.chat.id)
    
    event_number = int(call.data.split("_")[1])
    target_date = str(call.data.split("_")[2])
    
    con = sl.connect(db)
    cursor = con.cursor()
    offset = event_number - 1
        
    sql = f"""SELECT * FROM events WHERE user_id LIKE ? AND date LIKE ? ORDER BY date, start_time LIMIT ? OFFSET ?"""
    data = (target_id, target_date, 1, offset)
    cursor.execute(sql, data)
    result = cursor.fetchone()
    
    try:
        start_time = result[5]
    except:
        start_time = ""
    try:
        end_time = result[6]
    except:
        end_time = ""
        
    buttons = []
    
    keyboard = types.InlineKeyboardMarkup()
    buttons.append(types.InlineKeyboardButton('Изменить', callback_data='edit_selected_event'))
    buttons.append(types.InlineKeyboardButton('Отмена', callback_data='cancel_editing'))
    keyboard.row(*buttons)
    
    msg = bot.send_message(call.message.chat.id, f"Изменить следующее мероприятие?\n\n\n<b>Мероприятие:</b> {result[7]}\n\n<b>Дата:</b> {result[4]}\n\n<b>Время:</b> {start_time} - {end_time}\n\n<b>Помещение:</b> {result[10]}\n\n<b>Ответственные:</b> {result[12]}", reply_markup=keyboard, parse_mode='html')
    bot.add_data(call.from_user.id, chat_id, last_m_id=msg.id, editing_event=result)
    bot.delete_message(chat_id, call.message.message_id)


@bot.callback_query_handler(state=States.editing_event, func=lambda call: True)
def handle_event_selection(call):
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
    
    bot.set_state(call.from_user.id, States.editing_event_parameters, call.message.chat.id)
    
    if call.data == 'edit_selected_event':
        
        event = []
        
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            event = data.get("editing_event", None)
            
            try:
                start_time = event[5]
            except:
                start_time = ""
            try:
                end_time = event[6]
            except:
                end_time = ""
                        
        bot.add_data(call.from_user.id, chat_id, event_id=event[0], userid=event[1], record_datetime=event[2], generic_title=event[7], edited_title=event[7], generic_date=event[4], edited_date=event[4], edited_day_of_week=event[3], generic_start_time=start_time, generic_end_time=end_time, edited_start_time=start_time, edited_end_time=end_time, generic_equipment=event[11], edited_equipment=event[11], generic_place=event[10], edited_place=event[10], generic_count_students=event[8], edited_count_students=event[8], generic_count_visitors=event[9], edited_count_visitors=event[9], generic_seniors=event[12], edited_seniors=event[12], event_edited=False)
            
        edit_selected_event(call)
    elif call.data == 'cancel_editing':
        tmp_msg = bot.send_message(chat_id, "Изменение отменено", parse_mode='html')

        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        from events_plan.events_plan_menu import get_calendar
        get_calendar(call)
        
        time.sleep(3)
        try:
            bot.delete_message(chat_id, tmp_msg.id)
        except:
            pass
        
        return


def edit_selected_event(call):
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
    
    bot.set_state(call.from_user.id, States.editing_event_parameters, chat_id)
    
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
        title=data.get('edited_title', None)
        date=data.get('edited_date', None)
        if data.get("edited_start_time", None) != None:
            start_time = data.get("edited_start_time", None)
        else:
            start_time = ""
        if data.get("edited_end_time", None) != None:
            end_time = data.get("edited_end_time", None)
        else:
            end_time = ""
        equipment=data.get('edited_equipment', None)
        place=data.get('edited_place', None)
        count_students=data.get('edited_count_students', None)
        count_visitors=data.get('edited_count_visitors', None)
        seniors=data.get('edited_seniors', None)
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(types.InlineKeyboardButton('Название', callback_data='edit_event_title'))
        keyboard.row(types.InlineKeyboardButton('Дата', callback_data='edit_event_date'))
        keyboard.row(types.InlineKeyboardButton('Время', callback_data='edit_event_time'))
        keyboard.row(types.InlineKeyboardButton('Оборудование', callback_data='edit_event_equipment'))
        keyboard.row(types.InlineKeyboardButton('Помещение', callback_data='edit_event_place'))
        keyboard.row(types.InlineKeyboardButton('Количество учащихся', callback_data='edit_event_students'))
        keyboard.row(types.InlineKeyboardButton('Количество посетителей', callback_data='edit_event_visitors'))
        keyboard.row(types.InlineKeyboardButton('Ответственные', callback_data='edit_event_seniors'))
        keyboard.row(types.InlineKeyboardButton('Завершить редактирование', callback_data='edit_event_complete'))
            
        msg = bot.send_message(chat_id, f"Выберите поле для редактирования:\n\n\n<b>Мероприятие:</b> {title}\n\n<b>Дата:</b> {date}\n\n<b>Время:</b> {start_time} - {end_time}\n\n<b>Оборудование:</b> {equipment}\n\n<b>Помещение:</b> {place}\n\n<b>Количество учащихся:</b> {count_students}\n\n<b>Количество посетителей:</b> {count_visitors}\n\n<b>Ответственные:</b> {seniors}", reply_markup=keyboard, parse_mode='html')
        
    bot.add_data(user_id=call.from_user.id, chat_id=chat_id, last_m_id=msg.id)


# Обработчик нажатий на кнопки
@bot.callback_query_handler(state=States.editing_event_parameters, func=lambda call: call.data.startswith("edit_event_complete"))
def handle_editor(call):
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
    
    
    with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
        edit_status = data.get("event_edited", None)
        edit_message = data.get("edit_msg_id", None)
        bot.delete_message(chat_id, edit_message)
        if edit_status == False:
            tmp_msg = bot.send_message(chat_id, "Редактирование отменено", parse_mode='html')
        elif edit_status == True:
            with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
                
                info_text = ""
                
                event_id=data.get('event_id', None)
                userid=data.get('userid', None)
                record_datetime=data.get('record_datetime', None)
                
                generic_title=data.get('generic_title', None)
                title=data.get('edited_title', None)
            
                if data.get('edited_title', None) != data.get('generic_title', None):
                    info_text += f"<b>Мероприятие:</b> <code>{data.get('edited_title', None)}</code>\n\n"

                generic_date=data.get('generic_date', None)
                date=data.get('edited_date', None)
                
                if data.get('edited_date', None) != data.get('generic_date', None):
                    info_text += f"<b>Дата:</b> <code>{data.get('edited_date', None)}</code>\n\n"
                
                day_of_week=data.get('edited_day_of_week', None)
                
                generic_start_time = data.get("generic_start_time", None)
                start_time = data.get("edited_start_time", None)
                generic_end_time = data.get("generic_end_time", None)
                end_time = data.get("edited_end_time", None)
                
                if data.get('edited_start_time', None) != data.get('generic_start_time', None) or data.get('edited_end_time', None) != data.get('generic_end_time', None):
                    if data.get("edited_start_time", None) != None:
                        start_time = data.get("edited_start_time", None)
                    else:
                        start_time = ""
                    
                    if data.get("edited_end_time", None) != None:
                        end_time = data.get("edited_end_time", None)
                    else:
                        end_time = ""
                    
                    info_text += f"<b>Время:</b> <code>{start_time}</code> - <code>{end_time}</code>\n\n"
                
                generic_equipment=data.get('generic_equipment', None)
                equipment=data.get('edited_equipment', None)
                
                if data.get('edited_equipment', None) != data.get('generic_equipment', None):
                    info_text += f"<b>Оборудование:</b> <code>{data.get('edited_equipment', None)}</code>\n\n"
                
                generic_place=data.get('generic_place', None)
                place=data.get('edited_place', None)
                
                if data.get('edited_place', None) != data.get('generic_place', None):
                    info_text += f"<b>Помещение:</b> <code>{data.get('edited_place', None)}</code>\n\n"
                
                generic_count_students=data.get('generic_count_students', None)
                count_students=data.get('edited_count_students', None)
                
                if data.get('edited_count_students', None) != data.get('generic_count_students', None):
                    info_text += f"<b>Количество учащихся:</b> <code>{data.get('edited_count_students', None)}</code>\n\n"
                
                generic_count_visitors=data.get('generic_count_visitors', None)
                count_visitors=data.get('edited_count_visitors', None)
                
                if data.get('edited_count_visitors', None) != data.get('generic_count_visitors', None):
                    info_text += f"<b>Количество посетителей:</b> <code>{data.get('edited_count_visitors', None)}</code>\n\n"
                
                generic_seniors=data.get('generic_seniors', None)
                seniors=data.get('edited_seniors', None)
                
                if data.get('edited_seniors', None) != data.get('generic_seniors', None):
                    info_text += f"<b>Ответственные:</b> <code>{data.get('edited_seniors', None)}</code>\n\n"
                
                operation_type = "EDIT"
            
            
            con = sl.connect(db)
            sql_rec = 'UPDATE events SET title = ?, day_of_week = ?, date = ?, start_time = ?, end_time = ?, count_students = ?, count_visitors = ?, place = ?, equipment = ?, seniors = ?, operation_type = ? WHERE title = ? AND date = ? AND start_time = ? AND end_time = ? RETURNING *;'            
            with con:
                try:
                    cursor = con.cursor()
                    cursor.execute(sql_rec, (title, day_of_week, date, start_time, end_time, count_students, count_visitors, place, equipment, seniors, operation_type, generic_title, generic_date, generic_start_time, generic_end_time))
                    row = cursor.fetchone()
                except Exception as e:
                    print(e)
            
            
            try:
                msg_text = f"<b>Информация о следующем мероприятии была изменена:</b>\n\n\n<b>Мероприятие:</b> {generic_title}\n<b>Дата:</b> {generic_date}\n<b>Время:</b> {generic_start_time} - {generic_end_time}\n\n\n<b>Новые данные:</b>\n\n{info_text}"
                
                bot.send_message(chat_id, text=msg_text, parse_mode='html')
            except Exception as e:
                print(e)
                print(f"Невозможно отправить сообщение юзеру {chat_id}")
                bot.send_message(chat_id, f"Не удалось сформировать для Вас подтверждение записи", parse_mode='html')
                bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {userid}
                <pre> <code class="language-python">   
                {e}
                </code> </pre>""", parse_mode='html')
            
            # Отправка уведомлений администрации
            con = sl.connect(db)
            cursor = con.cursor()
            cursor.execute("""SELECT telegram_id, full_name FROM staff WHERE notifications = 'ALL'""")
            notifications_all = cursor.fetchall()
            for id in notifications_all:
                if chat_id != id[0]:
                    try:
                        msg_text = f"<b>Информация о следующем мероприятии была изменена:</b>\n\n\n<b>Мероприятие:</b> {generic_title}\n<b>Дата:</b> {generic_date}\n<b>Время:</b> {generic_start_time} - {generic_end_time}\n\n\n<b>Новые данные:</b>\n\n{info_text}"
                        
                        bot.send_message(id[0], text=msg_text, parse_mode='html')
                    except Exception as e:
                        print(e)
                        print(f"Невозможно отправить сообщение пользователю {id[1]}")
                        bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {id[1]}
                        <pre> <code class="language-python">   
                        {e}
                        </code> </pre>""", parse_mode='html')
            if chat_id != userid:
                msg_text = f"<b>Информация о Вашем мероприятии была изменена:</b>\n\n\n<b>Мероприятие:</b> {generic_title}\n<b>Дата:</b> {generic_date}\n<b>Время:</b> {generic_start_time} - {generic_end_time}\n\n\n<b>Новые данные:</b>\n\n{info_text}"
                
                bot.send_message(userid, text=msg_text, parse_mode='html')
            
            
            tmp_msg = bot.send_message(chat_id, "Дописать сохранение изменений", parse_mode='html')    
    
    from events_plan.events_plan_menu import get_calendar
    get_calendar(call)
    
    time.sleep(3)
    try:
        bot.delete_message(chat_id, tmp_msg.id)
    except:
        pass
    
    return
