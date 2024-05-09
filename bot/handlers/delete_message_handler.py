from init_bot import bot
from bot_states import *


@bot.callback_query_handler(
    func=lambda call: 'close_message',
    state=States.state_list()
    )
def delete_message(call):
    try:
        chat_id = call.chat.id
    except:
        chat_id = call.message.chat.id
    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
