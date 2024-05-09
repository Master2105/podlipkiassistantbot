from telebot.handler_backends import State, StatesGroup


class States(StatesGroup):
    start = State()
    
    main_menu = State()
    
    bot_management = State()
    events_plan = State()
    
    record_new_event = State()
    edit_event = State()
    delete_event = State()
    record_new_event_confirmed = State()
    record_event_title = State()
    title_confirmation = State()
    record_event_date = State()
    date_event_confirmation = State()
    record_event_start_time = State()
    start_time_event_confirmation = State()
    record_event_end_time = State()
    end_time_event_confirmation = State()
    record_count_students = State()
    students_confirmation = State()
    record_count_visitors = State()
    visitors_confirmation = State()
    record_place = State()
    another_place = State()
    place_confirmation = State()
    record_equipment = State()
    eqipment_confirmation = State()
    record_seniors = State()
    seniors_confirmation = State()
    
    get_looking_date = State()
    get_looking_place = State()
    looking_place_confirmation = State()
    choose_looking_period = State()
    get_looking_date_info = State()
    choose_looking_day = State()
    choose_looking_month = State()
    
    get_looking_date_for_delete = State()
    get_looking_date_for_edit = State()
    get_events_for_delete = State()
    get_events_for_edit = State()
    choose_looking_period_for_edit = State()
    choose_looking_period_for_delete = State()
    get_looking_date_info_for_edit = State()
    get_looking_date_info_for_delete = State()
    deleting_event = State()
    editing_event = State()
    editing_event_parameters = State()
    
    edit_title = State()
    edit_title_confirmation = State()
    edit_date = State()
    edit_date_confirmation = State()
    edit_start_time = State()
    edit_start_time_confirmation = State()
    edit_end_time = State()
    edit_end_time_confirmation = State()
    edit_equipment = State()
    edit_equipment_confirmation = State()
    edit_place = State()
    edit_another_place = State()
    edit_place_confirmation = State()
    edit_students = State()
    edit_students_confirmation = State()
    edit_visitors = State()
    edit_visitors_confirmation = State()
    edit_seniors = State()
    edit_seniors_confirmation = State()
    
    delete_user = State()
    
    cancel_last_try = State()
    
    choose_group = State()
    
    append_id = State()
    
    calendar = State()
    
    name = State()
    surname = State()
    age = State()