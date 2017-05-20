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

TOKEN = "303602093:AAGz6ihk895s3K07vYqc6eBY8InFwX4YuhQ"
TOKEN2 = "286496122:AAGED92TDcccXHGJmgyz5oJcCcZ4TI-vTrM"
MAX_GAMES = 10

AdminId = [186898465, 319325008]
Admins = [telebot.types.User(id=186898465, username='antonsa', first_name='Anton', last_name='Anikushin'),
          telebot.types.User(id=319325008, username='greatkorn', first_name='Anton', last_name='Kvasha')]

curr = 0
readyKeyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
readyKeyboard.row(telebot.types.KeyboardButton('Yes'), telebot.types.KeyboardButton('No'))

class Player:
    def __init__(self, cards=[], id=186898465, username='antonsa', number=-1, first_name='Anton', last_name='Anikushin',
                 User=None):
        self.cards = deepcopy(cards)
        self.alive = True
        self.auto = False
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
        self.ready = set()
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
        sendAdmin(str(pl) + ' joined ' + str(self))
        self.players += [pl]
    
    def deletePlayer(self, pl):
        if not self.started:
            self.players.pop(self.players.index(pl))
            self.ready.discard(pl)
            sendAdmin(str(pl) + ' leaves ' + str(self))
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
            while not self.players[self.now].alive or self.players[self.now].auto:
                if self.players[self.now].auto and self.players[self.now].alive:
                    send_all(self.players[self.now] + ' in afk mode, skips a move')
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
                    self.go(self.now)
                    if self.my_ans != "I couldn't help you" and self.my_ans != '':
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
        
        
    #######
    #######
    def go(self, index):
        self.my_ans = ''
        man = (index + 1) % self.n
        while man != index and not self.answer(man):
            self.my_ans = ''
            man = (man + 1) % self.n
        if man == index:
            send_all('Nobody can help!', self)
        else:
            bot.send_message(self.players[index].id, self.my_ans + ' from ' + str(self.players[man]))
            send_all('Answered by ' + str(self.players[man]), self, [self.players[index].id, self.players[man].id])
        self.who = -1


    def answer(self, man):
        self.who = man
        pl = self.players[man]
        id = pl.id
        cards = set(pl.cards)
        now = set(self.now_chosen)
        self.inter = now.intersection(cards)
        print(pl.auto)
        if len(self.inter) == 0:
            if not pl.auto:
                bot.send_message(id, "Choose an answer: ", reply_markup=make(["I couldn't help you"]))
                self.inter = set(["I couldn't help you"])
                while len(self.my_ans) == 0:
                    pass
            else:
                self.my_ans = "I couldn't help you"
            send_all(str(self.players[man]) + " couldn't answer", self, [self.players[man].id])
            return False
        else:
            if not pl.auto:
                bot.send_message(id, "Choose an answer: ", reply_markup=make(list(self.inter)))
                while len(self.my_ans) == 0:
                    pass
            else:
                self.my_ans = rd.choice(list(self.inter))
            return True
        
    ######
    ######
    
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

    def keyboard(self):
        keys = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keys.row(telebot.types.KeyboardButton('Cards'))
        keys.row(telebot.types.KeyboardButton('Ask'), telebot.types.KeyboardButton('Accuse'))
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
    
    def check(self):
        cnt = 0
        for pl in self.players:
            if pl.alive is True and pl.auto is False:
                cnt += 1
        return cnt != 0
        
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


file_name = 'logs.txt'

#@bot.message_handler()
#def trash(message):
#    print(message.text)

def fromAdmin(message):
    return message.from_user.id in AdminId


def join_error(id):
    bot.send_message(id, 'Invalid command, please try again!')
    return

#@bot.message_handler(commands=['auto'])
def setAuto(message):
    gm = getGame(message)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    pl = gm.players[gm.numberById(message.from_user.id)]
    if not pl.auto:
        send_all(str(pl) + ' in afk mode', gm)
    else:
        send_all(str(pl) + ' alive again', gm)
    pl.auto ^= True
    
    
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
    personToGame[pl] = None
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
    bot.send_message(pl.id, "You join game " + str(gm), reply_markup=readyKeyboard)
    send_all(str(gm) + ':\n' + playersList(gm), gm, bad=[pl.id])


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
    bot.send_message(pl.id, "You join game " + str(gm), reply_markup=readyKeyboard)
    try:
        send_all(str(gm) + ":\n" + playersList(gm), gm, bad=[pl.id])
    except:
        send_all(str(gm), gm, bad=[pl.id])

