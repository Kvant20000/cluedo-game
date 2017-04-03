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
import cfg

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "314275855:AAEA4Z-sF5E213qVm38VE2CJ8d8dVV6dZCg"

AdminId = [186898465, 319325008, 355967723]
Admins = [telebot.types.User(id = 186898465, username = 'antonsa', first_name = 'Anton', last_name = 'Anikushin'), telebot.types.User(id = 319325008, username = 'greatkorn', first_name = 'Anton', last_name = 'Kvasha')]

am_open = cfg.cluedo_open
people = cfg.cluedo_people
weapons = cfg.cluedo_weapons
places = cfg.cluedo_places



class Player:
    def __init__(self, cards = [], id = 186898465, username = 'antonsa', number = -1, first_name = 'Anton', last_name = 'Anikushin', User = None):
        self.cards = deepcopy(cards)
        self.alive = True
        self.know = set(cards)
        self.number = number
        self.asked = False
        self.user = User
        self.place = places[-1]
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

        self.check()

    def __str__(self):
        if str(self.username) == '':
            return str(self.first_name) + ' ' + str(self.last_name)
        else:
            return str(self.username)

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
        self.ans = (rd.choice(people), rd.choice(weapons), rd.choice(places[:-1]))  # the answer
        self.won = False
        self.now = 0
        self.asked = False

        deck = people + weapons + places[:-1]
        for i in self.ans:
            deck.remove(i)
        rd.shuffle(deck)  # so i shuffled

        self.opencards = deck[:am_open[n]]
        am_per_player = (len(deck) - am_open[n]) // n
        for i in range(n):
            players[i].setCards(deck[am_open[n] + i * am_per_player: am_open[n] + i * am_per_player + am_per_player])
        printLog(players[i].cards)

    def numberById(id):
        for elem in players:
            if elem.id == id:
                return elem.number


    def who_killed(self):
        return self.ans

    def __str__(self):
        s = 'Открытые карты: ' + ', '.join(self.opencards)
        if s == 'Открытые карты: ':
            s = 'Открытых карт нет'
        return s

    def keyboard(self, cards = True, ask = True, accuse = True, finish = True):
        keys = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if cards:
            keys.row(telebot.types.KeyboardButton('Карты'))

        if ask and accuse:
            keys.row(telebot.types.KeyboardButton('Спросить'), telebot.types.KeyboardButton('Обвинить'))
        elif ask:
            keys.row(telebot.types.KeyboardButton('Спросить'))
        elif accuse:
            keys.row(telebot.types.KeyboardButton('Обвинить'))

        if finish:
            keys.row(telebot.types.KeyboardButton('Закончить'))
        return keys

    def game(self):
        global my_ans, now_chosen, answ
        send_all('Сейчас играют :\n' + playersList())
        sendAdmin('Сейчас играют :\n' + playersList()) 
        answ = open("ans.txt", "w")
        answ.write(', '.join(GAME.ans))
        answ.close()
        while not self.won:
            while not players[self.now].alive:
                self.now = (self.now + 1) % self.n


            send_turn(players[self.now])

            my_ans = ''
            self.won = self.turn()

            my_ans = ''
            self.now = (self.now + 1) % self.n
            self.asked = False
        return

    def turn(self):
        global my_ans
        
        value = dice()

        can_go = []
        for place in places:
            if dist(players[self.now].place, place) <= value:
                can_go += [place]
                
        if len(can_go) == 0:
            my_ans = ''
            return
        if len(can_go) > 1:
            my_ans = ''
            bot.send_message(players[self.now].id, "Куда пойдете?", reply_markup = make(can_go))
            self.choose_place = True
            while my_ans == '':
                pass
            players[self.now].place = my_ans
            self.choose_place = False
        
        my_ans = ''
        bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=self.keyboard())
        
        while True:
            if my_ans == 'Закончить':
                my_ans = ''
                return False

            if my_ans == 'Карты':
                self.printCards()
                my_ans = ''
                bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=self.keyboard())

            if my_ans == 'Спросить':
                my_ans = ''
                if players[self.now].place == places[-1]:
                    bot.send_message(players[self.now].id, 'Про вашу локацию нельзя спрашивать')
                elif not self.asked:
                    choice = self.ask()
                    bot.send_message(players[self.now].id, "Ваш выбор: " + ', '.join(choice))
                    send_all(str(players[self.now]) + " спросил: " + ', '.join(now_chosen), [players[self.now].id])
                    go(self.now)
                    players[self.now].addCards(my_ans)
                    self.asked = True
                    bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=self.keyboard())
                else:
                    bot.send_message(players[self.now].id, "Вы уже спрашивали")
                    bot.send_message(players[self.now].id, 'Выберите действие:', reply_markup=self.keyboard())

            if my_ans == 'Обвинить':
                choice = self.accuse()
                bot.send_message(players[self.now].id, "Your choice is: " + ', '.join(choice))
                flag = self.checking(choice)
                return flag

        return False

    def printCards(self):
        print('cards')
        pl = players[self.now]
        text = ['', '\n', '\n', '\n\nОстальные\n', 'Кто: ', 'Чем: ', 'Где: ']
        text[0] += str(self)
        text[1] += 'Карты в руке: ' + pl.cardsInHand()
        text[2] += 'Известные тебе: ' + ', '.join(list(pl.know.difference(set(pl.cards)).difference(self.opencards)))
        text[3] += ''
        text[4] += ', '.join(list(set(people).difference(pl.know)))
        text[5] += ', '.join(list(set(weapons).difference(pl.know)))
        text[6] += ', '.join(list(set(places).difference(pl.know)))
        bot.send_message(pl.id, '\n'.join(text))
        return


    def ask(self):
        global now_chosen
        now_chosen = []
        bot.send_message(players[self.now].id, "Выберите персонажа: ", reply_markup=make(people))
        while len(now_chosen) != 1:
            pass
        bot.send_message(players[self.now].id, "Выберите оружие: ", reply_markup=make(weapons))
        while len(now_chosen) != 2:
            pass
        now_chosen.append(players[self.now].place)
        return now_chosen

    def accuse(self):
        global now_chosen
        now_chosen = []
        player = players[self.now]
        bot.send_message(players[self.now].id, "Выберите персонажа: ", reply_markup=make(list(set(people).difference(player.knownCards()))))
        while len(now_chosen) != 1:
            pass
        bot.send_message(players[self.now].id, "Выберите оружие: ", reply_markup=make(list(set(weapons).difference(player.knownCards()))))
        while len(now_chosen) != 2:
            pass
        bot.send_message(players[self.now].id, "Выберите место: ", reply_markup=make(list(set(places).difference(player.knownCards()))))
        while len(now_chosen) != 3:
            pass
        return now_chosen


    def checking(self, ans):
        if check_ans(ans):
            bot.send_photo(players[self.now].id, open('win.png', 'rb'))
            send_all(str(players[self.now]) + " выиграл!")
            send_all("Правильный ответ: " + ', '.join(self.who_killed()), [players[self.now].id])
            return True
        else:
            players[self.now].alive = False
            self.alive -= 1
            bot.send_photo(players[self.now].id, open('lose.jpg', 'rb'))
            send_all(str(players[self.now]) + " обвинил: " + ', '.join(ans))
            send_all(str(players[self.now]) + " не угадал! Он вышел из игры!")
            bot.send_message(players[self.now].id, "Правильный ответ: " + ', '.join(self.who_killed()))

        if self.alive == 1:
            for i in range(self.n):
                pl = players[i]
                if pl.alive == True:
                    bot.send_photo(players[i].id, open('win.png', 'rb'))
                    send_all(str(players[i]) + ' выиграл!')
                    bot.send_message(players[i].id, "Правильный ответ: " + ', '.join(self.who_killed()))
                    break
            return True
        return False

