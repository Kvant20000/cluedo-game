# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import datetime
import random as rd

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"

am_open = [0, 0, 0, 0, 2, 3, 0]  # other option is [0, 0, 0, 6, 6, 3, 6]
people = ["Ворона", "Берёза", "Князь Пожарский", "Васечка", "Афганский мафиози", "СВ"]  # КТО?
weapons = ["Тихим Доном", "клавиатурой", "выносом мозга", "тупыми мемами", "коробкой из-под пиццы",
           "огнетушителем"]  # ЧЕМ?
places = ["в 209", "у психолога", "в Маке", "на футбольном поле", "в электричке", "в актовом зале", "в ТЦ Охотный",
          "у выхода из метро", "в офисе 1С"]  # ГДЕ?


class Player:
    def __init__(self, A):
        self.cards = A

    def __str__(self):
        return ', '.join(self.cards)


class Game:
    def __init__(self, n):  # n players
        self.ans = (rd.choice(people), rd.choice(weapons), rd.choice(places))  # the answer

        deck = people + weapons + places
        for i in self.ans:
            deck.remove(i)
        rd.shuffle(deck)  # so i shuffled

        self.opencrds = deck[:am_open[n]]
        am_per_player = (len(deck) - am_open[n]) // n
        self.players = [Player(deck[i: i + am_per_player]) for i in range(am_open[n], len(deck), am_per_player)]

    def kill(self):
        return self.ans()

    def cards(self, person):
        s = "Открытые карты: " + ', '.join(self.opencrds) + '\n'
        s += "Ваши карты: " + str(self.players[person]) + '\n'
        return s


players = []
now_chosen = []
FINISHED = False
GAME = None

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['play'])
def get_players(message):
    global players
    Id = message.chat.id
    user = message.chat.username
    if len(players) > 5 and FINISHED:
        msg = bot.send_message(message.chat.id, "Sorry, no empty places!")
    if (Id, user) not in players:
        players.append((Id, user))
    msg = bot.send_message(message.chat.id, "Welcome to the game, {0}!".format(user))
    print(players)


@bot.message_handler(commands=['start'])
def start_game(message):
    global FINISHED
    global GAME
    if FINISHED:
        msg = bot.send_message(message.chat.id, "Game has already started")
    else:
        FINISHED = True
        print(players)
        GAME = Game(len(players))
        rd.shuffle(players)
        d = dict()
        place = 0
        for elem in players:
            d[elem[0]] = place
            place += 1
        for player in players:
            msg = bot.send_message(player[0], GAME.cards(d[player[0]]))


def make(arr):
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True)
    for elem in arr:
        now.add(telebot.types.KeyboardButton(elem))
    return now


@bot.message_handler(commands=['ask'])
def ask(message):
    global now_chosen
    now_chosen = []
    bot.send_message(message.chat.id, "Choose person: ", reply_markup = make(people))
    while len(now_chosen) != 1:
        pass
    bot.send_message(message.chat.id, "Choose weapon: ", reply_markup = make(weapons))
    while len(now_chosen) != 2:
        pass
    bot.send_message(message.chat.id, "Choose place: ", reply_markup = make(places))
    while len(now_chosen) != 3:
        pass
    bot.send_message(message.chat.id, "Your choise is: " + ', '.join(now_chosen))


@bot.message_handler()
def tmp(message):
    global now_chosen
    if message.text in people + weapons + places:
        now_chosen += [message.text]



bot.polling()
