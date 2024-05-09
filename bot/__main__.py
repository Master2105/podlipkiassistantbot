import os
from telebot import types, custom_filters
import sqlite3 as sl
from events_plan.events_plan_menu import *
from bot_management import *
from handlers.back_button_handlers import *
from bot_states import *
from init_bot import bot
from my_custom_filters import *
from send_action import send_action
from middlewares.antiflood_middleware import SimpleMiddleware
from handlers.delete_message_handler import *
import logging, sys
import telebot
from secrets import db


if os.path.exists("logs"):
    pass
else:
    os.mkdir("logs")

MY_NAME = "podlipki_assistant_bot"

logger = telebot.logger
# logger = logging.getLogger(MY_NAME)

logc = logger.critical
loge = logger.error
logw = logger.warning
logi = logger.info
logd = logger.debug


BASEDTFORMAT = "%d.%m.%y %H:%M:%S"
FLN = "[%(levelname)9s %(asctime)s] %(funcName)s %(threadName)s " \
"%(filename)s:%(lineno)d: "
FLNC = "%(filename)s:%(lineno)04d; %(funcName)-12s %(threadName)s "\
"%(levelname)9s %(asctime)s\n"
MSG = "%(message)s"

file_formatter = logging.Formatter(FLN + MSG, BASEDTFORMAT)
console_formatter = logging.Formatter(FLN + MSG, BASEDTFORMAT)

telebot.console_output_handler.setFormatter(console_formatter)
ch = logging.StreamHandler(sys.stderr)
ch.setFormatter(console_formatter)
telebot.console_output_handler.setFormatter(console_formatter)
LOGFILE_FP = os.path.join("logs", datetime.now().strftime("%y.%m.%d") + ".log")
fh = logging.FileHandler(LOGFILE_FP, encoding="utf-8")
fh.setFormatter(file_formatter)
logger.addHandler(fh)

logger.setLevel(logging.INFO)

logi("Запуск")

FILENAME = "/data/todo.json" if "AMVERA" in os.environ else "todo.json"


@bot.message_handler(is_access=True, commands=['start'])
@send_action('typing')
def send_welcome(m):
    bot.set_state(m.from_user.id, States.start, m.chat.id)
    msg = bot.send_message(m.chat.id, '''Привет! На связи бот-ассистент хоровой школы. Я способен помочь в решении различных повседневных задач. С моей помощью Вы сможете полностью управлять планом мероприятий - добавлять мероприятия, редактировать и удалять, а так же получать информацию о мероприятиях из плана. Кнопку перехода к плану мероприятий Вы можете видеть ниже''', parse_mode='html')
    bot.add_data(m.from_user.id, m.chat.id, start_m_id=msg.id)
    main_menu(m)


@bot.message_handler(is_main_menu=True, state=States.state_list())
def main_menu(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
        try:
            rec_message = data.get("rec_msg_id", None)
            bot.delete_message(chat_id, rec_message)
        except:
            pass
        try:
            look_message = data.get("look_msg_id", None)
            bot.delete_message(chat_id, look_message)
        except:
            pass
            
    bot.set_state(m.from_user.id, States.main_menu, chat_id)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("План мероприятий")
    btn2 = types.KeyboardButton("Управление ботом")
    
    row = []
    
    row.append(btn1)
        
    con = sl.connect(db)
    
    with con:
        try:
            info = con.execute('SELECT role FROM staff WHERE telegram_id=?', (chat_id, )).fetchone()[0]
            if info == 'root': 
                row.append(btn2)
        except Exception as e:
            print(e)
    
    markup.row(*row)
        
    msg = bot.send_message(chat_id, '''Выберите действие''', parse_mode='html', reply_markup=markup)
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
    except:
        pass
    
    bot.delete_message(chat_id, m.message_id)
    bot.add_data(m.from_user.id, chat_id, last_m_id=msg.id)


if __name__ == '__main__':
    bot.setup_middleware(SimpleMiddleware(0.5))
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.add_custom_filter(custom_filters.IsDigitFilter())
    bot.add_custom_filter(AccessFilter())
    bot.add_custom_filter(AdminFilter())
    bot.add_custom_filter(MainMenuFilter())
    bot.add_custom_filter(BotManagementFilter())
    bot.add_custom_filter(EventsPlantFilter())
    bot.add_custom_filter(LookPlanFilter())
    bot.add_custom_filter(NewEventFilter())
    bot.add_custom_filter(NewEventConfirmedFilter())
    bot.add_custom_filter(EditEventFilter())
    bot.add_custom_filter(DeleteEventFilter())
    bot.add_custom_filter(RecordNewUserFilter())
    bot.add_custom_filter(DeleteUserFilter())
    bot.add_custom_filter(CancelLastTryFilter())
    bot.add_custom_filter(BackButtonFilter())
    bot.add_custom_filter(CancelButtonFilter())
    bot.add_custom_filter(ExportDBFilter())
    # logging.basicConfig(level=logging.DEBUG, filename=f"""logs/{datetime.now().strftime("%y.%m.%d")}.log""", filemode="w", format="%(asctime)s %(levelname)s %(message)s")
    # logging.debug("A DEBUG Message")
    # logging.info("An INFO")
    # logging.warning("A WARNING")
    # logging.error("An ERROR")
    # logging.critical("A message of CRITICAL severity")
    while True:
        try:
            bot.infinity_polling(none_stop=True)
        except Exception as e:
            print(e)
