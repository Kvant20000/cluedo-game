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
import threading

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "286496122:AAGED92TDcccXHGJmgyz5oJcCcZ4TI-vTrM"
MAX_GAMES = 10

AdminId = [186898465, 319325008]
Admins = [telebot.types.User(id=186898465, username='antonsa', first_name='Anton', last_name='Anikushin'),
          telebot.types.User(id=319325008, username='greatkorn', first_name='Anton', last_name='Kvasha')]

curr = 0


class Player:
    def __init__(self, cards=[], id=186898465, username='antonsa', number=-1, first_name='Anton', last_name='Anikushin',
                 User=None):
        self.cards = deepcopy(cards)
        self.alive = True
        self.know = set(cards)
        self.number = number
        self.asked = False
        self.user = User
        self.place = 'cobybook'
        self.person = 'pen'
        if User is None:
            self.user = telebot.types.User(id=id, username=username, first_name=first_name)
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
    def __init__(self):
        cfg.cluedo_init()
        self.am_open = cfg.cluedo_open
        self.people = cfg.cluedo_people
        self.weapons = cfg.cluedo_weapons
        self.places = cfg.cluedo_places
        self.distance = cfg.cluedo_dist

        self.id = int(rd.random() * 10000000)

        self.now = 0
        self.max_players = 6
        self.started = False

        self.won = False
        self.asking = False
        self.accusing = False
        self.asked = False
        self.choose_place = False

        self.ans = (rd.choice(self.people), rd.choice(self.weapons), rd.choice(self.places))  # the answer
        self.players = []

        self.my_ans = ''
        self.now_chosen = []
        self.inter = set()
        self.who = -1

    def addPlayers(self, pl):
        self.players += [pl]
    
    def deletePlayer(self, pl):
        if not self.started:
            self.players.pop(self.players.index(pl))
            return True
        else:
            return False
    
    def start(self):
        sendAdmin('Game ' + str(game_by_id[self.id]) + ' starts')
        rd.shuffle(self.players)
        self.started = True
        n = len(self.players)
        self.alive = n
        self.n = n
        deck = self.people + self.weapons + self.places
        for i in self.ans:
            deck.remove(i)
        rd.shuffle(deck)

        self.opencards = deck[:self.am_open[n]]

        self.startPrint()

        other = deepcopy(self.people)

        am_per_player = (len(deck) - self.am_open[n]) // n
        for i in range(n):
            self.players[i].number = i
            self.players[i].setCards(
                deck[self.am_open[n] + i * am_per_player: self.am_open[n] + i * am_per_player + am_per_player])
            bot.send_message(self.players[i].id, 'Your cards: ' + self.players[i].cardsInHand())
            for open in self.opencards:
                self.players[i].addCards(open)

            self.players[i].place = rd.choice(self.places)
            self.players[i].person = rd.choice(other)
            other.remove(self.players[i].person)
            printLog(self.players[i].cards)
        for i in range(n):
            send_all(str(self.players[i]) + ' is ' + self.players[i].person, self)

        sendAdmin('Currently in ' + str(game_by_id[self.id]) + ': \n' + playersList(self))
        send_all('Currently in game: \n' + playersList(self), self)

    def startPrint(self):
        send_all("Cards in game", self)
        send_all('People: ' + ', '.join(self.people), self)
        send_all('Weapons: ' + ', '.join(self.weapons), self)
        send_all('Places: ' + ', '.join(self.places), self)
        send_all(self.open(), self)

    def game(self):
        while not self.won:
            while not self.players[self.now].alive:
                self.now = (self.now + 1) % self.n

            send_turn(self.players[self.now], self)

            self.my_ans = ''
            self.won = self.turn()

            self.my_ans = ''
            self.now = (self.now + 1) % self.n
            self.asked = False
        return

    def turn(self):
        pl = self.players[self.now]
        value = dice()

        bot.send_message(pl.id, 'You are ' + pl.place + '\ndice = ' + str(value))

        can_go = []
        for place in self.places:
            if dist(pl.place, place, self) <= value:
                can_go += [place]

        if len(can_go) == 0:
            self.my_ans = ''
            return

        if len(can_go) > 1:
            self.my_ans = ''
            bot.send_message(pl.id, "Where will you go?", reply_markup=make(can_go))
            self.choose_place = True
            while self.my_ans == '':
                pass
            pl.place = self.my_ans
            self.choose_place = False
            bot.send_message(pl.id, 'Now you are ' + pl.place)

        self.my_ans = ''
        bot.send_message(pl.id, 'Choose an action:', reply_markup=self.keyboard())

        while True:
            if self.my_ans == 'End turn':
                self.my_ans = ''
                return False

            if self.my_ans == 'Ask':
                self.my_ans = ''
                if not self.asked:
                    self.asking = True
                    self.asked = True
                    self.ask()
                    another = self.numberByName(self.now_chosen[0])
                    print(another, self.now_chosen[0])
                    if another is None:
                        pass
                    else:
                        self.players[another].place = self.now_chosen[2]
                    bot.send_message(pl.id, "Your choice is: " + ', '.join(self.now_chosen))
                    send_all(str(pl) + ": Was the murder committed by " + ' '.join(self.now_chosen) + "?", self,
                             [pl.id])
                    go(self.now, self)
                    if self.my_ans != 'NO' and self.my_ans != '':
                        pl.addCards(self.my_ans)
                    self.asking = False
                else:
                    bot.send_message(pl.id, "You have already asked")
                bot.send_message(pl.id, 'Choose an action:', reply_markup=self.keyboard())
                self.my_ans = ''
                self.asking = False

            if self.my_ans == 'Accuse':
                self.my_ans = ''
                self.accusing = True
                self.accuse()
                bot.send_message(pl.id, "Your choice is: " + ', '.join(self.now_chosen))
                flag = self.checking(self.now_chosen)
                self.my_ans = ''
                self.accusing = False
                return flag

        return False

    def end(self):
        for pl in self.players:
            personToGame[pl] = None

    def ask(self):
        pl = self.players[self.now]
        self.now_chosen = []
        bot.send_message(pl.id, "Choose a person: ", reply_markup=make(self.people))
        while len(self.now_chosen) != 1:
            pass
        bot.send_message(pl.id, "Choose a weapon: ", reply_markup=make(self.weapons))
        while len(self.now_chosen) != 2:
            pass
        self.now_chosen.append(pl.place)
        return

    def accuse(self):
        pl = self.players[self.now]
        self.now_chosen = []
        bot.send_message(pl.id, "Choose a person: ",
                         reply_markup=make(list(set(self.people).difference(pl.knownCards()))))
        while len(self.now_chosen) != 1:
            pass
        bot.send_message(pl.id, "Choose a weapon: ",
                         reply_markup=make(list(set(self.weapons).difference(pl.knownCards()))))
        while len(self.now_chosen) != 2:
            pass
        bot.send_message(pl.id, "Choose a place: ",
                         reply_markup=make(list(set(self.places).difference(pl.knownCards()))))
        while len(self.now_chosen) != 3:
            pass
        return

    def checking(self, ans):
        pl = self.players[self.now]
        if check_ans(ans, self):
            bot.send_photo(pl.id, open('win.png', 'rb'))
            send_all(str(pl) + " won the game!", self)
            send_all("The correct answer is: " + ', '.join(self.who_killed()), self, [pl.id])
            return True
        else:
            self.players[self.now].alive = False
            self.alive -= 1
            bot.send_photo(pl.id, open('lose.jpg', 'rb'))
            send_all(str(pl) + " accused: " + ', '.join(ans), self)
            send_all(str(pl) + " didn't guess correctly. He leaves the game! Ha-ha, what a loser!", self)
            bot.send_message(pl.id, "The correct answer is: " + ', '.join(self.who_killed()))

        if self.alive == 1:
            for i in range(self.n):
                pla = self.players[i]
                if pla.alive == True:
                    bot.send_photo(pla.id, open('win.png', 'rb'))
                    send_all(str(pla) + ' won the game!', self)
                    bot.send_message(pla.id, "The correct answer is: " + ', '.join(self.who_killed()))
                    break
            return True
        return False

    def hasPlayer(self, pl):
        for elem in self.players:
            if elem.id == pl.id:
                return True
        return False

    def numberById(self, id):
        for elem in self.players:
            if elem.id == id:
                return elem.number
        return None

    def numberByName(self, name):
        for elem in self.players:
            if str(elem.person) == str(name):
                return elem.number
        return None

    def who_killed(self):
        return self.ans

    def keyboard(self, cards=True, ask=True, accuse=True, finish=True):
        keys = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if cards:
            keys.row(telebot.types.KeyboardButton('Cards'))

        if ask and accuse:
            keys.row(telebot.types.KeyboardButton('Ask'), telebot.types.KeyboardButton('Accuse'))
        elif ask:
            keys.row(telebot.types.KeyboardButton('Ask'))
        elif accuse:
            keys.row(telebot.types.KeyboardButton('Accuse'))

        if finish:
            keys.row(telebot.types.KeyboardButton('End turn'))
        return keys

    def open(self):
        s = 'Open cards: ' + ', '.join(self.opencards)
        if s == 'Open cards: ':
            s = 'No open cards'
        return s

    def __str__(self):
        return str(game_by_id[self.id])

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def status(self):
        st = "started, " if self.started else ("waiting (" + str(self.max_players - len(self.players)) + '), ')
        if st == "started, ":
            return "Room " + str(game_by_id[self.id]) + ", " + st + ("room is empty" if len(self.players) == 0 else 'currently in room: ' + ', '.join(map(str, self.players)))
        else:
            return "Room " + str(game_by_id[self.id]) + ", " + st + ("room is empty" if len(self.players) == 0 else 'currently in room: ' + ', '.join(map(str, self.players))) + '  /join_' + str(game_by_id[self.id])


