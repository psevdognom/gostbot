from telebot import TeleBot

from .settings import API_TOKEN

bot = TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Введите номер госта для поиска')


bot.poll()
