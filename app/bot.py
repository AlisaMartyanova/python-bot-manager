import telebot
from threading import Thread

bots = dict()


# create and launch new bot by given token
def run_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, f'Print something, {message.from_user.first_name}')

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        bot.send_message(message.from_user.id, message.text)

    bots[token] = bot

    bot.polling(none_stop=True)


# start new thread with bot
def start(token):
    bot = bots.get(token, None)
    if bot is None:
        Thread(target=run_bot, args=(token, )).start()


# shut down existing bot
def stop(token):
    bot = bots.get(token, None)
    if bot:
        bot.stop_bot()
        bots.pop(token)