MAX_PLAYERS = 6
bot = telebot.TeleBot(TOKEN)
games = []

personToGame = dict()
game_by_id = dict()
cnt = 1


def running(gm):
    gm.start()
    gm.game()
    for play in gm.players:
        personToGame[play] = None
    last_id = game_by_id[gm.id] - 1
    games[last_id] = Game()
    game_by_id[games[last_id].id] = last_id + 1


# FINISHED = False
# active = []

# FINISHED = False
# active = []

file_name = 'logs.txt'


# @bot.message_handler()
# def trash(message):
# print(message.text)

def fromAdmin(message):
    return message.from_user.id in AdminId


def join_error(id):
    bot.send_message(id, 'Invalid command, please try again!')
    return


@bot.message_handler(commands=['new_game'], func=fromAdmin)
def addGame(message):
    global cnt

    if cnt > MAX_GAMES + MAX_GAMES // 2:
        pl = Player(User=message.from_user)
        bot.send_message(pl.id, "Max number of rooms created!")
        return
    gm = Game()
    games.append(gm)
    game_by_id[gm.id] = cnt
    cnt += 1
    sendAdmin('New game created')
    printLog('New game created')


@bot.message_handler(commands=['join'])
def add_player(message):
    pl = Player(User=message.from_user)
    if personToGame.get(pl, None) is not None:
        bot.send_message(pl.id, 'You are already in the game')
        return

    if not message.text.startswith('/join '):
        join_error(pl.id)
        return

    try:
        game_id = int(message.text[len('/join '):].replace('<', '').replace('>', ''))
    except:
        join_error(pl.id)
        return

    if game_id > len(games) or game_id < 1:
        bot.send_message(pl.id, "No such game!")
        return
    
    gm = games[game_id - 1]
    if gm.started:
        bot.send_message(pl.id, "This game has already started")
        return
    gm.addPlayers(pl)
    personToGame[pl] = gm
    bot.send_message(pl.id, "You join " + str(gm))
    send_all(str(gm) + ':\n' + playersList(gm), gm, bad=[pl.id])
    if len(gm.players) == gm.max_players:
        start_game(message)


