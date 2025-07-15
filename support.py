import datetime
from datetime import *
import telebot

bot = telebot.TeleBot('',skip_pending=True)

gr_id = str('') #айди чата поддержки
last_time_dic = {} #словарь для сохранения времени взаимодействия
ban_list = [] #список забаненых людей

#обработка старта
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Здравствуйте! Я бот для тех. поддержки команды SIGN, для обращения в поддержку подробно опишите проблему, возникшую в процессе работы с ботом, одним сообщением, приложив скриншот. Учтите, минимальное время между сообщениями в поддержку составляет 6 часов, относитесь с умом к вашим запросам. Постараемся ответить в кратчайшие сроки!')
    print(message.chat.id,'     ', message.from_user.username) #вывод новых пользователей в консоль(не обязательно)

#обработка ответа от поддержки
@bot.message_handler(commands=['answer'])
def sup_ans(message):
    if gr_id in str(message.chat.id):
        us_id = str(message.reply_to_message.text[13:])     #айди пользователя
        try:
            bot.send_message(chat_id=us_id,text=f'Вам пришел ответ от тех. поддержки:\n\n{message.text[8:]}')
            bot.reply_to(message, 'Отправлено')
            last_time_dic[us_id] = datetime.now() + timedelta(hours=-6) #обновление данных чтобы пользователь снова мог обратиться в поддержку
        except:
            bot.reply_to(message,'Произошла какая-то ошибка, проверьте что вы ответили на сообщение с указанием айди и написали /answer {ответ}')

#система бана
@bot.message_handler(commands=['ban'])
def ban(message):
    try:
        if str(message.chat.id) == gr_id:
            ban_list.append(message.reply_to_message.text[13:])
            bot.send_message(message.chat.id, 'Забанен')
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка, убедитесь что вы ответили на сообщение с указанием айди пользователя нужной вам командой')

#система разбана
@bot.message_handler(commands=['unban'])
def ban(message):
    try:
        if str(message.chat.id) == gr_id:
            ban_list.remove(message.reply_to_message.text[13:])
            bot.send_message(message.chat.id, 'Разбанен')
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка, убедитесь что вы ответили на сообщение с указанием айди пользователя нужной вам командой')

#обработка запросов в поддержку
@bot.message_handler(func=lambda message:True)
def sup(message):
    if str(message.chat.id) in ban_list:
        bot.send_message(message.chat.id, 'Отказано в доступе')
    else:
        us_id = str(message.chat.id)    #айди пользователя
        if not('-' in str(message.chat.id)):    #проверка чтобы нельзя было писать из групп
            if not(us_id in last_time_dic):
                last_time_dic[us_id] = datetime.now() + timedelta(hours=-6)
            delta = datetime.now() - last_time_dic[us_id]
            if delta.seconds >= 21600:
                bot.reply_to(message, 'Ваше сообщение передано в тех. поддержу, ожидайте ответа')
                bot.send_message(chat_id=gr_id, text=f'Сообщение от {us_id}')
                bot.forward_message(gr_id,us_id,message.id)
                last_time_dic[us_id] = datetime.now()
            else:
                bot.send_message(message.chat.id, 'Время между обращениями не может составлять менее 6 часов')



bot.polling()