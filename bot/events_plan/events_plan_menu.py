from telebot import types
from init_bot import bot
from events_plan.record_event_module.record_event import *
from events_plan.edit_event_module.edit_event import *
from events_plan.delete_event_module.delete_event import *
from events_plan.looking_event_module.looking_plan import *
from bot_states import *
from send_action import send_action


@bot.message_handler(
    is_events_plan_menu=True,
    state=States.state_list()
    )
def get_calendar(m):
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
        try:
            last_message_id = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message_id)
        except Exception as e:
            pass
        try:
            look_message = data.get("look_msg_id", None)
            bot.delete_message(chat_id, look_message)
        except:
            pass
        try:
            delete_message = data.get("delete_msg_id", None)
            bot.delete_message(chat_id, delete_message)
        except Exception as e:
            pass
        try:
            edit_message = data.get("edit_msg_id", None)
            bot.delete_message(chat_id, edit_message)
        except Exception as e:
            pass
    
    # bot.delete_state(user_id=m.from_user.id, chat_id=chat_id)
    
    bot.set_state(m.from_user.id, States.events_plan, chat_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Посмотреть план")
    btn2 = types.KeyboardButton("Создать мероприятие")
    btn3 = types.KeyboardButton("Изменить мероприятие")
    btn4 = types.KeyboardButton("Удалить мероприятие")
    btn5 = types.KeyboardButton("В главное меню")
    markup.row(btn2, btn3, btn4)
    markup.row(btn1)
    markup.row(btn5)
    msg = bot.send_message(chat_id, "Выберите действие", parse_mode='html', reply_markup=markup)

    try:
        bot.delete_message(chat_id, m.message_id)
    except:
        pass
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)
        
        
@bot.message_handler(is_new_event=True, state=States.events_plan)
def confirmation(m):
    bot.set_state(m.from_user.id, States.record_new_event, m.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Подтверждаю")
    btn2 = types.KeyboardButton("Ознакомиться")
    markup.add(btn1, btn2)
    markup.row(types.KeyboardButton("Назад к плану"))
    markup.row(types.KeyboardButton("В главное меню"))
    msg = bot.send_message(m.chat.id, "Подтвердите, что ознакомились с планом", parse_mode='html', reply_markup=markup)
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=m.chat.id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(m.chat.id, last_message)
    except:
        pass
    bot.delete_message(m.chat.id, m.message_id)
    bot.add_data(m.from_user.id, m.chat.id, last_m_id=msg.id)