@bot.message_handler(func=lambda mess: messageType(mess) == 'ready')
def readyGame(message):
    gm = getGame(message)
    pl = Player(User=message.from_user)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    if message.text == 'Yes':
        gm.ready.add(pl)
    else:
        gm.ready.discard(pl)
        
    if gm.ready == set(gm.players):
        send_all('All the players are ready to start', gm)

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
        if gm.ready == set(gm.players):
            new_thr = threading.Thread(name="Game " + str(gm), target=running, args=[gm])
            new_thr.start()
        else:
            ans = []
            for i in gm.players:
            	if i not in gm.ready:
            		ans += [str(i)]
            bot.send_message(pl.id, "Not all players of the room ready to start.\nWait for them to start: " + ', '.join(ans))

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


@bot.message_handler(commands=['players'], func=lambda mess: getGame(mess) is None)
def composition(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
        
@bot.message_handler(commands=['players'], func=lambda mess: not getGame(mess).started)
def composition(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    ans = []
    for elem in gm.players:
        ans.append(str(elem) + ' is ready' * (elem in gm.ready))
    bot.send_message(pl.id, '\n'.join(ans))
    
@bot.message_handler(commands=['players'], func=lambda mess: getGame(mess).started)
def composition(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    ans = []
    for elem in gm.players:
        ans.append(str(elem) + ' is ' + elem.person + ' ' + elem.place + (' is afk') * elem.auto)
    bot.send_message(pl.id, '\n'.join(ans))

@bot.message_handler(commands=['turn'])
def WhoseTurn(message):
    pl = Player(User=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    bot.send_message(pl.id, gm.players[gm.now])
    
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
    text += '''Firstly send /status, after it join any suitable room'''    
    bot.send_message(message.from_user.id, text)

@bot.message_handler(commands=['commands'])
def myCommands(message):
    bot.send_message(message.from_user.id, open('commands.txt', 'rt').read())

@bot.message_handler(commands=['full_help'])
def bigHelp(message):
    bot.send_message(message.from_user.id, open('help.txt', 'rt').read())

@bot.message_handler(commands=['feedback'])
def feedback(message):
    sendAdmin(message.text.replace('/feedback', '', 1))
    
@bot.message_handler(commands=['full_end'], func=fromAdmin)
def botEnd(message):
    printLog('end of bot')
    broadcast('The bot has stopped. Game over. Sorry:(')
    sendAdmin('The bot has stopped. Game over. Sorry:(')
    print('full end')
    bot.stop_polling()

@bot.message_handler(commands=['broadcast'], func=fromAdmin)
def forAll(message):
    broadcast(message.text)

@bot.message_handler(commands=['update'], func=fromAdmin)
def update(message):
    os.system('git pull')
    sendAdmin('Git update and run all')
    os.system('screen python3 flows_main.py')

@bot.message_handler(commands=['run'], func=fromAdmin)
def runCode(message):
    sendAdmin('Rerun all code')
    os.system('screen python3 flows_main.py')    

@bot.message_handler(commands=['deck'], func=fromAdmin)
def printDecks(message):
    bot.send_message(message.from_user.id, ', '.join(cfg.cluedo_deck_list))
    
@bot.message_handler(commands=['upfile'], func=fromAdmin)
def updateFiles(message):
    os.system('git pull')
    sendAdmin('Git update file')
    
@bot.message_handler(commands=['all'], func=fromAdmin)
def allRegister(message):
    for pl in personToGame.keys():
        bot.send_message(message.from_user.id, str(pl))
    

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

@bot.message_handler(func=lambda mess: messageType(mess) == 'action')
def gameTurn(message):
    text = message.text
    gm = getGame(message)
    gm.my_ans = text

@bot.message_handler(func=lambda mess:mess.text[0] == '/')
def invalidCommand(message):
    print(message.text)
    bot.send_message(message.from_user.id, 'Invalid command')

@bot.message_handler(func=lambda mess: getGame(mess) is None or messageType(mess) == 'ignore')
def ignore(message):
    pass
    return    
    
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
    if gm is None:
        return 'ignore'
        
    if not gm.started:
        if message.text in ['Yes', 'No']:
            return 'ready'
        return 'ignore'
        
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
        return 'action'

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
    cfg.cluedo_init()
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
