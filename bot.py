from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update
import logging

from constants import TOKEN


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def ping(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Pong')


dispatcher.add_handler(CommandHandler('ping', ping))

updater.start_polling()

