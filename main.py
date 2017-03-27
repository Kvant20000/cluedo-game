# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import sys
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
MAX_PLAYERS = 6


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
        s = ["Открытые карты: " + ', '.join(self.opencrds) + '\n']
        s += ["Ваши карты: " + str(self.players[person]) + '\n']
        return s


players = []
now_chosen = []
FINISHED = False
GAME = None
d = dict()
active = []

bot = telebot.TeleBot(TOKEN)
my_ans = ''


#@bot.message_handler()
#def trash(message):
#    print(message.text)


def playersToString(names):
    ans = ''
    for elem in names:
        ans += elem[1] + '\n'
    return ans


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
        send_all('Answered by ' + players[man][1], [players[index], players[man]])


def answer(man):
    global my_ans
    id = players[man][0]
    Pl = GAME.players[man]
    cards = set(Pl.cards)
    now = set(now_chosen)
    inter = now.intersection(cards)

    print(inter)

    if len(inter) == 0:
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
    if user is None:
        bot.send_message(message.chat.id, "Set your username and try again!")
    else:
        user = str(user)
    if len(players) >= MAX_PLAYERS:
        bot.send_message(message.chat.id, "Sorry, no empty places!")
        return
    elif (Id, user) not in players:
        players.append((Id, user))
        bot.send_message(message.chat.id, "Welcome to the game, {0}!".format(user))
        send_all(playersToString(players))
    print(players)
    printLog(players)


@bot.message_handler(commands=['game'])
def start_game(message):
    global FINISHED
    global GAME
    global d
    global active
    if FINISHED:
        bot.send_message(message.chat.id, "Game has already started")
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
        order = "Order of people: "
        for player in players:
            cards = GAME.cards(d[player[0]])
            bot.send_message(player[0], cards[0])
            bot.send_message(player[0], cards[1])
            order += (player[1] + ', ')
        send_all(order[:-2])
        print(d, active)
        print(GAME.killed())
        printLog(str(d))
        printLog(str(active))
        printLog(str(players))
        printLog(str(GAME.killed))
        send_turn()


def make(arr):
    printLog('make(' + str(arr) + ')')
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    i = 0
    while i + 3 <= len(arr):
        now.row(telebot.types.KeyboardButton(arr[i + 0]), telebot.types.KeyboardButton(arr[i + 1]), telebot.types.KeyboardButton(arr[i + 2]))
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
    printLog('Why i print it?')
    

def make2(arr):
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    if len(arr) == 1:
        now.row(telebot.types.KeyboardButton(arr[0]))
    elif len(arr) == 2:
        now.row(telebot.types.KeyboardButton(arr[0]), telebot.types.KeyboardButton(arr[1]))
    elif len(arr) > 2:
        now.row(telebot.types.KeyboardButton(arr[0]), telebot.types.KeyboardButton(arr[1]),
                telebot.types.KeyboardButton(arr[2]))
        now.row(telebot.types.KeyboardButton(arr[3]), telebot.types.KeyboardButton(arr[4]),
                telebot.types.KeyboardButton(arr[5]))
        if len(arr) == 9:
            now.row(telebot.types.KeyboardButton(arr[6]), telebot.types.KeyboardButton(arr[7]),
                    telebot.types.KeyboardButton(arr[8]))
    return now


