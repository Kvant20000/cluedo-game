# -*- coding: utf-8 -*-
import telebot

TOKEN2 = # TOKEN HERE

bot = telebot.TeleBot(TOKEN2)
myID = # admin id


@bot.message_handler(commands=['help'])
def resell(message):
    bot.send_message(message.chat.id,
                     '''
1: отрежем лист, граф более, чем полный, значит все плохо
2: нет, так как должно быть больше вершин
3: от противного, есть компонента с <= 8 вершин, все плохо
4: 2^(n-1) * 2^(n-1), где n - расстояние до листьев
5: что-то там через индукцию вроде как
6: любой срез хотя бы n ребер
7: вообще нет идей
''')


while True:
    try:
        bot.polling()
    except Exception as error:
        print(str(error))
