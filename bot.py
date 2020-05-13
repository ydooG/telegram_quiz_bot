from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from telegram import Update
import logging
import smiles

from credentials import TOKEN


updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)


def ping(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Pong')


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def unknown(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Такую команду я не знаю" + smiles.SAD)


dispatcher.add_handler(CommandHandler('ping', ping))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.start_polling()

