from abc import ABC
from telebot.handler_backends import State
from telebot.custom_filters import SimpleCustomFilter, AdvancedCustomFilter
from telebot import types
import os
import sqlite3 as sl
from secrets import db


class AccessFilter(SimpleCustomFilter):
    key = "is_access"
    
    def check(self, m):        
        try:
            chat_id = m.chat.id
        except:
            chat_id = m.message.chat.id
        
        con = sl.connect(db)
        
        with con:
            try:
                info = con.execute('SELECT * FROM staff WHERE telegram_id=?', (chat_id, )).fetchone()
                if info is not None: 
                        return True
                else:
                        return False
            except Exception as e:
                print(e)


class AdminFilter(SimpleCustomFilter):
    key = "is_admin"
    
    def check(self, m):        
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
        
        
class MainMenuFilter(SimpleCustomFilter):
    key = "is_main_menu"
    
    def check(self, m):
        if m.text.lower() == "в главное меню":
            return True


class BotManagementFilter(SimpleCustomFilter):
    key = "is_management_menu"
    
    def check(self, m):
        if m.text.lower() == "управление ботом":
            return True


class EventsPlantFilter(SimpleCustomFilter):
    key = "is_events_plan_menu"
    
    def check(self, m):
        massive = ["план мероприятий", "назад к плану"]
        if m.text.lower() in massive:
            return True
        else:
            return False


class LookPlanFilter(SimpleCustomFilter):
    key = "is_looking_plan"
    
    def check(self, m):
        massive = ["посмотреть план", "ознакомиться"]
        if m.text.lower() in massive:
            return True


class NewEventFilter(SimpleCustomFilter):
    key = "is_new_event"
    
    def check(self, m):
        if m.text.lower() == "создать мероприятие":
            return True


class NewEventConfirmedFilter(SimpleCustomFilter):
    key = "is_new_event_confirmed"
    
    def check(self, m):
        if m.text.lower() == "подтверждаю":
            return True


class EditEventFilter(SimpleCustomFilter):
    key = "is_edit_event"
    
    def check(self, m):
        if m.text.lower() == "изменить мероприятие":
            return True


class DeleteEventFilter(SimpleCustomFilter):
    key = "is_delete_event"
    
    def check(self, m):
        if m.text.lower() == "удалить мероприятие":
            return True


class RecordNewUserFilter(SimpleCustomFilter):
    key = "is_recording_user"
    
    def check(self, m):
        if m.text.lower() == "зарегистрировать пользователя":
            return True


class DeleteUserFilter(SimpleCustomFilter):
    key = "is_deleting_user"
    
    def check(self, m):
        if m.text.lower() == "удалить пользователя":
            return True


class CancelLastTryFilter(SimpleCustomFilter):
    key = "is_cancel_try"
    
    def check(self, m):
        if m.text.lower() == "отменить незавершённую попытку записи":
            return True


class BackButtonFilter(SimpleCustomFilter):
    key = "is_back_button_filter"
    
    def check(self, m):
        if m.text.lower() == "назад":
            return True
        else:
            return False


class CancelButtonFilter(SimpleCustomFilter):
    key = "is_cancel_button_filter"
    
    def check(self, m):
        if m.text.lower() == "отменить запись":
            return True
        else:
            return False


class ExportDBFilter(SimpleCustomFilter):
    key = "is_export_base_msg"
    
    def check(self, m):
        if m.text.lower() == "экспорт базы":
            return True
