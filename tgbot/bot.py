from telegram import ReplyKeyboardMarkup, Message
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

from settings import API_TOKEN
from parse_tools import get_search_list

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Поиск']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update: Message, context):
    update.message.reply_text(
        "Приветвую, я бот ебать его в рот могу искать госты по ихх ебанному номеру. "
        "Нахуя это надо? Просто так нахуй",
        reply_markup=markup)

    return CHOOSING


def search_gost(update, context):
    text = update.message.text
    context.user_data['search_string'] = text
    update.message.reply_text(
        'Введите номер(часть номера) для поиска')

    return TYPING_REPLY


def custom_choice(update, context):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(update, context):
    user_data = context.user_data
    text = update.message.text
    gost_list = get_search_list(user_data['search_string'])

    del user_data['search_string']
    for gost in gost_list:
        update.message.reply_text(gost[0] +
                                  '\n' +
                                  gost[1],
                              reply_markup=markup)

    return CHOOSING


def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    user_data.clear()
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(API_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Поиск)$'),
                                      search_gost)
                       ],

            TYPING_CHOICE: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               search_gost)],

            TYPING_REPLY: [
                MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')),
                               received_information)],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)]
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()