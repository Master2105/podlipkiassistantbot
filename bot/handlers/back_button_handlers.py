from init_bot import bot
from bot_states import *


cancel_states = [
        States.record_new_event_confirmed,
        States.record_event_title, 
        States.title_confirmation,
        States.record_event_date,
        States.date_event_confirmation,
        States.record_event_start_time,
        States.start_time_event_confirmation,
        States.record_event_end_time,
        States.end_time_event_confirmation,
        States.record_count_students,
        States.students_confirmation,
        States.record_count_visitors,
        States.visitors_confirmation,
        States.record_place,
        States.another_place,
        States.place_confirmation,
        States.record_equipment,
        States.eqipment_confirmation,
        States.record_seniors,
        States.seniors_confirmation,
        ]


edit_event_states = [
    States.edit_title,
    States.edit_title_confirmation,
    States.edit_date,
    States.edit_date_confirmation,
    States.edit_start_time,
    States.edit_start_time_confirmation,
    States.edit_end_time,
    States.edit_end_time_confirmation,
    States.edit_equipment,
    States.edit_equipment_confirmation,
    States.edit_place,
    States.edit_another_place,
    States.edit_place_confirmation,
    States.edit_students,
    States.edit_students_confirmation,
    States.edit_visitors,
    States.edit_visitors_confirmation,
    States.edit_seniors,
    States.edit_seniors_confirmation,
]


@bot.message_handler(
    state=cancel_states,
    is_cancel_button_filter=True
    )
def cancel(m):
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
            last_message = data.get("last_m_id", None)
            bot.delete_message(chat_id, last_message)
        except:
            pass
    
    bot.delete_state(user_id=m.from_user.id, chat_id=chat_id)
    
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.record_event_title, 
    is_back_button_filter=True
    )
def go_back(m):
    try:
        chat_id = m.chat.id
    except:
        chat_id = m.message.chat.id
    
    try:
        with bot.retrieve_data(user_id=m.from_user.id, chat_id=chat_id) as data:
            rec_message = data.get("rec_msg_id", None)
            bot.delete_message(chat_id, rec_message)
    except:
        pass
    
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.title_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_title
    get_title(m)


@bot.message_handler(
    state=States.record_event_date, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_title
    get_title(m)


@bot.message_handler(
    state=States.date_event_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_date
    get_date(m)


@bot.message_handler(
    state=States.record_event_start_time, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import clear_visitors_message
    clear_visitors_message(m)


@bot.message_handler(
    state=States.start_time_event_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_start_time
    get_start_time(m)


@bot.message_handler(
    state=States.record_event_end_time, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_start_time
    get_start_time(m)


@bot.message_handler(
    state=States.end_time_event_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_end_time
    get_end_time(m)


@bot.message_handler(
    state=States.record_count_students, 
    is_back_button_filter=True
    )
def go_back(m):
    
    
    
    from events_plan.record_event_module.record_event import get_end_time
    get_end_time(m)


@bot.message_handler(
    state=States.students_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_students_number
    get_students_number(m)


@bot.message_handler(
    state=States.record_count_visitors, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_students_number
    get_students_number(m)


@bot.message_handler(
    state=States.visitors_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_visitors_number
    get_visitors_number(m)


@bot.message_handler(
    state=States.record_place, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_date
    get_date(m)


@bot.message_handler(
    state=States.another_place, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import clear_visitors_message
    clear_visitors_message(m)


@bot.message_handler(
    state=States.place_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import clear_visitors_message
    clear_visitors_message(m)


@bot.message_handler(
    state=States.record_equipment, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_visitors_number
    get_visitors_number(m)


@bot.message_handler(
    state=States.eqipment_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_equipment
    get_equipment(m)


@bot.message_handler(
    state=States.record_seniors, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_equipment
    get_equipment(m)


@bot.message_handler(
    state=States.seniors_confirmation, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.record_event_module.record_event import get_seniors
    get_seniors(m)


# @bot.message_handler(
#     state=States.get_looking_place, 
#     is_back_button_filter=True
#     )
# def go_back(m):
#     from events_plan.events_plan_menu import get_calendar
#     get_calendar(m)


@bot.message_handler(
    state=States.choose_looking_period, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.choose_looking_day, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.looking_event_module.looking_plan import choose_period
    choose_period(m)


@bot.message_handler(
    state=States.choose_looking_month, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.looking_event_module.looking_plan import choose_period
    choose_period(m)


@bot.message_handler(
    state=States.get_looking_place, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.looking_event_module.looking_plan import choose_period
    choose_period(m)


@bot.message_handler(
    state=States.get_looking_date, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.looking_event_module.looking_plan import choose_period
    choose_period(m)


@bot.message_handler(
    state=States.edit_event, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.delete_event, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.get_looking_date_for_delete, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.get_events_for_delete, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.get_looking_date_for_edit, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.get_events_for_edit, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.editing_event, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.events_plan_menu import get_calendar
    get_calendar(m)


@bot.message_handler(
    state=States.editing_event_parameters, 
    is_back_button_filter=True,
    is_admin=False
    )
def go_back(m):
    from events_plan.edit_event_module.edit_event import show_events
    show_events(m)


@bot.message_handler(
    state=States.editing_event_parameters, 
    is_back_button_filter=True,
    is_admin=True
    )
def go_back(m):
    from events_plan.edit_event_module.edit_event import get_events_date_admin
    get_events_date_admin(m)


@bot.message_handler(
    state=edit_event_states, 
    is_back_button_filter=True
    )
def go_back(m):
    from events_plan.edit_event_module.edit_event import edit_selected_event
    edit_selected_event(m)


@bot.message_handler(
    state=States.deleting_event, 
    is_back_button_filter=True,
    is_admin=False
    )
def go_back(m):
    from events_plan.delete_event_module.delete_event import show_events
    show_events(m)


@bot.message_handler(
    state=States.deleting_event, 
    is_back_button_filter=True,
    is_admin=True
    )
def go_back(m):
    from events_plan.delete_event_module.delete_event import get_events_date_admin
    get_events_date_admin(m)
