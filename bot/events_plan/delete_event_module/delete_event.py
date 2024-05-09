from telebot import types
from telebot.types import CallbackQuery
from init_bot import bot
from bot_states import *
import sqlite3 as sl
from datetime import datetime
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE
import time
from secrets import db


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
@bot.message_handler(is_admin=False, is_delete_event=True, state=States.events_plan)
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
    
    bot.set_state(m.from_user.id, States.choose_looking_period_for_delete, chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    btn2 = types.KeyboardButton("План мероприятий")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(chat_id, "Удаление мероприятия", parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, delete_msg_id=msg.id, userid=m.from_user.id)
    
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
        
    bot.set_state(m.from_user.id, States.get_events_for_delete, chat_id)
        
    page = 1 # Начальная страница
    items_per_page = 5 # Количество элементов на странице
    event_index = 1

    count = get_count(target_id, target_date)
    
    if len(count) ==0:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton('Закрыть', callback_data='close_message'))
        
        bot.send_message(chat_id, '''Мероприятия не найдены''', parse_mode='html', reply_markup=keyboard)
    
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
                last_message = data.get("last_m_id", None)
                delete_message = data.get("delete_msg_id", None)
                bot.delete_message(chat_id, last_message)
                bot.delete_message(chat_id, delete_message)
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
        msg_text += "<b>Выберите мероприятие для удаления</b>:\n\n\n"
    for event in events:
        msg_text += f"[{event_index}]\n<b>Мероприятие:</b> {event[7]}\n<b>Дата:</b> {event[4]}\n<b>Время:</b> {event[5]} - {event[6]}\n<b>Помещение:</b> {event[10]}\n<b>Ответственные:</b> {event[12]}\n\n\n"
        event_index += 1
    if len(events) == 0:
        msg_text += "Мероприятий нет"
    msg = bot.send_message(chat_id, text=msg_text, parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(state=States.get_events_for_delete, func=lambda call: call.data.startswith("prev_") or call.data.startswith("next_") or call.data.startswith("prevday_") or call.data.startswith("nextday_"))
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
    
    bot.set_state(call.from_user.id, States.get_events_for_delete, chat_id)
        
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



@bot.message_handler(is_admin=True, is_delete_event=True, state=States.events_plan)
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
    
    bot.set_state(m.from_user.id, States.choose_looking_period_for_delete, chat_id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Назад")
    btn2 = types.KeyboardButton("План мероприятий")
    markup.add(btn1, btn2)
    
    msg = bot.send_message(chat_id, "Удаление мероприятия", parse_mode='html', reply_markup=markup)
    bot.add_data(m.from_user.id, chat_id, delete_msg_id=msg.id, userid=m.from_user.id)
    
    get_events_date_admin(m)



def get_events_date_admin(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
        
    bot.set_state(m.from_user.id, States.get_looking_date_for_delete, chat_id)
    
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
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id, date_to_delete=None)
    


@bot.callback_query_handler(
    func=lambda call: call.data.startswith(calendar_1_callback.prefix),
    state=States.get_looking_date_for_delete
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
            bot.set_state(call.from_user.id, States.get_looking_date_info_for_delete, call.message.chat.id)
            bot.add_data(call.from_user.id, chat_id, date_to_delete=date.strftime('%d.%m.%Y'))
            show_events(call, date.strftime('%d.%m.%Y'))



# Обработчик выбора конкретного результата
@bot.callback_query_handler(state=States.get_events_for_delete, func=lambda call: call.data.startswith("event_"))
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
    
    bot.set_state(call.from_user.id, States.deleting_event, call.message.chat.id)
        
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
    buttons.append(types.InlineKeyboardButton('Удалить', callback_data='delete_selected_event'))
    buttons.append(types.InlineKeyboardButton('Отмена', callback_data='cancel_deleting'))
    keyboard.row(*buttons)
    
    msg = bot.send_message(call.message.chat.id, f"Удалить выбранное мероприятие?\n\n\n<b>Мероприятие:</b> {result[7]}\n\n<b>Дата:</b> {result[4]}\n\n<b>Время:</b> {start_time} - {end_time}\n\n<b>Помещение:</b> {result[10]}\n\n<b>Ответственные:</b> {result[12]}", reply_markup=keyboard, parse_mode='html')
    bot.add_data(call.from_user.id, chat_id, deleting_event=result, last_m_id=msg.id)
    bot.delete_message(chat_id, call.message.message_id)


@bot.callback_query_handler(state=States.deleting_event, func=lambda call: True)
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
    
    if call.data == 'delete_selected_event':
        with bot.retrieve_data(user_id=call.from_user.id, chat_id=chat_id) as data:
            event = data.get("deleting_event", None)
            con = sl.connect(db)
            cursor = con.cursor()
            sql = f"""DELETE FROM events WHERE event_id = ? AND user_id = ? AND title = ? AND date = ?"""
            data = (event[0], event[1], event[7], event[4])
            cursor.execute(sql, data)
            con.commit()
        try:
            bot.send_message(chat_id, f"Мероприятие «{event[7]}» удалено", parse_mode='html')
        except Exception as e:
            print(e)
            print(f"Невозможно отправить сообщение юзеру {chat_id}")
            bot.send_message(chat_id, f"Не удалось сформировать для Вас подтверждение записи", parse_mode='html')
            bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {event[1]}
            <pre> <code class="language-python">   
            {e}
            </code> </pre>""", parse_mode='html')
        
        # Отправка уведомлений администрации
        cursor = con.cursor()
        cursor.execute("""SELECT telegram_id, full_name FROM staff WHERE notifications = 'ALL'""")
        notifications_all = cursor.fetchall()
        data = (chat_id, )
        cursor.execute("""SELECT full_name FROM staff WHERE telegram_id = ?""", data)
        deleter = cursor.fetchone()
        for id in notifications_all:
            if chat_id != id[0]:
                try:
                    bot.send_message(id[0], f"<b>Следующее мероприятие удалено пользователем {deleter[0]}</b>\n\n\n<b>Мероприятие:</b> {event[7]}\n\n<b>Дата:</b> {event[4]}\n\n<b>Время:</b> {event[5]} - {event[6]}\n\n<b>Помещение:</b> {event[10]}", parse_mode='html')
                except Exception as e:
                    print(e)
                    print(f"Невозможно отправить сообщение пользователю {id[1]}")
                    bot.send_message(102452736, f"""Невозможно отправить сообщение пользователю {id[1]}
                    <pre> <code class="language-python">   
                    {e}
                    </code> </pre>""", parse_mode='html')
        if chat_id != event[1]:
            bot.send_message(event[1], f"<b>Ваше мероприятие было удалено администратором {deleter[0]}</b>\n\n\n<b>Мероприятие:</b> {event[7]}\n\n<b>Дата:</b> {event[4]}\n\n<b>Время:</b> {event[5]} - {event[6]}\n\n<b>Помещение:</b> {event[10]}", parse_mode='html')
    elif call.data == 'cancel_deleting':
        tmp_msg = bot.send_message(chat_id, "Удаление отменено", parse_mode='html')
    
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
    from events_plan.events_plan_menu import get_calendar
    get_calendar(call)
    
    time.sleep(3)
    try:
        bot.delete_message(chat_id, tmp_msg.id)
    except:
        pass
    
    return
