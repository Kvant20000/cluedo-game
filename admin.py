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
    gameList = [{'name' : 'cluedo V2', 'bot' : '@cluedo_agent_bot', 'status' : 'stopped'}]
    games = {'cluedo' : 'stopped'}
    ids = {'cluedo' : 303602093}
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
        bot.send_message(id, game['name'] + ': ' + game['bot']).wait()

        
@bot.message_handler(commands=['cluedo'], func=fromAdmin)
def startCluedo(message):
    print(message.text)
    if message.text == '/cluedo':
        bot.send_message(message.chat.id, ourGames.games['cluedo']).wait()
        return 
    else:
        action = message.text.replace('/cluedo ', '')
        if action == 'start':
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
        elif action == 'stop':
            if ourGames.games['cluedo'] == 'running':
               cluedo_main.botEnd(message)
            else:
                bot.send_message(message.chat.id, 'Already stopped')
            
            
@bot.message_handler(commands=['status'], func=fromAdmin)
def status(message):
    if message.text == '/status':
        info(message)
        return
    try:
        gm = message.text.replace('/status ', '')
        bot.send_message(message.chat.id, ourGames.games[gm]).wait()
    except:
        bot.send_message(message.chat.id, 'No such game').wait()

@bot.message_handler(commands=['full_end'])
def botEnd(message = None): #new
    if not (message.chat.id in AdminId):
        bot.send_message(message.chat.id, "Access denied!").wait()
        return
    else:
        sendAdmin('Admin bot ends')
        print('full end')
        exit(0)

@bot.message_handler(commands=['update'], func=fromAdmin)
def update_bot(message):
    os.system('git pull')
    sendAdmin('Git pull complete, restarting bot...')
    os.system('screen python3 admin.py')
        
@bot.message_handler()
def other(message):
    print(message.text, 'from', message.chat.username)

#send function    
def sendAdmin(text): #new
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text).wait()
    
#other function


ourGames = Game()    
sendAdmin('Admin bot starts')
bot.polling()
sendAdmin('Admin bot ends')