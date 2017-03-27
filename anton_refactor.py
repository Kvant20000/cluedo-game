# -*- coding: utf-8 -*-
import telebot
import logging
import colorlog
import emoji
import time
import sys
import datetime
import random as rd
from copy import deepcopy

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "314275855:AAEA4Z-sF5E213qVm38VE2CJ8d8dVV6dZCg"

Admin = telebot.types.User(id = 186898465, username = 'antonsa', first_name = 'Anton', last_name = 'Anikushin')

am_open = [0, 0, 0, 0, 2, 3, 0]  # other option is [0, 0, 0, 6, 6, 3, 6]
people = ["Ворона", "Берёза", "Князь Пожарский", "Васечка", "Афганский мафиози", "СВ"]  # КТО?
weapons = ["Тихим Доном", "клавиатурой", "выносом мозга", "тупыми мемами", "коробкой из-под пиццы",
           "огнетушителем"]  # ЧЕМ?
places = ["в 209", "у психолога", "в Маке", "на футбольном поле", "в электричке", "в актовом зале", "в ТЦ Охотный",
          "у выхода из метро", "в офисе 1С"]  # ГДЕ?



class Player:
    def __init__(self, cards = [], id = 186898465, username = 'antonsa', number = -1, first_name = 'Anton', last_name = 'Anikushin', User = None):
        self.cards = deepcopy(cards)
        self.alive = True
        self.know = set(cards)
        self.number = number
        self.asked = False
        self.user = User
        if User is None:
            self.user = telebot.types.User(id = id, username = username, first_name = first_name)
            self.id = id
            self.username = username
            self.first_name = first_name
            self.last_name = last_name
        else:
            self.id = User.id
            self.username = User.username
            self.first_name = User.first_name
            self.last_name = User.last_name
        
        
    def __str__(self):
        return str(self.first_name) + ' ' + str(self.last_name) + '(' + str(self.username) + ')'
    
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
        self.know = set(cards)
    
    def addCards(self, card):
        self.know.add(card)
    
    def cardsInHand(self):
        return ', '.join(self.cards) 
    
    def knownCards(self):
        return self.know
    
    def data(self):
        return self.cards + [self.username, self.id]

        
class Game:
    def __init__(self, n):  # n players
        self.now = 0
        self.alive = n
        self.n = n
        self.d = dict()
        self.full = False
        self.max_players = 6
        self.ans = (rd.choice(people), rd.choice(weapons), rd.choice(places))  # the answer
        self.won = False
        self.now = 0
        
        deck = people + weapons + places
        for i in self.ans:
            deck.remove(i)
        rd.shuffle(deck)  # so i shuffled

        self.open_cards = deck[:am_open[n]]
        am_per_player = (len(deck) - am_open[n]) // n
        for i in range(n):
            players[i].setCards(deck[am_open[n] + i * am_per_player: am_open[n] + i * am_per_player + am_per_player])
    
    def numberById(id):
        for elem in players:
            if elem.id == id:
                return elem.number
    

    def who_killed(self):
        return self.ans

    def __str__(self, person):
        s = 'Открытые карты: ' + ', '.join(self.opencrds)
        return s
    
    def game():
        global my_ans, now_chosen
        send_all('Сейчас играют :\n' + playersList())
        sendAdmin('Сейчас играют :\n' + playersList())
        
        while not self.won:
            while not players[self.now].alive:
                self.now += 1
                
            keys = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
            keys.row(telebot.types.KeyboardButton('Ваши карты'))
            keys.row(telebot.types.KeyboardButton('Спросить'), telebot.types.KeyboardButton('Обвинить'))
            keys.row(telebot.types.KeyboardButton('Закончить'))
            
            send_turn(players[self.now])
            bot.send_message('Выберите действие:', reply_markup=keys)
            
            while my_ans != '':
                pass
                
            flag = self.turn()
            if flag:
                return
            self.now += 1
            
             
    def turn(self):
        global my_ans
        
        if my_ans == 'Закончить':
            my_ans = ''
            return False
        if my_ans == 'Ваши карты':
            bot.send_message(players[self.now].id, players[self.now].knownCards())
            my_ans = ''
            
            keys = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
            keys.row(telebot.types.KeyboardButton('Спросить'), telebot.types.KeyboardButton('Обвинить'))
            keys.row(telebot.types.KeyboardButton('Закончить'))
            bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=keys)
            while my_ans == '':
                pass

        if my_ans == 'Закончить':
            my_ans = ''
            return False
        if my_ans == 'Спросить':
            choice = self.ask()
            bot.send_message(players[self.now].id, "Your choice is: " + ', '.join(choice))
            send_all(str(players[self.now]) + " asks: " + ', '.join(now_chosen), [Pl])
            go(self.now)
            players[self.now].addCards(my_ans)

            keys = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
            keys.row(telebot.types.KeyboardButton('Обвинить'))
            keys.row(telebot.types.KeyboardButton('Закончить'))
            bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=keys)
            while my_ans == '':
                pass
        
        if my_ans == 'Закончить':
            my_ans = ''
            self.now += 1
            return False
        if my_ans == 'Обвинить':
            choice = self.accuse()
            bot.send_message(players[self.now].id, "Your choice is: " + ', '.join(choice))
            
            flag = self.checking(choice)
    
    def checking(self, ans):
        if check_ans(ans):
            send_all(str(players[self.now]) + " won!")
            send_all("Correct answer is: " + ', '.join(self.killed()), players[self.now])
            return True
        else:
            players[self.now].alive = False
            self.alive -= 1
            send_all(str(players[self.now]) + " has accused: " + ', '.join(ans))
            send_all(str(players[self.now]) + " didn't guess correctly! He's out of the game!")
            bot.send_message(players[self.now].id, "Correct answer is: " + ', '.join(self.who_killed()))
            
            
        if self.alive == 1:
            for i in range(self.n):
                pl = players[i]
                if pl.alive == True:
                    send_all(str(players[i]) + ' won!')
                    bot.send_message(players[i].id, "Correct answer is: " + ', '.join(self.who_killed()))
                    break
            return True
        return False
        
    
    def ask(self):
        global now_chosen
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
        return now_chosen
        
    def accuse(self):
        global now_chosen
        now_chosen = []
        player = players[self.now]
        bot.send_message(message.chat.id, "Choose person: ", reply_markup=make(list(set(people).difference(player.knownCards()))))
        while len(now_chosen) != 1:
            pass
        bot.send_message(message.chat.id, "Choose weapon: ", reply_markup=make(list(set(weapons).difference(player.knownCards()))))
        while len(now_chosen) != 2:
            pass
        bot.send_message(message.chat.id, "Choose place: ", reply_markup=make(list(set(places).difference(player.knownCards()))))
        while len(now_chosen) != 3:
            pass
        return now_chosen


