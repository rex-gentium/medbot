import telebot
from dbworker import DbWorker
from settings import *

bot = telebot.TeleBot(bot_token)
dbworker = DbWorker()


@bot.message_handler(commands=["start"])
def cmd_start(message):
    user_id = message.chat.id
    dbworker.add_user(user_id)
    bot.send_message(user_id, "Привет! Вот список моих команд:\n"
                              "/start\n"
                              "/addmedication\n"
                              "/addprescription")


if __name__ == '__main__':
    bot.polling(none_stop=True)