MAX_PLAYERS = 6
bot = telebot.TeleBot(TOKEN)
GAME = None
players = []
#FINISHED = False
#active = []

now_chosen = []
my_ans = ''
who = -1


#FINISHED = False
#active = []

file_name = 'logs.txt'
now_chosen = []
my_ans = ''
who = -1

#@bot.message_handler()
#def trash(message):
#    print(message.text)
def fromAdmin(message):
    return message.chat.id in AdminId


@bot.message_handler(commands=['join'])
def get_players(message): #new
    if GAME is not None:
        bot.send_message(message.chat.id, "Игра уже началась")
        return

    global players

    id = message.chat.id
    name = message.chat.username
    user = telebot.types.User(id = id, username = name, first_name = message.chat.first_name, last_name = message.chat.last_name)
    pl = Player(User = user)
    if len(players) >= MAX_PLAYERS:
        bot.send_message(id, "Извените, свободных мест нет!")
        return
    elif not hasPlayer(pl):
        players.append(pl)
        bot.send_message(id, "Добро пожаловать в игру, {0}!".format(str(players[-1])))
        sendAdmin(str(players[-1]) + ' joined game')
        send_all(playersList())
        printLog(playersList())
        return
    printLog(playersList())


@bot.message_handler(commands=['game'], func=fromAdmin)
def start_game(message): #new
    global GAME, active
    if GAME is not None:
        bot.send_message(message.chat.id, "Игра уже началась")
    else:
        sendAdmin('Игра начинается')
        active = [True] * len(players)

        send_all('Карты в игре')
        send_all('Кто :' + ', '.join(people))
        send_all('Чем :' + ', '.join(weapons))
        send_all('Где :' + ', '.join(places))

        rd.shuffle(players)
        GAME = Game(len(players))
        place = 0
        for i in range(len(players)):
            players[i].setNumber(place)
            for card in GAME.opencards:
                players[i].addCards(card)
            place += 1


        for player in players:
            cards = str(GAME)
            bot.send_message(player.id, cards)
            bot.send_message(player.id, 'Ваши карты: ' + player.cardsInHand())

        GAME.game()
        gameEnd()


