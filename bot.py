from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
import logging

import smiles
from models import User, Question
from credentials import TOKEN
import util


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


name_state, surname_state, group_state, info_verification_state, ready_state, questions_state = range(6)
user = User()
# q_states = [i for i in range(12)]


def ping(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Pong')


def start(update: Update, context: CallbackContext):
    text = 'Введите ваше имя'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return name_state


def name(update: Update, context: CallbackContext):
    user.name = update.message.text
    context.user_data['name'] = update.message.text
    text = 'Введите вашу фамилию'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return surname_state


def surname(update: Update, context: CallbackContext):
    user.surname = update.message.text
    context.user_data['surname'] = update.message.text
    text = 'Введите вашу группу'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return group_state


def group(update: Update, context: CallbackContext):
    user.group = update.message.text
    context.user_data['group'] = update.message.text
    text = '{} {} {}. Всё верно?'.format(user.name, user.surname, user.group)
    buttons = [
        ['Да', 'Нет']
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
    return info_verification_state


def cancel(update: Update, context: CallbackContext):
    logger.info('User {} cancelled conversation')
    text = r'Текущий сеанс завершён, чтобы начать заново повторите команду /start'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    return ConversationHandler.END


def unknown(update: Update, context: CallbackContext):
    text = 'Я не знаю такой команды' + smiles.SAD
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def check_info(update: Update, context: CallbackContext):
    answer = update.message.text

    if answer == 'Да':
        text = 'Ознакомтесь с видеолекциями первой недели из данного курса https://openedu.ru/course/mipt/DATA_AN/'
        reply_markup = ReplyKeyboardMarkup([['Готов(а)']], one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)
        return ready_state
    elif answer == 'Нет':
        text = 'Начнём сначала. Введите имя'
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return name_state
    else:
        logger.error("Expected other answer, got:", answer)


def questions(update: Update, context: CallbackContext):
    if 'questions'not in context.bot_data:
        context.bot_data['questions'] = util.get_questions(path='personal/questions.txt')
    if 'iter' not in context.chat_data:
        context.chat_data['iter'] = 1
    quests = context.bot_data['questions']
    i = context.chat_data['iter']

    question = quests[i]
    buttons = [[j] for j in question.variants]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=question.text, reply_markup=reply_markup)
    context.chat_data['iter'] += 1
    return questions_state


def ready(update: Update, context: CallbackContext):
    if 'questions'not in context.bot_data:
        context.bot_data['questions'] = util.get_questions(path='personal/questions.txt')
    quests = context.bot_data['questions']
    question = quests[0]
    buttons = [[i] for i in question.variants]
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=question.text, reply_markup=reply_markup)
    return questions_state


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points={
            CommandHandler('start', start)
        },

        states={
            name_state: [MessageHandler(Filters.text & ~Filters.command, name)],
            surname_state: [MessageHandler(Filters.text & ~Filters.command, surname)],
            group_state: [MessageHandler(Filters.text & ~Filters.command, group)],
            info_verification_state: [MessageHandler(Filters.text & ~Filters.command, check_info)],
            ready_state: [MessageHandler(Filters.text & ~Filters.command, ready)],
            questions_state: [MessageHandler(Filters.text & ~Filters.command, questions)]
        },

        fallbacks={
            CommandHandler('cancel', cancel)
        }
    )
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

