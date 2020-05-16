from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler, \
    CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    ParseMode
import logging

import smiles
from models import User, Question
from credentials import TOKEN
import util, gsheet_util as gsheet


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


name_state, surname_state, group_state, info_verification_state, ready_state, questions_state, finish_state = range(7)
user = User()


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
    context.chat_data['iter'] = 1
    gsheet.write_user(user)
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


def ready(update: Update, context: CallbackContext):
    if 'questions'not in context.bot_data:
        context.bot_data['questions'] = util.get_questions(path='personal/questions.txt')
    quests = context.bot_data['questions']
    question = quests[0]
    text = get_question_text(question)
    buttons = util.get_letter_variants(len(question.variants))
    reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=reply_markup,
                             parse_mode=ParseMode.HTML)
    return questions_state


def get_question_text(q: Question):
    letters = util.LETTERS
    text = "<i>" + q.text + "</i>"
    ending = '\n' if any(len(variant) > 30 for variant in q.variants) else ""
    for i in range(len(q.variants)):
        text += "\n" + letters[i] + ". " + q.variants[i] + str(ending)
    return text


# state
def questions(update: Update, context: CallbackContext):
    if 'questions'not in context.bot_data:
        context.bot_data['questions'] = util.get_questions(path='personal/questions.txt')
    if 'iter' not in context.chat_data:
        context.chat_data['iter'] = 1
    quests = context.bot_data['questions']
    i = context.chat_data['iter']
    logger.info(i)
    answer = update.message.text
    logger.info(str(util.LETTERS.index(answer)) + ":" + str(quests[i-1].answer_index))
    if util.LETTERS.index(answer) == quests[i - 1].answer_index:
        user.points += 1
    user.answers.append(answer)

    if i >= len(quests):
        logger.info('Now i = 14')
        finish(update, context)
        return ConversationHandler.END
    else:
        question = quests[i]
        text = get_question_text(question)
        buttons = util.get_letter_variants(len(question.variants))
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=text, reply_markup=reply_markup,
                                 parse_mode=ParseMode.HTML)
        context.chat_data['iter'] += 1
        return questions_state


def finish(update: Update, context: CallbackContext):
    context.chat_data['iter'] = 1
    text = 'Тест завершен'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ReplyKeyboardRemove())
    gsheet.write_user(user)


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
    dispatcher.add_handler(CommandHandler('ping', ping))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    while True:
        try:
            updater.start_polling()
        except Exception as ex:
            logger.error(ex)


if __name__ == '__main__':
    main()

