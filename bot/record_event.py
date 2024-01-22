import datetime
from telebot import types
from accepted_ids import IDs
import gspread
import gspread_formatting
import requests
import secrets
from secrets import events_sheet_id
from init_bot import bot
import array as arr


gc = gspread.service_account(filename=secrets.path_to_service_json)


event_data = []


def get_name(message):
    print("get_name")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    else:
        event_name = message.text

        event_data.append(event_name)

        bot.send_message(message.chat.id, "Дата мероприятия", parse_mode='html')
        bot.register_next_step_handler(message, get_date)


def get_date(message):
    print("get_date")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    else:
        event_date = message.text

        event_data.append(event_date)

        bot.send_message(message.chat.id, "Время начала в формате ЧЧ:ММ. Если время отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_start_time)


def get_start_time(message):
    print("get_start_time")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "нет":
        start_time = ''

        event_data.append(start_time)

        bot.send_message(message.chat.id, "Время окончания в формате ЧЧ:ММ. Если время отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_end_time)
    else:
        start_time = message.text

        event_data.append(start_time)

        bot.send_message(message.chat.id, "Время окончания в формате ЧЧ:ММ. Если время отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_end_time)


def get_end_time(message):
    print("get_end_time")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "нет":
        end_time = ''

        event_data.append(end_time)

        bot.send_message(message.chat.id, "Количество учащихся. Напишите только число. Если параметр отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_students_number)
    else:
        end_time = message.text

        event_data.append(end_time)

        bot.send_message(message.chat.id, "Количество учащихся. Напишите только число. Если параметр отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_students_number)


def get_students_number(message):
    print("get_students_number")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "нет":
        students_number = ''

        event_data.append(students_number)

        bot.send_message(message.chat.id, "Количество посетителей. Напишите только число. Если параметр отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_visitors_number)
    else:
        students_number = message.text

        event_data.append(students_number)

        bot.send_message(message.chat.id, "Количество посетителей. Напишите только число. Если параметр отсутствует, напишите нет", parse_mode='html')
        bot.register_next_step_handler(message, get_visitors_number)


def get_visitors_number(message):
    print("get_visitors_number")
    if message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == "возвращаемся":
        button_halls = types.InlineKeyboardButton('Залы', callback_data='halls')
        button_rooms = types.InlineKeyboardButton('Кабинеты', callback_data='rooms')
        button_another_place = types.InlineKeyboardButton('Другое место', callback_data='another_place')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_halls, button_rooms, button_another_place)

        bot.send_message(message.chat.id, "Выберите помещение", parse_mode='html', reply_markup=keyboard)
    elif message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "нет":
        visitors_number = ''

        event_data.append(visitors_number)

        button_halls = types.InlineKeyboardButton('Залы', callback_data='halls')
        button_rooms = types.InlineKeyboardButton('Кабинеты', callback_data='rooms')
        button_another_place = types.InlineKeyboardButton('Другое место', callback_data='another_place')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_halls, button_rooms, button_another_place)

        bot.send_message(message.chat.id, "Выберите помещение", parse_mode='html', reply_markup=keyboard)
    else:
        visitors_number = message.text

        event_data.append(visitors_number)

        button_halls = types.InlineKeyboardButton('Залы', callback_data='halls')
        button_rooms = types.InlineKeyboardButton('Кабинеты', callback_data='rooms')
        button_another_place = types.InlineKeyboardButton('Другое место', callback_data='another_place')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(button_halls, button_rooms, button_another_place)

        bot.send_message(message.chat.id, "Выберите помещение", parse_mode='html', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def choose_room(call):
    print("choose_room")
    if call.data == 'halls':
        hall_concert_button = types.InlineKeyboardButton('Концертный зал', callback_data='hall_concert')
        hall_organ_button = types.InlineKeyboardButton('Органный зал', callback_data='hall_organ')
        to_all_rooms_button = types.InlineKeyboardButton('Назад', callback_data='to_all_rooms')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(hall_concert_button, hall_organ_button, to_all_rooms_button)

        bot.edit_message_text("Выберите помещение", reply_markup=keyboard, chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'rooms' or call.data == 'to_floors':
        floor_1_button = types.InlineKeyboardButton('Первый этаж', callback_data='floor_1')
        floor_2_button = types.InlineKeyboardButton('Второй этаж', callback_data='floor_2')
        to_all_rooms_button = types.InlineKeyboardButton('Назад', callback_data='to_all_rooms')


        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(floor_1_button, floor_2_button, to_all_rooms_button)

        bot.edit_message_text("Выберите помещение", reply_markup=keyboard, chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'floor_1':
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
        to_floors_button = types.InlineKeyboardButton('Назад', callback_data='to_floors')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(ff_104_button, ff_105_button, ff_106_button, ff_107_button, ff_108_button, ff_109_button, ff_110_button, ff_111_button, ff_112_button, ff_113_button, to_floors_button)

        bot.edit_message_text("Выберите помещение", reply_markup=keyboard, chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'floor_2':
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
        to_floors_button = types.InlineKeyboardButton('Назад', callback_data='to_floors')

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(sf_201_button, sf_202_button, sf_203_button, sf_204_button, sf_205_button, sf_206_button, sf_207_button, sf_209_button, sf_210_button, sf_211_button, sf_212_button, sf_213_button, sf_214_button, sf_215_button, sf_216_button, to_floors_button)

        bot.edit_message_text("Выберите помещение", reply_markup=keyboard, chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'to_all_rooms':
        msg = bot.send_message(call.message.chat.id, "Возвращаемся", parse_mode='html')
        get_visitors_number(msg)
    elif call.data == 'another_place':
        msg = bot.send_message(call.message.chat.id, "Напишите место", parse_mode='html')
        bot.register_next_step_handler(msg, another_place_record)
    elif call.data == 'hall_concert':
        room_event = 'Концертный зал'
        event_data.append(room_event)
        msg = bot.send_message(call.message.chat.id, "Требуемое оборудование. Напишите всё необходимое через запятую\nЕсли оборудование не требуется, напишите нет", parse_mode='html')
        bot.register_next_step_handler(msg, event_equipment)
    elif call.data == 'hall_organ':
        room_event = 'Органный зал'
        event_data.append(room_event)
        msg = bot.send_message(call.message.chat.id, "Требуемое оборудование. Напишите всё необходимое через запятую\nЕсли оборудование не требуется, напишите нет", parse_mode='html')
        bot.register_next_step_handler(msg, event_equipment)
    elif call.data.split('_')[0] == 'room':
        room_event = str('Кабинет ') + call.data.split('_')[1]
        event_data.append(room_event)
        msg = bot.send_message(call.message.chat.id, "Требуемое оборудование. Напишите всё необходимое через запятую\nЕсли оборудование не требуется, напишите нет", parse_mode='html')
        bot.register_next_step_handler(msg, event_equipment)


def another_place_record(message):
    print("another_place_record")
    room_event = message.text
    event_data.append(room_event)
    msg = bot.send_message(message.chat.id, "Требуемое оборудование. Напишите всё необходимое через запятую\nЕсли оборудование не требуется, напишите нет", parse_mode='html')
    bot.register_next_step_handler(msg, event_equipment)


def event_equipment(message):
    print("event_equipment")
    if message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    elif message.text.lower() == 'нет':
        equipment = ''
        event_data.append(equipment)
        bot.send_message(message.chat.id, "Ответственные лица. Напишите всех ответственных через запятую в формате Фамилия И.О.", parse_mode='html')
        bot.register_next_step_handler(message, event_seniors)
    else:
        equipment = message.text
        event_data.append(equipment)
        bot.send_message(message.chat.id, "Ответственные лица. Напишите всех ответственных через запятую в формате Фамилия И.О.", parse_mode='html')
        bot.register_next_step_handler(message, event_seniors)


def event_seniors(message):
    print("event_seniors")
    if message.text.lower() == "/start":
        print("go_to_access in events_plan")
        event_data.clear()
        from __main__ import check_access
        check_access(message)
    elif message.text.lower() == "назад к плану":
        event_data.clear()
        from events_plan import get_calendar
        get_calendar(message)
    else:
        seniors = message.text

        event_data.append(seniors)
        record(message)


# @dramatiq.actor
def record(message):
    print("record")

    try:
        sh = gc.open_by_key(events_sheet_id)
        next_row = len(sh.sheet1.get_all_values()) + 1

        sh.sheet1.update(f'A{next_row}:L{next_row}', [[event_data[0], f"{datetime.datetime.now()}", event_data[2], event_data[2], event_data[3], event_data[4], event_data[1], event_data[5], event_data[6], event_data[7], event_data[8], event_data[9]]])

        #Я
        try:
            bot.send_message(102452736, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> <code>{event_data[1]}</code>\n\n<b>Место:</b> <code>{event_data[7]}</code>\n\n<b>Оборудование:</b> <code>{event_data[8]}</code>\n\n<b>Ответственные:</b> <code>{event_data[9]}</code>", parse_mode='html')
        except Exception as e:
            print(e)
            print("Невозможно отправить сообщение юзеру 102452736")
            bot.send_message(102452736, f"Не удалось сформировать для Вас подтверждение записи", parse_mode='html')

        # # #Юлия Валерьевна
        # try:
        #     bot.send_message(5872921373, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 5872921373")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Юлии Валерьевне Кочетковой, 5872921373", parse_mode='html')


        # # #Людмила Владимировна
        # try:
        #     bot.send_message(446760871, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 446760871")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Людмиле Владимировне Коневой, 446760871", parse_mode='html')


        # # #Ольга Борисовна
        # try:
        #     bot.send_message(438166996, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 438166996")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Ольге Борисовне Майоровой, 438166996", parse_mode='html')


        # # #Ольга Николаевна
        # try:
        #     bot.send_message(373266581, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 373266581")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Ольге Николаевне Филатовой, 373266581", parse_mode='html')


        # # #Оксана Ивановна
        # try:
        #     bot.send_message(179580474, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 179580474")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Оксане Ивановне Пономарёвой, 179580474", parse_mode='html')
            
            
        # # #Оксана Васильевна
        # try:
        #     bot.send_message(1259962123, f"<b>Новое мероприятие</b>\n\n<b>Дата:</b> {event_data[2]}\n<b>Время:</b> {event_data[3]}-{event_data[4]}\n\n<b>Мероприятие:</b> {event_data[1]}\n\n<b>Место:</b> {event_data[7]}\n\n<b>Оборудование:</b> {event_data[8]}\n\n<b>Ответственные:</b> {event_data[9]}", parse_mode='html')
        # except Exception as e:
        #     print(e)
        #     print("Невозможно отправить сообщение юзеру 1259962123")
        #     bot.send_message(102452736, f"Невозможно отправить сообщение Оксане Васильевне Федяковой, 1259962123", parse_mode='html')


    except Exception as e:
        print(e)
        print(f"При записи мероприятия {event_data[1]} в таблицу возникла ошибка {e}")
        bot.send_message(message.chat.id, f"<b>Возникла непредвиденная ошибка. Информация уже передана разработчикам. Скоро всё поправят</b>", parse_mode='html')
        bot.send_message(102452736, f"При записи мероприятия {event_data[1]} в таблицу возникла ошибка {e}", parse_mode='html')


    event_data.clear()
    bot.send_message(message.chat.id, "Мероприятие записано", parse_mode='html')
    from events_plan import get_calendar
    get_calendar(message)


@bot.message_handler(func=lambda message: message.text.lower() == "назад к плану")
def cancel_record(message):
    print("cancel_record in record event")
    event_data.clear()
    from events_plan import get_calendar
    get_calendar(message)


@bot.message_handler(func=lambda message: message.text.lower() == "в главное меню")
def go_to_main(message):
    print("go_to_main in record event")
    from __main__ import send_welcome
    send_welcome(message)


@bot.message_handler(commands=['start'])
def go_to_access(message):
    print("go_to_access in bot management")
    from __main__ import check_access
    check_access(message)