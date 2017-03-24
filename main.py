# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import datetime

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands = ['hello'])
def send_msg(message):
    print(message.chat.id)
    msg = bot.send_message('@greatkorn', "Tuc Tuc")

bot.polling()
