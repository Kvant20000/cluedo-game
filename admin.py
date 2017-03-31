# -*- coding: utf-8 -*-
import telebot
from telebot import types
import logging
import colorlog
import emoji
import time
import sys
import datetime
import random as rd
import os

TOKEN = "355967723:AAG4x935upwWEt-Ne_72Tx1L_W0vUMGINiI"

AdminId = [186898465]#, 319325008]
Admins = [telebot.types.User(id = 186898465, username = 'antonsa', first_name = 'Anton', last_name = 'Anikushin')]#, telebot.types.User(id = 319325008, username = 'greatkorn', first_name = 'Anton', last_name = 'Kvasha')]

bot = telebot.TeleBot(TOKEN)

gameList = [{'name' : 'cluedo V1', 'bot' : '@cluedo_agent_bot'}, {'name' : 'cluedo v2', 'bot' : '@try_masha_bot'}]

class Game():
    titles = ['cluedo V1', 'cluedo V2']
    paths = {'cluedo' : 'refactor.py'}
    def __init__(self):
        pass
    
def fromAdmin(message):
    return message.chat.id in AdminId

    
@bot.message_handler(commands=['start', 'games', 'game', 'help'])
def help(message):
    print(message.text)
    id = message.chat.id
    for game in gameList:
        bot.send_message(id, game['name'] + ': ' + game['bot'])


@bot.message_handler(commands=['cluedo'], func=fromAdmin)
def startCluedo(message):
    sendAdmin(message.chat.username + ' starts cluedo support bot')
    os.system('C:\\python34\\python.exe ' + paths[cluedo])
    sendAdmin('Cluedo support bot ends')

@bot.message_handler()
def other(message):
    print(message.text, 'from', message.chat.username)

#send function    
def sendAdmin(text): #new
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)
    
#other function


    
sendAdmin('Admin bot starts')
bot.polling()
