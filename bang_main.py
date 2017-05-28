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

common_cards = ["bang", "miss", "beer", "saloon", "shop", "draw", "panic", "tnn", "duel", "gatling", "indeans"]
special_cards = ["weapon", "mustang", "zoom", "barrel", "prison", "dynamite"]

personToGame = dict()


class Card:
    def __init__(self, arr):
        self.card_use, self.value, self.type = arr

    def useCard(self):
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
        self.status = 1

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
        used.push_back(self.cards[self.cards.index(card)])
        self.cards.pop(self.cards.index(card))

    def addActive(self, cards):
        self.active.append(card)

    def delActive(self, cards):
        used.push_back(self.cards[self.cards.index(card)])
        self.active.pop(self.active.index(card))

    def cardsInHand(self):
        return ', '.join(self.cards)

    def draw_card(self):
        if len(deck) == 0:
            deck = used
            rd.shuffle(deck)
        self.addCard(deck[0])
        deck.pop(0)


class Game:
    def __init__(self):
        self.id = int(rd.random() * 10 ** 30)

        self.max_players = 7
        self.started = False
        self.end = False
        self.now = 0

        self.players = []


    def add_player(self, P):
        self.players += [p]

    def start(self):
        global deck
        self.deck = 50 * ["bang"] + 30 * ["miss"] + 20 * ["beer"]
        self.used = []
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
            while not self.players[self.now].status:
                self.now = (self.now + 1) % self.n
            self.end = self.turn()

            self.now = (self.now + 1) % self.n
        return
    
    def getPlayer(self, name):
        for pl in self.players:
            if str(pl) == name:
                return pl
    
    def check_death(person):
        if person.hp == 0 and "beer" in person.cards():
            send_message(person.id, "You must use beer to stay alive")
            person.hp += 1
            person.delCard("beer")
            return False
        else:
            return True

    def bang(person1):
        send_message(person1.id, "You can shoot at: ", reply_markup = make(playersList(self)))
        while self.curr_person == "":
            pass
            
        person2 = self.getPlayer(self.curr_person)
        self.curr_person = ""
        if "miss" in person2.cards():
            send_message(person2.id, "You have {0} hp. Do you want to use miss?".format(person2.hp))
            bot.send_message(person2.id, "Choose yes/no: ", reply_markup = make(["Yes", "No"]))
            while self.curr_ans == "":
                pass
            if self.curr_ans == "Yes":
                person2.delCard("miss")
            else
                person2.hp -= 1
                if check_death(person2):
                    person2.status = 0
            self.curr_ans = ""
        else:
            person2.hp -= 1
            if check_death(person2):
                person2.status = 0
        person1.delCard("bang")

    def turn(self):
        print("Now it is player № " + str(self.now) + ' turn')
        P = players[self.now]
        P.draw_card()
        P.draw_card()

        send_message(P.id, "Cards in you hand: ", reply_markup = make(P.cards))
        while self.curr_card == "":
            pass
        tmp = self.curr_card
        self.curr_card = ""
        exec("self." + tmp + "(P)")

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
    
    personToGame[pl] = game
    game.add_player(pl)
    bot.send_message(pl.id, "you join the game")
    send_all(str(pl) + ' join our game', bad = [pl])

    
@bot.message_handler(command=['game'])
def startGame(message):
    sendAdmin("pre-game init")
    game.start()
    sendAdmin("main loop starts")
    game.game()
    for pl in game.players:
        personToGame[pl] = None

@bot.message_handler(func=lambda message : messageType(message) == "card")
def chooseCard(message):
    gm = getGame(message)
    gm.curr_card = message.text
    
@bot.message_handler(func=lambda message : messageType(message) == "person")
def choosePerson(message):
    gm = getGame(message)
    gm.curr_person = message.text

@bot.message_handler(func=lambda message : messageType(message) == "binary")
def chooseCard(message):
    gm = getGame(message)
    gm.curr_ans = message.text
    
def messageType(message):
    gm = getGame(message)
    if gm is None:
        return "ignore"
    
    text = message.text
    if text in ["bang", "miss", "beer"]:
        return "card"
    if text in playersList(gm):
        return "person"
    if text in ["Yes", "No"]:
        return "binary"
    return "ignore"
    
def getGame(User):#raise 'TypeError'
    pl = User
    if isinstance(pl, telebot.types.Message):
        pl = pl.from_user
    if isinstance(pl, telebot.types.User):
        pl = Player(pl)
    elif not isinstance(pl, Player):
        raise TypeError
    gm = personToGame.get(pl, None)
    return gm

    
def sendAll(msg, bad=[]):
    for player in game.players:
        if player.id not in bad:
            bot.send_message(player.id, msg)
    return


def sendAdmin(text):
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)


def sendTurn(pl):
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


def make(arr, one_time=True):
    arr = list(arr)
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    i = 0
    while i + 3 <= len(arr):
        now.row(telebot.types.KeyboardButton(arr[i]), telebot.types.KeyboardButton(arr[i + 1]),
                telebot.types.KeyboardButton(arr[i + 2]))
        i += 3
    n = len(arr)
    d = n - i
    if d == 0:
        return now
    elif d == 1:
        now.row(telebot.types.KeyboardButton(arr[i + 0]))
        return now
    elif d == 2:
        now.row(telebot.types.KeyboardButton(arr[i + 0]), telebot.types.KeyboardButton(arr[i + 1]))
        return now

def playersList(gm):
    ans = []
    for elem in gm.players:
        ans.append(str(elem))
    if ans == []:
        ans = ['No players yet']
    return ans        

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