@bot.message_handler(func=lambda message: message.text[:6] == '/join_')
def add_to_game(message):
    number = int(message.text[6:])
    try:
        gm = games[number - 1]
    except:
        gm = None

    if gm is None:
        bot.send_message(message.from_user.id, "No such game")
        return

    pl = Player(User = message.from_user)
    if personToGame.get(pl, None) is not None:
        bot.send_message(pl.id, 'You are already in the game')
        return
    gm.addPlayers(pl)
    personToGame[pl] = gm
    bot.send_message(pl.id, "You join game " + (str(gm)))
    try:
        send_all(str(gm) + ":\n" + playersList(gm), gm, bad=[pl.id])
    except:
        send_all(str(gm), gm, bad=[pl.id])
    if len(gm.players) == gm.max_players:
        start_game(message)

@bot.message_handler(commands=['leave'])
def deletePlayer(message):
    gm = getGame(message)
    pl = Player(User=message.from_user)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    if gm.deletePlayer(pl):
        bot.send_message(pl.id, 'You have successfully left the room ' + str(gm))
        send_all(str(pl) + ' leaves the room', gm)
        personToGame[pl] = None
    else:
        bot.send_message(pl.id, "The game has already started. You can't leave the room")
        
        
@bot.message_handler(commands=['game'])
def start_game(message):
    pl = Player(User=message.from_user)
    gm = personToGame.get(pl, None)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    else:
        new_thr = threading.Thread(name="Game " + str(gm), target=running, args=[gm])
        new_thr.start()


@bot.message_handler(commands=['status', 'active'], func=fromAdmin)
def status(message):
    print(message.text, len(games), 'admin')
    id = message.from_user.id
    ans = ''
    for gm in games:
        ans += gm.status() + '\n'
    if ans == '':
        ans = 'No games yet'
    bot.send_message(id, ans)

