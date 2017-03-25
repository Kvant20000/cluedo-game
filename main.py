# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import datetime
import random as rd

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "314275855:AAEA4Z-sF5E213qVm38VE2CJ8d8dVV6dZCg"

am_open = [0, 0, 0, 0, 2, 3, 0]  # other option is [0, 0, 0, 6, 6, 3, 6]
people = ["Ворона", "Берёза", "Князь Пожарский", "Васечка", "Афганский мафиози", "СВ"]  # КТО?
weapons = ["Тихим Доном", "клавиатурой", "выносом мозга", "тупыми мемами", "коробкой из-под пиццы",
           "огнетушителем"]  # ЧЕМ?
places = ["в 209", "у психолога", "в Маке", "на футбольном поле", "в электричке", "в актовом зале", "в ТЦ Охотный",
          "у выхода из метро", "в офисе 1С"]  # ГДЕ?

CHOOSING_NOW = 0
NUMBER_OF_PEOPLE = 0
COUNT = 0
HAS_ASKED = False


class Player:
    def __init__(self, A):
        self.cards = A
        self.alive = True

    def __str__(self):
        return ', '.join(self.cards)


class Game:
    def __init__(self, n):  # n players
        global NUMBER_OF_PEOPLE, COUNT
        NUMBER_OF_PEOPLE = n
        COUNT = n
        print(NUMBER_OF_PEOPLE, COUNT)
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


# @bot.message_handler()
# def trash(message):
# print(message.text)

def go(index):
    global my_ans
    my_ans = ''
    man = (index + 1) % COUNT
    while man != index and not answer(man):
        my_ans = ''
        man = (man + 1) % COUNT
    if man == index:
        send_all('Nobody can help!')
    else:
        bot.send_message(players[index][0], my_ans + ' from ' + players[man][1])
        send_all('Answered by ' + players[man][1], [players[index]])


def answer(man):
    global my_ans
    id = players[man][0]
    Pl = GAME.players[man]
    cards = set(Pl.cards)
    now = set(now_chosen)
    inter = now.intersection(cards)

    #print(inter)

    if len(now.intersection(cards)) == 0:
        bot.send_message(id, "Choose answer: ", reply_markup=make(['NO']))
        while len(my_ans) == 0:
            pass
        send_all(players[man][1] + " answered 'NO'", [players[man]])
        return False
    else:
        bot.send_message(id, "Choose answer: ", reply_markup=make(list(inter)))
        while len(my_ans) == 0:
            pass
        return True


@bot.message_handler(commands=['play'])
def get_players(message):
    if FINISHED:
        bot.send_message(message.chat.id, "Game has already started!")
        return
    global players
    Id = message.chat.id
    user = message.chat.username
    if len(players) > 5 and FINISHED:
        msg = bot.send_message(message.chat.id, "Sorry, no empty places!")
    elif (Id, user) not in players:
        players.append((Id, user))
        msg = bot.send_message(message.chat.id, "Welcome to the game, {0}!".format(user))
    print(players)


@bot.message_handler(commands=['game'])
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
        send_turn()


def make(arr):
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for elem in arr:
        now.add(telebot.types.KeyboardButton(elem))
    return now


@bot.message_handler(commands=['ask'])
def ask(message):
    global now_chosen
    global CHOOSING_NOW
    global HAS_ASKED

    if CHOOSING_NOW != d[message.chat.id]:
        bot.send_message(message.chat.id, "Not your turn!")
        return
    if HAS_ASKED == True:
        bot.send_message(message.chat.id, "You have already asked")
        return

    HAS_ASKED = True
    now_chosen = []
    if not GAME.players[d[message.chat.id]].alive:
        bot.send_message(message.chat.id, "You are dead!")
        return
    bot.send_message(message.chat.id, "Choose person: ", reply_markup=make(people))
    while len(now_chosen) != 1:
        pass
    bot.send_message(message.chat.id, "Choose weapon: ", reply_markup=make(weapons))
    while len(now_chosen) != 2:
        pass
    bot.send_message(message.chat.id, "Choose place: ", reply_markup=make(places))
    while len(now_chosen) != 3:
        pass
    bot.send_message(message.chat.id, "Your choice is: " + ', '.join(now_chosen))
    send_all(players[d[message.chat.id]][1] + " asks: " + ', '.join(now_chosen), [players[d[message.chat.id]]])
    go(d[message.chat.id])


@bot.message_handler(commands=['help'])
def helpMessege(message):
    text = '/help - see this message again' + '\n' + '/play - join unstarted game' + '\n' + '/game - start new game with conected players' + '\n' + '/ask - ask one CLUEDO question' + '\n' + '/accuse - make accusation' + '\n' + '/finish - end of your turn'
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['accuse'])
def accuse(message):
    global now_chosen
    global active
    global GAME
    global CHOOSING_NOW
    global NUMBER_OF_PEOPLE
    global HAS_ASKED

    if CHOOSING_NOW != d[message.chat.id]:
        bot.send_message(message.chat.id, "Not your turn!")
        return
    if not GAME.players[d[message.chat.id]].alive:
        bot.send_message(message.chat.id, "You are dead!")
        return
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
        send_all("Correct answer is: " + ', '.join(GAME.killed()))
        end()
    else:
        GAME.players[d[message.chat.id]].alive = False
        NUMBER_OF_PEOPLE -= 1
        send_all(players[d[message.chat.id]][1] + " has accused: " + ', '.join(now_chosen))
        send_all(players[d[message.chat.id]][1] + " didn't guess correctly! He's out of the game!")
        bot.send_message(message.chat.id, "Correct answer is: " + ', '.join(GAME.killed()))
        nextTurn()

    if NUMBER_OF_PEOPLE == 1:
        for i in range(len(GAME.players)):
            pl = GAME.players[i]
            if pl.alive == True:
                send_all(players[i][1] + ' won!')
                break
        end()


@bot.message_handler(commands=['finish'])
def nextTurn(message=None):
    global CHOOSING_NOW, HAS_ASKED
    if message is None or CHOOSING_NOW != d[message.chat.id]:
        bot.send_message(message.chat.id, "Not your turn!")
        return
    HAS_ASKED = False
    CHOOSING_NOW = (CHOOSING_NOW + 1) % COUNT
    send_turn()


@bot.message_handler()
def tmp(message):
    global now_chosen, my_ans
    if message.text in now_chosen or message.text == 'NO':
        my_ans = message.text

    if message.text in people + weapons + places:
        now_chosen += [message.text]
    return


def end():
    exit(0)


def check_ans(arr):
    return sorted(GAME.killed()) == sorted(arr)


def send_all(msg, bad = []):
    for player in players:
        if player not in bad:
            bot.send_message(player[0], msg)
    return


def send_turn():
    for player in players:
        bot.send_message(player[0], "Now it's " + players[CHOOSING_NOW][1] + "'s turn")
    return


bot.polling()