@bot.message_handler(commands=['help', 'start'])
def helpMessege(message): #should be remake
    #printLog('help from ' + str(message.chat.id))
    text = ('/help - чтобы снова увидеть это сообщение\n/join - присоедениться к игре\nвсё остальное спрашивать у @antonsa')
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['how_use'])
def use(message): #should be remake
    #printLog('how use from ')
    id = message.chat.id
    text = ('пиши @antonsa')
    bot.send_message(id, text)


@bot.message_handler(commands=['status'], func=fromAdmin)
def status(message):
    if GAME is None:
        bot.send_message(message.chat.id, 'Stopped')
    else:
        bot.send_message(message.chat.id, 'In process')


@bot.message_handler(commands=['players'])
def composition(message):
    bot.send_message(message.chat.id, playersList())


@bot.message_handler(commands=['end'])
def gameEnd(message = None): #think is new
    if message is None:
        send_all('Игра закончена, можете начать новую')
        sendAdmin('Игра закончена, можете начать новую')
        end()
    elif not (message.chat.id in AdminId or hasPlayer(message.chat)):
        bot.send_message(message.chat.id, "Нет доступа(разрешения)!")
        return
    else:
        send_all('Игра закончена, можете начать новую')
        sendAdmin('Игра закончена, можете начать новую')
        end()


@bot.message_handler(commands=['full_end'])
def botEnd(message = None): #new
    if not (message.chat.id in AdminId):
        bot.send_message(message.chat.id, "Отказано в доступе!")
        return
    else:
        printLog('end of bot')
        send_all('Игра закончена, бот остановлен')
        sendAdmin('Игра закончена, бот остановлен')
        print('full end')
        bot.stop_polling()


@bot.message_handler()
def catch(message): #new
    global now_chosen, my_ans, who
    if GAME is None:
        return

    if not (message.chat.id == players[GAME.now].id or message.chat.id == players[who].id):
        return

    text = message.text

    if text in ['Карты', 'Спросить', 'Обвинить', 'Закончить'] and message.chat.id == players[GAME.now].id:
        my_ans = text
        return
    if text in now_chosen or message.text == 'НЕТ' and message.chat.id == players[who].id:
        my_ans = text
        return
    if text in places and GAME.choose_place:
        my_ans = text
        return
    if text in people + weapons + places and message.chat.id == players[GAME.now].id:
        now_chosen += [text]
        return
    return


def end(): #new
    global players, GAME
    printLog('end of game\n-------------------------------------------------------\n\n')
    GAME = None
    players = []


def playersList(): #new
    ans = []
    for elem in players:
        ans.append(str(elem))
    if ans == []:
        ans = ['No players yet']
    return ', '.join(ans)


def make(arr, one_time = True): #new
    arr = list(arr)
    now = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=one_time)
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


def go(index): #think is new
    global my_ans, who
    my_ans = ''
    man = (index + 1) % GAME.n
    while man != index and not answer(man):
        my_ans = ''
        man = (man + 1) % GAME.n
    if man == index:
        send_all('Никто не смог помочь!')
    else:
        bot.send_message(players[index].id, my_ans + ' от ' + str(players[man]))
        send_all('Ответил ' + str(players[man]), [players[index].id, players[man].id])
    who = -1

def answer(man): #think is new
    global my_ans, who

    who = man
    id = players[man].id
    Pl = players[man]
    cards = set(Pl.cards)
    now = set(now_chosen)
    inter = now.intersection(cards)


    if len(inter) == 0:
        bot.send_message(id, "Выберите ответ: ", reply_markup=make(['НЕТ']))
        while len(my_ans) == 0:
            pass
        send_all(str(players[man]) + " ответил 'НЕТ'", [players[man].id])
        return False
    else:
        bot.send_message(id, "Выберите ответ: ", reply_markup=make(list(inter)))
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
        if player.id not in bad:
            bot.send_message(player.id, msg)
    return

def sendAdmin(text): #new
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)

def send_turn(pl): #new
    for player in players:
        bot.send_message(player.id, "Сейчас ходит " + str(pl))
    return

def printLog(text): #should be checked
    global file_name
    logs = open(file_name, "a")
    logs.write(str(text) + '\n\n')
    logs.close()

def logName():
    log = "logs ("
    today = time.gmtime()
    year = str(today.tm_year)
    month = str(today.tm_mon)
    day = str(today.tm_mday)
    hour = str(today.tm_hour)
    minute = str(today.tm_min)
    seconds = str(today.tm_sec)
    log += str(year) + '.' + str(month) + '.' + str(day) + ' ' + str(hour) + ';' + str(minute) + ';' + str(seconds) + ').txt'
    return log

def dice():
    return rd.randrange(1, 7) + rd.randrange(1, 7)

def dist(place1, place2):
    return 0
    
def main():
    global file_name, GAME, players
    file_name = logName()
    loggs = open(file_name, "w")
    loggs.close()
    GAME = None
    players = []
    try:
        sendAdmin('Bot starts')
        bot.polling()
    except Exception as err:
        printLog(str(err))


if __name__ == '__main__':
    main()
