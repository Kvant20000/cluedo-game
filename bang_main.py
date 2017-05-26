# -*- coding: utf-8 -*-
import telebot
import time
import sys
import os
import datetime
import random as rd
from copy import deepcopy
import cfg
import threading


TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN_2 = "286496122:AAGED92TDcccXHGJmgyz5oJcCcZ4TI-vTrM"
MAX_GAMES = 10

###
bot = telebot.TeleBot(TOKEN_2)
###

AdminId = [186898465, 319325008]
Admins = [telebot.types.User(id=186898465, username='TwoBlueCats', first_name='Anton', last_name='Anikushin'),
          telebot.types.User(id=319325008, username='greatkorn', first_name='Anton', last_name='Kvasha')]

common_cards = ["bang", "miss", "bear", "saloon", "shop", "take", "panic", "tnn", "duel", "gatling", "indeans"]
special_cards = ["weapon", "mustang", "zoom", "barrel", "prison", "dynamite"]

deck = []
used = []

class Card:
    def __init__(self, arr):
        self.card_use, self.value, self.type = arr

    def use_card(self):
        pass


class Player:
    def __init__(self, User):
        self.id = User.id
        self.username = User.username
        self.first_name = User.first_name
        self.last_name = User.last_name

        self.cards = []
        self.number = -1
        self.user = User
        self.person = 'observer'
        self.mx_hp = 4
        self.hp = 4

    def __str__(self):
        if str(self.username) == '':
            return str(self.first_name) + ' ' + str(self.last_name)
        else:
            return str(self.username)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def check(self):
        if self.username is None:
            self.username = ''
        if self.first_name is None:
            self.first_name = ''
        if self.last_name is None:
            self.last_name = ''

    def setUser(self, User):
        self.user = User
        self.id = User.id
        self.username = User.username
        self.first_name = User.first_name
        self.last_name = User.last_name

    def setNumber(self, num):
        self.number = num

    def setPerson(self, name):
        self.person = name

    def setCards(self, cards):
        self.cards = deepcopy(cards)

    def addCard(self, card):
        self.cards.append(card)

    def delCard(self, card):
        self.cards.pop(self.cards.index(card))

    def addActive(self, cards):
        self.active.append(card)

    def delActive(self, cards):
        self.active.pop(self.active.index(card))

    def cardsInHand(self):
        return ', '.join(self.cards)


class Game:
    def __init__(self):
        self.id = int(rd.random() * 10 ** 30)

        self.max_players = 7
        self.started = False
        self.end = False

        self.players = []


    def add_player(self, P):
        self.players += [p]


    def start(self):
        self.deck = 50 * ["bang"] + 50 * ["miss"]
        rd.shuffle(self.deck)
        self.n = len(self.players)
        rd.shuffle(self.players)

        rest = cfg.bang_roles[:self.n]
        self.roles = cfg.bang_roles[:self.n]
        last = 0
        for i in range(self.n):
            pl = self.players[i]
            pl.setNumber(i)
            pl.setPerson(rd.choice(rest))
            rest.pop(rest.index(pl.person))
            if pl.person == 'the Sheriff':
                self.now = i
                pl.mx_hp += 1
                pl.hp += 1
            pl.setCards(deck[last:last + pl.mx_hp])
            last += pl.mx_hp


    def game(self):
        while not self.end:
            while not self.players[self.now].alive:
                self.now = (self.now + 1) % self.n

            self.end = self.turn()

            self.now = (self.now + 1) % self.n
        return

    def turn(self):
        print("Now it is player № " + str(self.now) + ' turn')
        return False
        #'return True' if game is finished

@bot.message_handler(command=['join'])
def addPlayer(message):
    global game
    pl = Player(message.from_user)
    if game.started:
        bot.send_message(pl.id, "game had already started")
        return
    if pl in game.players:
        bot.send_message(pl.id, "you are already in the game")
        return
    
    game.add_player(pl)
    bot.send_message(pl.id, "you join the game")
    send_all(str(pl) + ' join our game', bad = [pl])

    
@bot.message_handler(command=['game'])
def startGame(message):
    sendAdmin("pre-game init")
    game.start()
    sendAdmin("main loop starts")
    game.game()
    
def send_all(msg, bad=[]):
    for player in game.players:
        if player.id not in bad:
            bot.send_message(player.id, msg)
    return


def sendAdmin(text):
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)


def send_turn(pl):
    for player in game.players:
        bot.send_message(player.id, "Now it's " + str(pl) + "'s turn")
    return

def logName():
    log = "bang logs "
    today = time.gmtime()
    year = str(today.tm_year)
    month = str(today.tm_mon)
    day = str(today.tm_mday)
    hour = str(today.tm_hour)
    minute = str(today.tm_min)
    seconds = str(today.tm_sec)
    log += str(year) + '.' + str(month) + '.' + str(day) + ' ' + str(hour) + ';' + str(minute) + ';' + str(
        seconds) + '.txt'
    return log


def main():
    global file_name, game
    cfg.bang_init()
    file_name = logName()
    loggs = open(file_name, "w")
    loggs.close()
    games = []
    game = Game()
    sendAdmin('Bot starts')
    bot.polling()


if __name__ == '__main__':
    main()

print(__name__)
