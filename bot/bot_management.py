from telebot import types
from accepted_ids import IDs
import secrets
from secrets import events_sheet_id
from init_bot import bot


@bot.message_handler(commands=['start'])
def go_to_access(message):
    print("go_to_access in bot management")
    from __main__ import check_access
    check_access(message)


# @bot.message_handler(func=lambda message: message.text.lower() == "управление ботом")
def management_fork(message):
    print("management_fork")
    if message.text.lower() == "/start":
        print("go_to_access in events_plan")
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "в главное меню":
        from __main__ import send_welcome
        send_welcome(message)
    elif message.text.lower() == "план мероприятий":
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "управление ботом":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Зарегистрировать пользователя")
        btn2 = types.KeyboardButton("Удалить пользователя")
        btn3 = types.KeyboardButton("Отменить незавершённую попытку записи")
        btn5 = types.KeyboardButton("В главное меню")
        markup.add(btn1, btn2, btn3, btn5)
        bot.send_message(message.chat.id, "Выберите действие", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, bot_management)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки", parse_mode='html')
        bot.register_next_step_handler(message, management_fork)


def bot_management(message):
    print("bot_management")
    if message.text.lower() == "/start":
        print("go_to_access in events_plan")
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "зарегистрировать пользователя":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_adm = types.KeyboardButton("Администрация")
        btn_prep = types.KeyboardButton("Преподаватели")
        btn_root = types.KeyboardButton("Root")
        markup.add(btn_adm, btn_prep, btn_root)
        bot.send_message(message.chat.id, "В какую группу добавить?", parse_mode='html', reply_markup=markup)
        bot.register_next_step_handler(message, choose_group)
    elif message.text.lower() == "удалить пользователя":
        pass
    elif message.text.lower() == "отменить незавершённую попытку записи":
        from record_event import event_data
        event_data.clear()
        bot.send_message(message.chat.id, "Запись отменена", parse_mode='html')
        from __main__ import send_welcome
        send_welcome(message)
    elif message.text.lower() == "в главное меню":
        from __main__ import send_welcome
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки", parse_mode='html')
        bot.register_next_step_handler(message, bot_management)


def choose_group(message):
    print("choose_group")
    if message.text.lower() == "/start":
        print("go_to_access in events_plan")
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "администрация":
        selected_group = IDs.admins
        bot.send_message(message.chat.id, "Напишите ID", parse_mode='html')
        bot.register_next_step_handler(message, record_new_user, selected_group)
    elif message.text.lower() == "преподаватели":
        selected_group = IDs.preps
        bot.send_message(message.chat.id, "Напишите ID", parse_mode='html')
        bot.register_next_step_handler(message, record_new_user, selected_group)
    elif message.text.lower() == "root":
        selected_group = IDs.roots
        bot.send_message(message.chat.id, "Напишите ID", parse_mode='html')
        bot.register_next_step_handler(message, record_new_user, selected_group)


def record_new_user(message, selected_group):
    print("record_new_user")
    selected_group.append(message.text)
    bot.send_message(message.chat.id, "Пользователь зарегистрирован", parse_mode='html')
    from __main__ import send_welcome
    send_welcome(message)


@bot.message_handler(func=lambda message: message.text.lower() == "в главное меню")
def go_to_main(message):
    print("go_to_main in bot management")
    from __main__ import send_welcome
    send_welcome(message)