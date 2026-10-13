from datetime import timedelta, datetime
import telebot

#Инициализация бота, необходимо вставить токен в кавычки
bot = telebot.TeleBot('',skip_pending=True)

support_chat_id = str('') #ID чата через который происходит взаимодействие
last_request_time = {} #История времени обращения в поддержку {id_пользователя : время_последнего_сообщения}
banned_users = [] #Список ID заблокированных пользователей

# === ОБРАБОТЧИК КОМАНДЫ /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Здравствуйте! Я бот для тех. поддержки команды SIGN, для обращения в поддержку подробно опишите проблему, возникшую в процессе работы с ботом, одним сообщением, приложив скриншот. Учтите, минимальное время между сообщениями в поддержку составляет 6 часов, относитесь с умом к вашим запросам. Постараемся ответить в кратчайшие сроки!')
    print(message.chat.id,'     ', message.from_user.username) #вывод новых пользователей в консоль(не обязательно)

# === ОБРАБОТЧИК ОТВЕТОВ ПОДДЕРЖКИ (/answer) ===
@bot.message_handler(commands=['answer'])
def sup_ans(message):
    #Проверяем, что сообщение отправлено из чата поддержки
    if support_chat_id in str(message.chat.id):
        #Получаем ID пользователя из сообщения, на которое отвечаем
        us_id = str(message.reply_to_message.text[13:])
        try:
            #Отправляем сообщение с ответом пользователю
            bot.send_message(chat_id=us_id,text=f'Вам пришел ответ от тех. поддержки:\n\n{message.text[8:]}')
            bot.reply_to(message, 'Отправлено')
            #Сбрасываем время последнего взаимодействия, чтобы человек мог сразу обратиться снова
            last_request_time[us_id] = datetime.now() + timedelta(hours=-6)
        except:
            bot.reply_to(message,'Произошла какая-то ошибка, проверьте что вы ответили на сообщение с указанием айди и написали /answer {ответ}')

# === СИСТЕМА БАНА ПОЛЬЗОВАТЕЛЕЙ (/ban) ===
@bot.message_handler(commands=['ban'])
def ban(message):
    #блокирует пользователя в боте, выполняется ответом на сообщение с ID
    try:
        if str(message.chat.id) == support_chat_id:
            banned_users.append(message.reply_to_message.text[13:])
            bot.send_message(message.chat.id, 'Забанен')
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка, убедитесь что вы ответили на сообщение с указанием айди пользователя нужной вам командой')

# === СИСТЕМА РАЗБАНА ПОЛЬЗОВАТЕЛЕЙ (/unban) ===
@bot.message_handler(commands=['unban'])
def ban(message):
    #разблокирует пользователя в боте, выполняется ответом на сообщение с ID
    try:
        if str(message.chat.id) == support_chat_id:
            banned_users.remove(message.reply_to_message.text[13:])
            bot.send_message(message.chat.id, 'Разбанен')
    except:
        bot.send_message(message.chat.id, 'Произошла ошибка, убедитесь что вы ответили на сообщение с указанием айди пользователя нужной вам командой')

# === ОБРАБОТЧИК ВХОДЯЩИХ ЗАПРОСОВ ===
@bot.message_handler(func=lambda message:True)
def sup(message):
    #Проверка наличия пользователя в бан листе
    if str(message.chat.id) in banned_users:
        bot.send_message(message.chat.id, 'Отказано в доступе. Вас заблокировал администратор')
    else:
        us_id = str(message.chat.id)    #Получение ID пользователя
        if not('-' in us_id):    #Проверка, что сообщение из личного чата
            #Если пользователь пишет впервые создаем запись с последним временем посещения 6 часов назад, чтобы был доступ к сообщению
            if not(us_id in last_request_time):
                last_request_time[us_id] = datetime.now() + timedelta(hours=-6)
            #Считаем как давно было последнее обращение
            delta = datetime.now() - last_request_time[us_id]
            #Если больше чем 6 часов назад, отправляем заявку в поддержку
            if delta.seconds >= 21600:
                #Сообщаем пользователю, что его заявка отправлена
                bot.reply_to(message, 'Ваше сообщение передано в тех. поддержу, ожидайте ответа')
                #Отправляем сообщение с ID в чат поддержки
                bot.send_message(chat_id=support_chat_id, text=f'Сообщение от {us_id}')
                #Пересылаем сообщение пользователя
                bot.forward_message(support_chat_id,us_id,message.id)
                #Обновляем время последнего взаимодействия до нынешнего момента
                last_request_time[us_id] = datetime.now()
            else:
                bot.send_message(message.chat.id, 'Время между обращениями не может составлять менее 6 часов')


#Постоянный опрос серверов телеграм (Бот активен)
bot.polling()