from telebot import types
from init_bot import bot
from bot_states import *
from send_action import send_action
from secrets import db


@bot.message_handler(is_management_menu=True, state=States.state_list())
def bot_management(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
        
    with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
        try:
            start_message = data.get("start_m_id", None)
            bot.delete_message(chat_id, start_message)
        except Exception as e:
            pass
    bot.set_state(m.from_user.id, States.bot_management, m.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("Управление пользователями"))
    markup.row(types.KeyboardButton("Экспорт базы"))
    markup.row(types.KeyboardButton("В главное меню"))
    msg = bot.send_message(m.chat.id, "Выберите действие", parse_mode='html', reply_markup=markup)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id)


@bot.message_handler(is_export_base_msg=True, state=States.bot_management)
def export_base(m):
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
    
    bot.send_document(chat_id, open(rf'{db}', 'rb'))
    bot_management(m)


# Добавление пользователя
@bot.message_handler(is_recording_user=True, state=States.state_list())
def add_new_user(m):
    bot.set_state(m.from_user.id, States.choose_group, m.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Администрация")
    btn2 = types.KeyboardButton("Преподаватели")
    btn3 = types.KeyboardButton("Root")
    markup.add(btn1, btn2, btn3)
    markup.row(types.KeyboardButton("Назад"))
    markup.row(types.KeyboardButton("В главное меню"))
    msg = bot.send_message(m.chat.id, "В какую группу добавить?", parse_mode='html', reply_markup=markup)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id)


@bot.message_handler(state=States.choose_group)
def choose_group(m):
    if m.text.lower() == "администрация":
        bot.set_state(m.from_user.id, States.append_id, m.chat.id)
        selected_role = 'admin'
        msg = bot.send_message(m.chat.id, "Напишите ID", parse_mode='html')
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(m.chat.id, last_message)
        except:
            pass
        bot.delete_message(m.chat.id, m.message_id)
        bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id, selected_role=selected_role)
        print(selected_role)
        
    elif m.text.lower() == "преподаватели":
        bot.set_state(m.from_user.id, States.append_id, m.chat.id)
        selected_role = 'prep'
        msg = bot.send_message(m.chat.id, "Напишите ID", parse_mode='html')
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(m.chat.id, last_message)
        except:
            pass
        bot.delete_message(m.chat.id, m.message_id)
        bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id, selected_role=selected_role)
        print(selected_role)
        
    elif m.text.lower() == "root":
        bot.set_state(m.from_user.id, States.append_id, m.chat.id)
        selected_role = 'root'
        msg = bot.send_message(m.chat.id, "Напишите ID", parse_mode='html')
        try:
            with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
                last_message = data.get("last_m_id", None)
                bot.delete_message(m.chat.id, last_message)
        except:
            pass
        bot.delete_message(m.chat.id, m.message_id)
        bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id, selected_role=selected_role)


# ПОЧИНИТЬ ФУНКЦИЮ ДОБАВЛЕНИЯ ЮЗЕРА
@bot.message_handler(state=States.append_id)
def record_new_user(m):
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            role = data.get("selected_role", None)
    except:
        pass
    bot.send_message(m.chat.id, f"Пользователь {m.text} зарегистрирован", parse_mode='html')
    bot_management(m)


# Удаление пользователя
@bot.message_handler(is_deleting_user=True, state=States.state_list())
def delete_user(m):
    bot.set_state(m.from_user.id, States.delete_user, m.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton("Управление ботом"))
    markup.row(types.KeyboardButton("В главное меню"))
    msg = bot.send_message(m.chat.id, "Функция скоро будет доступна", parse_mode='html', reply_markup=markup)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id)


# @send_action('typing')
# def record_new_user(m, selected_group):
#     selected_group.append(m.text)
#     bot.send_message(m.chat.id, "Пользователь зарегистрирован", parse_mode='html')
#     from __main__ import main_menu
#     bot_management(m)
