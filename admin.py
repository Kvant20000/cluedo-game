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
import cluedo_main

TOKEN = "355967723:AAG4x935upwWEt-Ne_72Tx1L_W0vUMGINiI"

AdminId = [186898465, 319325008]
Admins = [telebot.types.User(id = 186898465, username = 'antonsa', first_name = 'Anton', last_name = 'Anikushin'), telebot.types.User(id = 319325008, username = 'greatkorn', first_name = 'Anton', last_name = 'Kvasha')]

bot = telebot.TeleBot(TOKEN)

class Game():
    titles = ['cluedo V1', 'cluedo V2']
    gameList = [{'name' : 'cluedo V2', 'bot' : '@cluedo_agent_bot', 'status' : 'stopped'}, 
                {'name' : 'cluedo V1', 'bot' : '@try_masha_bot', 'status' : 'stopped'}]
    games = {'cluedo' : 'stopped'}
    def __init__(self):
        pass
    
def fromAdmin(message):
    return message.chat.id in AdminId

    
@bot.message_handler(commands=['start', 'games', 'game', 'help'], func=fromAdmin)
def info(message):
    id = message.chat.id
    for game in ourGames.gameList:
        bot.send_message(id, game['name'] + ': ' + game['bot'] + '  ' + game['status'])

@bot.message_handler(commands=['help', 'start'])        
def help(message):
    id = message.chat.id
    bot.send_message("List of Antons' games")
    for game in gameList:
        bot.send_message(id, game['name'] + ': ' + game['bot'])

        
@bot.message_handler(commands=['cluedo'], func=fromAdmin)
def startCluedo(message):
    print(message.text)
    sendAdmin(str(message.chat.id) + ' starts cluedo main bot')
    ourGames.gameList[0]['status'] = 'running'
    ourGames.games['cluedo'] = 'running'
    
    try:
        cluedo_main.main()
    except:
        sendAdmin('Cluedo main bot falls down')
    sendAdmin('Cluedo main bot ends')
    ourGames.gameList[0]['status'] = 'stopped'
    ourGames.games['cluedo'] = 'stopped'

    
@bot.message_handler(commands=['status'], func=fromAdmin)
def status(message):
    if message.text == '/status':
        info(message)
        return
    try:
        gm = message.text.replace('/status ', '')
        bot.send_message(message.chat.id, ourGames.games[gm])
    except:
        bot.send_message(message.chat.id, 'No such game')
    
@bot.message_handler()
def other(message):
    print(message.text, 'from', message.chat.username)

#send function    
def sendAdmin(text): #new
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)
    
#other function


ourGames = Game()    
sendAdmin('Admin bot starts')
bot.polling()
sendAdmin('Admin bot ends')