@bot.message_handler(commands=['ask'])
def ask(message):
    global FINISHED, players, now_chosen, GAME, d, active, my_ans, CHOOSING_NOW, NUMBER_OF_PEOPLE, COUNT, HAS_ASKED
    
    printLog('person ' + str(message.chat.id) + 'asks')
    
    if GAME is None:
        printLog('Game not started yet')
        return
    
    if not FINISHED:
        return
    if CHOOSING_NOW != d[message.chat.id]:
        bot.send_message(message.chat.id, "Not your turn!")
        return
    if HAS_ASKED:
        bot.send_message(message.chat.id, "You have already asked")
        return
    printLog('trash question are ignored' + str(message.chat.id))
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
    printLog('person has choosen  ' + ', '.join(now_chosen) + ' ' + str(message.chat.id))
    bot.send_message(message.chat.id, "Your choice is: " + ', '.join(now_chosen))
    send_all(players[d[message.chat.id]][1] + " asks: " + ', '.join(now_chosen), [players[d[message.chat.id]]])
    go(d[message.chat.id])
    printLog('ask of wanting to accuse ' + str(message.chat.id))
    my_ans = ''
    bot.send_message(message.chat.id, "Do you want to accuse?", reply_markup=make(["YES", "NO"]))
    while my_ans == '':
        pass
    if my_ans == "YES":
        printLog('want to accuse by ' + str(message.chat.id))
        if not FINISHED:
            return
        if CHOOSING_NOW != d[message.chat.id]:
            bot.send_message(message.chat.id, "Not your turn!")
            return
        if not GAME.players[d[message.chat.id]].alive:
            bot.send_message(message.chat.id, "You are dead!")
            return
        now_chosen = []
        printLog('person ' + str(message.chat.id) + ' choose')
        bot.send_message(message.chat.id, "Choose person: ", reply_markup=make(people))
        while len(now_chosen) != 1:
            pass
        bot.send_message(message.chat.id, "Choose weapon: ", reply_markup=make(weapons))
        while len(now_chosen) != 2:
            pass
        bot.send_message(message.chat.id, "Choose place: ", reply_markup=make(places))
        while len(now_chosen) != 3:
            pass
        printLog('person ' + str(message.chat.id) + ' has choosen  ' + ', '.join(now_chosen))
        if check_ans(now_chosen):
            printLog(str(message.chat.id) + " guess")
            send_all(players[d[message.chat.id]][1] + " won!")
            send_all("Correct answer is: " + ', '.join(GAME.killed()))
            end()
        else:
            printLog(str(message.chat.id) + " didn't guess")
            GAME.players[d[message.chat.id]].alive = False
            NUMBER_OF_PEOPLE -= 1
            send_all(players[d[message.chat.id]][1] + " has accused: " + ', '.join(now_chosen))
            send_all(players[d[message.chat.id]][1] + " didn't guess correctly! He's out of the game!")
            bot.send_message(message.chat.id, "Correct answer is: " + ', '.join(GAME.killed()))
            if not FINISHED:
                return
            if message is None:
                return
            if CHOOSING_NOW != d[message.chat.id]:
                bot.send_message(message.chat.id, "Not your turn!")
                return
            HAS_ASKED = False
            CHOOSING_NOW = (CHOOSING_NOW + 1) % COUNT
            while not GAME.players[CHOOSING_NOW].alive:
                CHOOSING_NOW = (CHOOSING_NOW + 1) % COUNT
            send_turn()
            end()

        if NUMBER_OF_PEOPLE == 1:
            for i in range(len(GAME.players)):
                pl = GAME.players[i]
                if pl.alive == True:
                    send_all(players[i][1] + ' won!')
                    bot.send_message(players[i][0], "Correct answer is: " + ', '.join(GAME.killed()))
                    break
            end()
    else:
        printLog(str(message.chat.id) + " didn't accuse")
        if not FINISHED:
            return
        if message is None:
            return
        if CHOOSING_NOW != d[message.chat.id]:
            bot.send_message(message.chat.id, "Not your turn!")
            return
        HAS_ASKED = False
        CHOOSING_NOW = (CHOOSING_NOW + 1) % COUNT
        while not GAME.players[CHOOSING_NOW].alive:
            CHOOSING_NOW = (CHOOSING_NOW + 1) % COUNT
        send_turn()


@bot.message_handler(commands=['help', 'start'])
def helpMessege(message):
    printLog('help from ' + str(message.chat.id))
    text = ('/help - see this message again' + '\n' +
            '/play - join unstarted game' + '\n' +
            '/game - start new game with conected players' + '\n' +
            '/ask - ask one CLUEDO question' + '\n' +
            '/how_use - how use this bot')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['how_use'])
def use(message):
    printLog('how use from ' + str(message.chat.id))
    id = message.chat.id
    text = ('если ты хочешь изъявить желане играть, то напиши команду /play' + '\n' +
            'чтобы начать игру с другими подключенными игроками напиши /game' + '\n' +
            'для отправки вопроса команда /ask' + '\n' +
            'после надо или обвинять /accuse или закончить ход /finish' + '\n' +
            'ход перейдет к следующему игроку' + '\n')
    bot.send_message(id, text)


@bot.message_handler(commands=['end'])
def gemeEnd(message):
    send_all('This game ends, new can start')
    end()


@bot.message_handler(commands=['full_end'])
def botEnd(message):
    printLog('end of bot')
    send_all('This game and current session ends')
    time.sleep(10)
    print('full end')
    exit(0)


@bot.message_handler(commands=['cards'])
def show_cards(message):
    cards = GAME.cards(d[message.chat.id])
    bot.send_message(message.chat.id, cards[0])
    bot.send_message(message.chat.id, cards[1])
    printLog("Player {0} asked cards\n".format(players[d[message.chat.id]][1])) 


@bot.message_handler()
def tmp(message):
    global now_chosen, my_ans
    if message.text in now_chosen or message.text == 'NO' or message.text == "YES":
        my_ans = message.text

    if message.text in people + weapons + places:
        now_chosen += [message.text]

    return


def end():
    global FINISHED, players, now_chosen, GAME, d, active, my_ans, CHOOSING_NOW, NUMBER_OF_PEOPLE, COUNT, HAS_ASKED
    printLog('end of game')
    FINISHED = False
    players = []
    now_chosen = []
    GAME = None
    d = dict()
    active = []
    my_ans = ''
    CHOOSING_NOW = 0
    NUMBER_OF_PEOPLE = 0
    COUNT = 0
    HAS_ASKED = False
    
    


def check_ans(arr):
    return sorted(GAME.killed()) == sorted(arr)


def send_all(msg, bad=[]):
    for player in players:
        if player not in bad:
            bot.send_message(player[0], msg)
    return


def send_turn():
    for player in players:
        bot.send_message(player[0], "Now it's " + players[CHOOSING_NOW][1] + "'s turn")
    return

def printLog(text):
    global file_name
    logs = open(file_name, "a")
    logs.write(str(text) + '\n\n')
    logs.close()
    
    
file_name = "logs" + str(time.time()) + ".txt"
loggs = open(file_name, "w")
loggs.close()

try:
    bot.polling()
except Exception as err:
    printLog(str(err))
