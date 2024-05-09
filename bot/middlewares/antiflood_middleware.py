from telebot.handler_backends import BaseMiddleware, CancelUpdate
from init_bot import bot


class SimpleMiddleware(BaseMiddleware):
    def __init__(self, limit) -> None:
        self.last_time = {}
        self.limit = limit
        self.update_types = ['message', 'call']
        # Always specify update types, otherwise middlewares won't work


    def pre_process(self, message, data):
        try:
            chat_id = message.chat.id
        except:
            chat_id = message.message.chat.id
        
        if not message.from_user.id in self.last_time:
            # User is not in a dict, so lets add and cancel this function
            self.last_time[message.from_user.id] = message.date
            return
        if message.date - self.last_time[message.from_user.id] < self.limit:
            # User is flooding
            bot.send_message(chat_id, 'Сообщения приходят слишком часто. Попробуйте медленее')
            return CancelUpdate()
        self.last_time[message.from_user.id] = message.date

        
    def post_process(self, message, data, exception):
        pass