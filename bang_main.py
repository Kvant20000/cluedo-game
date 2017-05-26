# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import sys
import os
import datetime
import random as rd
from copy import deepcopy
import cfg
import threading
from cfg import BangCard as Card

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "286496122:AAGED92TDcccXHGJmgyz5oJcCcZ4TI-vTrM"
MAX_GAMES = 10

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
    def __init__(self, User = None):
        self.cards = []
        self.number = number
        self.user = User
        self.person = 'observer'
        self.id = User.id
        self.username = User.username
        self.first_name = User.first_name
        self.last_name = User.last_name
    
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
        self.won = False

        self.players = []

    def add_player(self, P):
        self.players += [p]

    def start(self):
        deck = 50 * ["bang"] + 50 * ["miss"]

        

def main():
    global file_name, game
    cfg.cluedo_init()
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