@bot.message_handler(commands=['status', 'active'])
def status(message):
    print(message.text, len(games))
    id = message.from_user.id
    ans = ''
    tmp = 0
    for gm in games:
        if not gm.started and (tmp == 0 or len(gm.players) != 0):
            ans += gm.status() + '\n'
            tmp += (len(gm.players) == 0)

    if ans == '':
        ans = 'No suitable games'
    bot.send_message(id, ans)


@bot.message_handler(commands=['players'])
def composition(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    if not gm.started:
        bot.send_message(pl.id, playersList(gm))
    else:
        ans = []
        for elem in gm.players:
            ans.append(str(elem) + ' is ' + elem.person)
        if ans == []:
            ans = ['No players yet']
        bot.send_message(pl.id, ', '.join(ans))


@bot.message_handler(commands=['cards'])
@bot.message_handler(func=lambda message: message.text == 'Cards')
def printCards(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    pl = gm.players[gm.numberById(pl.id)]
    text = ['', '\n', '\n', '\n\nOther cards\n', 'People: ', 'Weapons: ', 'Places: ']
    text[0] += gm.open()
    text[1] += 'Cards in your hand: ' + pl.cardsInHand()
    text[2] += 'Cards you know: ' + ', '.join(list(pl.know.difference(set(pl.cards)).difference(gm.opencards)))
    text[3] += ''
    text[4] += ', '.join(list(set(gm.people).difference(pl.know)))
    text[5] += ', '.join(list(set(gm.weapons).difference(pl.know)))
    text[6] += ', '.join(list(set(gm.places).difference(pl.know)))
    bot.send_message(pl.id, '\n'.join(text))
    if gm.numberById(pl.id) == gm.now and not gm.asking and not gm.choose_place:
        bot.send_message(pl.id, 'Choose an action:', reply_markup=gm.keyboard())
        return


@bot.message_handler(commands=['end'])
def gameEnd(message):
    global games, cnt
    pl = Player(User=message.from_user)
    if not (message.from_user.id in AdminId or getGame(pl) is None):
        bot.send_message(message.from_user.id, "Anton is a birch!")
        return
    elif message.from_user.id in AdminId:
        for gm in range(len(games)):
            for pl in games[gm].players:
                personToGame[pl] = None
                
            last_id = game_by_id[gm.id] - 1
            games[last_id] = Game()
            game_by_id[games[last_id].id] = last_id + 1
            
        broadcast("All the rooms are closed")
        return
    else:
        send_all('Game over. Do you want to start a new game?', getGame(pl))
        sendAdmin('Game over. Do you want to start a new game?')
        gm = personToGame.get(pl)
        for per in gm.players:
            personToGame[per] = None
        last_id = game_by_id[gm.id] - 1
        games[last_id] = Game()
        game_by_id[games[last_id].id] = last_id + 1



@bot.message_handler(commands=['rules'])
def printRules(message):
    bot.send_message(message.from_user.id, open('rules.txt', 'rt').read())

@bot.message_handler(commands=['help', 'how_use', 'start'])
def littleHelpMessege(message):
    text = ('/help - see this message again\n/full_help - see more help\n')
    bot.send_message(message.from_user.id, text)

@bot.message_handler(commands=['commands'])
def myCommands(message):
    bot.send_message(message.from_user.id, open('commands.txt', 'rt').read())

@bot.message_handler(commands=['full_help'])
def bigHelp(message):
    bot.send_message(message.from_user.id, open('help.txt', 'rt').read())

@bot.message_handler(commands=['full_end'], func=fromAdmin)
def botEnd(message):
    printLog('end of bot')
    broadcast('The bot has stopped. Game over. Sorry:(')
    sendAdmin('The bot has stopped. Game over. Sorry:(')
    print('full end')
    bot.stop_polling()


@bot.message_handler(func=lambda mess: getGame(mess) is None or messageType(mess) == 'ignore')
def ignore(message):
    pass
    return


@bot.message_handler(func=lambda mess: messageType(mess) == 'answer')
def gameAnswer(message):
    text = message.text
    gm = getGame(message)
    if text in gm.inter:
        gm.my_ans = text
    else:
        bot.send_message(message.from_user.id, 'Item is not found')

@bot.message_handler(func=lambda mess: messageType(mess) == 'ask')
def gameAsk(message):
    text = message.text
    gm = getGame(message)
    if text in gm.people + gm.weapons + gm.places:
        gm.now_chosen += [text]
    else:
        bot.send_message(message.from_user.id, 'Item is not found')

@bot.message_handler(func=lambda mess: messageType(mess) == 'place')
def gamePlace(message):
    text = message.text
    gm = getGame(message)
    if text in gm.places:
        gm.my_ans = text
    else:
        bot.send_message(message.from_user.id, 'Item is not found')

@bot.message_handler(func=lambda mess: messageType(mess) == 'accuse')
def gameAccuse(message):
    text = message.text
    gm = getGame(message)
    if text in gm.people + gm.weapons + gm.places:
        gm.now_chosen += [text]
    else:
        bot.send_message(message.from_user.id, 'Item is not found')

@bot.message_handler(func=lambda mess: messageType(mess) == 'turn')
def gameTurn(message):
    text = message.text
    gm = getGame(message)
    gm.my_ans = text

@bot.message_handler(func=lambda mess:mess.text[0] == '/')
def invalidCommand(message):
    bot.send_message(message.from_user.id, 'Invalid command')

@bot.message_handler()
def catch(message):
    sendAdmin("AAAAAAAAAAAA\nI am in 'catch' function. WHY?!&\nmessage is:\n" + message.text)
    return

def getGame(User):#raise 'TypeError'
    pl = User
    if isinstance(pl, telebot.types.Message):
        pl = pl.from_user
    if isinstance(pl, telebot.types.User):
        pl = Player(User = pl)
    elif not isinstance(pl, Player):
        raise TypeError
    gm = personToGame.get(pl, None)
    return gm

def messageType(message):
    gm = getGame(message)

    id = message.from_user.id
    now_id = gm.players[gm.now].id
    who = gm.who
    who_id = gm.players[gm.who].id
    if who != -1:
        if id == who_id:
            return 'answer'
        else:
            return 'ignore'
    if id != now_id:
        return 'ignore'

    if gm.asking:
        return 'ask'
    if gm.choose_place:
        return 'place'
    if gm.accusing:
        return 'accuse'
    if message.text in ['End turn', 'Ask', 'Accuse']:
        return 'turn'

    return 'ignore'

def playersList(gm):
    ans = []
    for elem in gm.players:
        ans.append(str(elem))
    if ans == []:
        ans = ['No players yet']
    return ', '.join(ans)


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


def go(index, gm):
    gm.my_ans = ''
    man = (index + 1) % gm.n
    while man != index and not answer(man, gm):
        gm.my_ans = ''
        man = (man + 1) % gm.n
    if man == index:
        send_all('Nobody can help!', gm)
    else:
        bot.send_message(gm.players[index].id, gm.my_ans + ' from ' + str(gm.players[man]))
        send_all('Answered by ' + str(gm.players[man]), gm, [gm.players[index].id, gm.players[man].id])
    gm.who = -1


def answer(man, gm):
    gm.who = man
    id = gm.players[man].id
    pl = gm.players[man]
    cards = set(pl.cards)
    now = set(gm.now_chosen)
    gm.inter = now.intersection(cards)

    if len(gm.inter) == 0:
        bot.send_message(id, "Choose an answer: ", reply_markup=make(['NO']))
        gm.inter = set(['NO'])
        while len(gm.my_ans) == 0:
            pass
        send_all(str(gm.players[man]) + " couldn't answer", gm, [gm.players[man].id])
        return False
    else:
        bot.send_message(id, "Choose an answer: ", reply_markup=make(list(inter)))
        while len(gm.my_ans) == 0:
            pass
        return True


def check_ans(arr, gm):
    return sorted(gm.who_killed()) == sorted(arr)


def broadcast(msg):
    for pl in personToGame:
        try:
            bot.send_message(pl.id, msg)
        except:
            pass


def send_all(msg, gm, bad=[]):
    for player in gm.players:
        if player.id not in bad:
            bot.send_message(player.id, msg)
    return


def sendAdmin(text):
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + text)


def send_turn(pl, gm):
    for player in gm.players:
        bot.send_message(player.id, "Now it's " + str(pl) + "'s turn")
    return


def printLog(text):
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
    log += str(year) + '.' + str(month) + '.' + str(day) + ' ' + str(hour) + ';' + str(minute) + ';' + str(
        seconds) + ').txt'
    return log


def dice():
    return rd.randrange(1, 7) + rd.randrange(1, 7)


def dist(place1, place2, gm):
    return gm.distance[gm.places.index(place1)][gm.places.index(place2)]


def main():
    global file_name
    file_name = logName()
    loggs = open(file_name, "w")
    loggs.close()
    games = []
    for i in range(MAX_GAMES):
        addGame('')
    sendAdmin('Bot starts')
    bot.polling()


if __name__ == '__main__':
    main()
print(__name__)
