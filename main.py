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

    def killed(self):
        return self.ans

    def cards(self, person):
        s = "Открытые карты: " + ', '.join(self.opencrds) + '\n'
        s += "Ваши карты: " + str(self.players[person]) + '\n'
        return s


players = []
now_chosen = []
FINISHED = False
GAME = None
d = dict()
active = []

bot = telebot.TeleBot(TOKEN)
my_ans = ''

def go(index):
    global my_ans
    my_ans = ''
    man = (index + 1) % len(GAME.players)
    while answer(man) and man != index:
        man = (man + 1) % len(GAME.players)
    if man == index:
        send_all('Nobody can help!!!')
    else:
        bot.send_message(players[index][0], my_ans + ' from ' + players[man][1])
        send_all('Answered by ' + players[man][1])
    
    
def answer(man):
    global my_ans
    id = players[man][0]
    Pl = GAME.players[man]
    cards = set(Pl.cards)
    now = set(now_chosen)
    inter = now.intersection(cards)
    
    print(inter)
    
    if len(now.intersection(cards)) == 0:
        bot.send_message(id, "Choose answer: ", reply_markup = make(['NO']))
        while len(my_ans) == 0:
            pass
        return False
    else:
        bot.send_message(id, "Choose answer: ", reply_markup = make(list(inter)))
        while len(my_ans) == 0:
            pass
        return True

@bot.message_handler(commands=['play'])
def get_players(message):
    global players
    Id = message.chat.id
    user = message.chat.username
    if len(players) > 5 and FINISHED:
        msg = bot.send_message(message.chat.id, "Sorry, no empty places!")
    elif (Id, user) not in players:
        players.append((Id, user))
        msg = bot.send_message(message.chat.id, "Welcome to the game, {0}!".format(user))
    print(players)


@bot.message_handler(commands=['start'])
def start_game(message):
    global FINISHED
    global GAME
    global d
    global active
    if FINISHED:
        msg = bot.send_message(message.chat.id, "Game has already started")
    else:
        active = [True] * len(players)
        FINISHED = True
        print(players)
        GAME = Game(len(players))
        rd.shuffle(players)
        place = 0
        for elem in players:
            d[elem[0]] = place
            place += 1
        for player in players:
            msg = bot.send_message(player[0], GAME.cards(d[player[0]]))
        print(d, active)
       
        
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
    go(d[message.chat.id])


@bot.message_handler(commands=['accuse'])
def accuse(message):
    print("WAAAT?")
    global now_chosen
    global active
    now_chosen = []
    bot.send_message(message.chat.id, "Choose person: ", reply_markup=make(people))
    while len(now_chosen) != 1:
        pass
    bot.send_message(message.chat.id, "Choose weapon: ", reply_markup=make(weapons))
    while len(now_chosen) != 2:
        pass
    bot.send_message(message.chat.id, "Choose place: ", reply_markup=make(places))
    while len(now_chosen) != 3:
        pass
    if check_ans(now_chosen):
        send_all(players[d[message.chat.id]][1] + " won!")
    else:
        active[d[message.chat.id]] = False
        send_all(players[d[message.chat.id]][1] + " didn't guess correct! He's out of game!")


@bot.message_handler()
def tmp(message):
    global now_chosen, my_ans
    if message.text in now_chosen or message.text == 'NO':
        my_ans = message.text
        
    if message.text in people + weapons + places:
        now_chosen += [message.text]
    return


def check_ans(arr):
    return sorted(GAME.killed()) == sorted(arr)


def send_all(msg):
    for player in players:
        bot.send_message(player[0], msg)
    return


bot.polling()