MAX_PLAYERS = 6
bot = telebot.TeleBot(TOKEN2)

GAME = None
players = []
#FINISHED = False
active = []

now_chosen = []
my_ans = ''


#@bot.message_handler()
#def trash(message):
#    print(message.text)



@bot.message_handler(commands=['play'])
def get_players(message): #new
    if GAME is not None:
        bot.send_message(message.chat.id, "Game has already started!")
        return
        
    global players
    
    id = message.chat.id
    name = message.chat.username
    user = telebot.types.User(id = id, username = name, first_name = message.chat.first_name, last_name = message.chat.last_name)
    pl = Player(User = user)
    if len(players) >= MAX_PLAYERS:
        bot.send_message(id, "Sorry, no empty places!")
        return
    elif not hasPlayer(pl):
        players.append(pl)
        bot.send_message(id, "Welcome to the game, {0}!".format(str(players[-1])))
        sendAdmin(str(players[-1]) + ' joined game')
        print(playersList())
        return
    print(playersList())

    
@bot.message_handler(commands=['game'])
def start_game(message): #new
    global GAME, active
    if GAME is not None:
        msg = bot.send_message(message.chat.id, "Game has already started")
    else:
        sendAdmin('Game starts')
        active = [True] * len(players)
        
        rd.shuffle(players)
        GAME = Game(len(players))
        place = 0
        for i in range(len(players)):
            players[i].setNumber(place)
            place += 1
            
            
        for player in players:
            cards = GAME.cards(d[player[0]])
            bot.send_message(player.id, cards)
            bot.send_message(player.id, 'Ваши карты: ' + player.cardsInHand())
        
        GAME.game()
        gemeEnd()
        
        
@bot.message_handler(commands=['help', 'start'])
def helpMessege(message): #should be remake
    printLog('help from ' + str(message.chat.id))
    text = ('/help - чтобы снова увидеть\nвсё остальное спрашивать у @antonsa')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['how_use'])
def use(message): #should be remake
    printLog('how use from ' + str(message.chat.id))
    id = message.chat.id
    text = ('пиши @antonsa')
    bot.send_message(id, text)


@bot.message_handler(commands=['end'])
def gemeEnd(message): #think is new
    send_all('This game ends, new can start')
    sendAdmin('Current game ends, new can start')
    end()


@bot.message_handler(commands=['full_end'])
def botEnd(message): #new
    printLog('end of bot')
    send_all('This game and current session ends')
    sendAdmin('This game and current session ends')
    time.sleep(10)
    print('full end')
    exit(0)


@bot.message_handler()
def catch(message): #new
    global now_chosen, my_ans
    
    text = message.text
    
    if text in ['Ваши карты', 'Спросить', 'Обвинить', 'Закончить']:
        my_ans = text
        return
    if message.text in now_chosen or message.text == 'NO' or message.text == "YES":
        my_ans = message.text
        return
    if message.text in people + weapons + places:
        now_chosen += [message.text]
        return
    return


def end(): #new
    global players, GAME
    printLog('end of game')
    GAME = None
    players = []

    
def playersList(): #new
    ans = []
    for elem in players:
        ans.append(str(elem))
    return ', '.join(ans)


def make(arr): #new
    arr = list(arr)
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

    
def go(index): #think is new
    global my_ans
    my_ans = ''
    man = (index + 1) % GAME.n
    while man != index and not answer(man):
        my_ans = ''
        man = (man + 1) % GAME.n
    if man == index:
        send_all('Nobody can help!')
    else:
        bot.send_message(players[index].id, my_ans + ' from ' + str(players[man]))
        send_all('Answered by ' + str(players[man]), [players[index], players[man]])


def answer(man): #think is new
    global my_ans
    
    id = players[man].id
    Pl = players[man]
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
    
def hasPlayer(pl): #new
    for elem in players:
        if elem.id == pl.id:
            return True
    return False
    

def check_ans(arr): #new
    return sorted(GAME.who_killed()) == sorted(arr)


def send_all(msg, bad=[]): #new
    for player in players:
        if player not in bad:
            bot.send_message(player.id, msg)
    return

def sendAdmin(text): #new
    bot.send_message(Admin.id, 'Admin : ' + text)

def send_turn(player): #new
    for player in players:
        bot.send_message(player[0], "Now it's " + str(player) + "'s turn")
    return

def printLog(text): #should be checked
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
