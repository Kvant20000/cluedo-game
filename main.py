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
    print(message.chat.id, message.chat.username)
    msg = bot.send_message(message.chat.id, "Tuc Tuc")

bot.polling()
