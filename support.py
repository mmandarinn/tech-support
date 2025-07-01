import datetime
from email import message_from_bytes
from datetime import *
import telebot

bot = telebot.TeleBot('8027076864:AAH7kxdu6b4yvnX3DOW6sLGdQlm4-fFtZAw',skip_pending=True)

gr_id = str('-1002159656601')
last_time_dic = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Здравствуйте! Я бот для тех. поддержки команды SIGN, для обращения в поддержку подробно опишите проблему, возникшую в процессе работы с ботом, одним сообщением, приложив скриншот. Учтите, минимальное время между сообщениями в поддержку составляет 6 часов, относитесь с умом к вашим запросам. Постараемся ответить в кратчайшие сроки!')
    print(message.chat.id,'     ', message.from_user.username)
    last_time_dic[message.chat.id] = datetime.now()+timedelta(hours=-6)
#Продумать бан мут
@bot.message_handler(commands=['answer'])
def sup_ans(message):
    if gr_id in str(message.chat.id):
        try:
            us_id = message.reply_to_message.text[13:]
            bot.send_message(chat_id=us_id,text=f'Вам пришел ответ от тех. поддержки:\n\n{message.text[8:]}')
        except:
            bot.reply_to(message,'Произошла какая-то ошибка, проверьте что вы ответили на сообщение с указанием айди и написали /answer {ответ}')

@bot.message_handler(func=lambda message:True)
def sup(message):
    if not(gr_id in str(message.chat.id)):
        us_id = message.chat.id
        delta = datetime.now() - last_time_dic[message.chat.id]
        if delta.seconds >= 21600:
            bot.reply_to(message, 'Ваше сообщение передано в тех. поддержу, ожидайте ответа')
            bot.send_message(chat_id=gr_id, text=f'Сообщение от {us_id}:')
            bot.forward_message(gr_id,us_id,message.id)
            last_time_dic[message.chat.id] = datetime.now()
        else:
            bot.send_message(message.chat.id, 'Время между обращениями не может составлять менее 6 часов')



bot.polling()