# -*- coding: utf-8 -*-
import telebot
import time
import os
import random as rd
from copy import deepcopy
from copy import copy
import cluedo_cfg
import threading

TOKEN = # TOKEN HERE
MAX_GAMES = 10

MAX_PLAYERS = 6
bot = telebot.TeleBot(TOKEN)
games = []

AdminId = []
Admins = []

curr = 0
readyKeyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
readyKeyboard.row(telebot.types.KeyboardButton('Yes'), telebot.types.KeyboardButton('No'))


# removeKeyboard = telebot.types.ReplyKeyboardRemove()


class Player:
    def __init__(self,  # cards=[], number=-1,
                 id=186898465, username='TwoBlueCats', first_name='Anton', last_name='Anikushin',
                 user=None):
        self.cards = deepcopy(list())
        self.alive = True
        self.auto = False
        self.know = set(list())
        self.number = -1
        self.asked = False
        self.user = copy(user)
        self.place = 'classroom'
        self.person = 'matan'
        if user is None:
            self.user = telebot.types.User(id=id, username=username, first_name=first_name)
            self.id = id
            self.username = username
            self.first_name = first_name
            self.last_name = last_name
        else:
            self.id = user.id
            self.username = user.username
            self.first_name = user.first_name
            self.last_name = user.last_name

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

    def setUser(self, user):
        self.user = user
        self.id = user.id
        self.username = user.username
        self.first_name = user.first_name
        self.last_name = user.last_name

    def setNumber(self, num):
        self.number = num

    def setCards(self, cards):
        self.cards = deepcopy(cards)
        self.know = set(cards)

    def addCards(self, card):
        self.know.add(card)

    def cardsInHand(self):
        return ', '.join(self.cards)

    @property
    def knownCards(self):
        return self.know


class Game:
    def __init__(self):
        deck = deepcopy(cluedo_cfg.init())
        self.am_open = cluedo_cfg.cluedo_open
        self.people, self.weapons, self.places = deck.get()
        self.deck = deck.deck()
        self.ans = (rd.choice(self.people), rd.choice(self.weapons), rd.choice(self.places))
        self.distance = cluedo_cfg.distance
        self.opencards = []

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

        self.players = []
        self.alive = -1
        self.n = -1
        self.my_ans = ''
        self.now_chosen = []
        self.inter = set()
        self.who = -1

    def addPlayer(self, pl):
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
        self.n = len(self.players)
        self.alive = self.n
        n = self.n

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
            for card in self.opencards:
                self.players[i].addCards(card)

            self.players[i].place = rd.choice(self.places)
            self.players[i].person = rd.choice(other)
            other.remove(self.players[i].person)
            printLog(self.players[i].cards)
        for i in range(self.n):
            sendAll(str(self.players[i]) + ' is ' + self.players[i].person, self)

        self.started = True
        sendAdmin('Currently in ' + str(game_by_id[self.id]) + ': \n' + playersList(self))
        sendAll('Currently in game: \n' + playersList(self), self)

    def startPrint(self):
        sendAll("Cards in game", self)
        sendAll('People: ' + ', '.join(self.people), self)
        sendAll('Weapons: ' + ', '.join(self.weapons), self)
        sendAll('Places: ' + ', '.join(self.places), self)
        sendAll(self.open(), self)

    def game(self):
        while not self.won:
            while not self.players[self.now].alive or self.players[self.now].auto:
                if self.players[self.now].auto and self.players[self.now].alive:
                    sendAll(self.players[self.now] + ' in afk mode, skips a move', self)
                self.now = (self.now + 1) % self.n

            sendTurn(self.players[self.now], self)

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
            if pl.auto:
                pl.place = rd.choice(can_go)
            else:
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
                    sendAll(str(pl) + ": Was the murder committed by " + ' '.join(self.now_chosen) + "?", self,
                            [pl.id])
                    self.go(self.now)
                    if self.my_ans in self.deck:
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
                         reply_markup=make(list(set(self.people).difference(pl.knownCards))))
        while len(self.now_chosen) != 1:
            pass
        bot.send_message(pl.id, "Choose a weapon: ",
                         reply_markup=make(list(set(self.weapons).difference(pl.knownCards))))
        while len(self.now_chosen) != 2:
            pass
        bot.send_message(pl.id, "Choose a place: ",
                         reply_markup=make(list(set(self.places).difference(pl.knownCards))))
        while len(self.now_chosen) != 3:
            pass
        return

    def go(self, index):
        self.my_ans = ''
        man = (index + 1) % self.n
        while man != index and not self.answer(man):
            self.my_ans = ''
            man = (man + 1) % self.n
        if man == index:
            sendAll('Nobody can help!', self)
        else:
            bot.send_message(self.players[index].id, self.my_ans + ' from ' + str(self.players[man]))
            sendAll('Answered by ' + str(self.players[man]), self, [self.players[index].id, self.players[man].id])
        self.who = -1

    def answer(self, man):
        self.who = man
        pl = self.players[man]
        cards = set(pl.cards)
        now = set(self.now_chosen)
        self.inter = now.intersection(cards)
        print(pl.auto)
        if len(self.inter) == 0:
            if not pl.auto:
                self.inter = set()
                self.inter.add("I couldn't help you")
                bot.send_message(pl.id, "Choose an answer: ", reply_markup=make(["I couldn't help you"]))
                while len(self.my_ans) == 0:
                    pass
            else:
                self.my_ans = "I couldn't help you"
            sendAll(str(self.players[man]) + " couldn't answer", self, [self.players[man].id])
            return False
        else:
            if not pl.auto:
                bot.send_message(pl.id, "Choose an answer: ", reply_markup=make(list(self.inter)))
                while len(self.my_ans) == 0:
                    pass
            else:
                self.my_ans = rd.choice(list(self.inter))
            return True

    def checking(self, ans):
        pl = self.players[self.now]
        if checkAns(ans, self):
            bot.send_photo(pl.id, open('win.png', 'rb'))
            sendAll(str(pl) + " won the game!", self)
            sendAll("The correct answer is: " + ', '.join(self.whoKilled()), self, [pl.id])
            return True
        else:
            self.players[self.now].alive = False
            self.alive -= 1
            bot.send_photo(pl.id, open('lose.jpg', 'rb'))
            sendAll(str(pl) + " accused: " + ', '.join(ans), self)
            sendAll(str(pl) + " didn't guess correctly. He leaves the game! Ha-ha, what a loser!", self)
            bot.send_message(pl.id, "The correct answer is: " + ', '.join(self.whoKilled()))

        if self.alive == 1:
            for i in range(self.n):
                pla = self.players[i]
                if pla.alive:
                    bot.send_photo(pla.id, open('win.png', 'rb'))
                    sendAll(str(pla) + ' won the game!', self)
                    bot.send_message(pla.id, "The correct answer is: " + ', '.join(self.whoKilled()))
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

    def whoKilled(self):
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
            return "Room " + str(game_by_id[self.id]) + ", " + st + (
                "room is empty" if len(self.players) == 0 else 'currently in room: ' + ', '.join(
                    map(str, self.players)))
        else:
            return "Room " + str(game_by_id[self.id]) + ", " + st + (
                "room is empty" if len(self.players) == 0 else 'currently in room: ' + ', '.join(
                    map(str, self.players))) + '  /join_' + str(game_by_id[self.id])

    def check(self):
        cnt = 0
        for pl in self.players:
            if pl.alive is True and pl.auto is False:
                cnt += 1
        return cnt != 0

    def setDeck(self, deck):
        self.am_open = cluedo_cfg.cluedo_open
        self.people, self.weapons, self.places = deck.get()
        self.deck = deck.deck()
        self.ans = (rd.choice(self.people), rd.choice(self.weapons), rd.choice(self.places))
        self.distance = cluedo_cfg.distance
        self.opencards = []


personToGame = dict()
game_by_id = dict()
cnt = 1


def running(gm):
    try:
        gm.start()
    except Exception as error:
        printLog("Fail in game starting\n" + str(error))
        sendAdmin("Fail in game starting:\n" + str(error))
    else:
        try:
            gm.game()
        except Exception as error:
            printLog("Fail in game\n" + str(error))
            sendAdmin("Fail in game\n" + str(error))

    for play in gm.players:
        personToGame[play] = None

    last_id = game_by_id[gm.id] - 1
    games[last_id] = Game()
    game_by_id[games[last_id].id] = last_id + 1


def lowercase(s):
    ans = ""
    for i in s:
        if ord('A') <= ord(i) <= ord('Z'):
            ans += chr(ord(i) - ord('A') + ord('a'))
        else:
            ans += i
    return ans


file_name = 'logs.txt'


# @bot.message_handler()
# def trash(message):
#    print(message.text)

def fromAdmin(message):
    return message.from_user.id in AdminId


def command_error(id):
    bot.send_message(id, 'Invalid command, please try again!')
    return


# @bot.message_handler(commands=['auto'])
def setAuto(message):
    gm = getGame(message)
    pl = Player(user=message.from_user)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    pl = gm.players[gm.numberById(message.from_user.id)]
    if not pl.auto:
        sendAll(str(pl) + ' in afk mode', gm)
    else:
        sendAll(str(pl) + ' alive again', gm)
    pl.auto ^= True


@bot.message_handler(commands=['broadcast'], func=fromAdmin)
def forAll(message):
    broadcast(message.text)


@bot.message_handler(commands=['update'], func=fromAdmin)
def update(message):
    os.system('git pull')
    sendAdmin('Git update and run all')
    os.system('screen python3 cluedo_main.py')


@bot.message_handler(commands=['rerun'], func=fromAdmin)
def runCode(message):
    sendAdmin('Rerun all code')
    os.system('screen python3 cluedo_main.py')


@bot.message_handler(commands=['deck'], func=fromAdmin)
def printDecks(message):
    bot.send_message(message.from_user.id, ', '.join(cluedo_cfg.cluedo_deck_list))


@bot.message_handler(commands=['upfile'], func=fromAdmin)
def updateFiles(message):
    os.system('git pull')
    sendAdmin('Git update file')


@bot.message_handler(commands=['all'], func=fromAdmin)
def allRegister(message):
    for pl in personToGame.keys():
        bot.send_message(message.from_user.id, str(pl))


@bot.message_handler(commands=['full_end', 'restart'], func=fromAdmin)
def botEnd(message):
    printLog('end of bot')
    broadcast('The bot has stopped. Game over. Sorry:(')
    sendAdmin('The bot has stopped. Game over. Sorry:(')
    print('full end')
    bot.stop_polling()
    exit(0)


@bot.message_handler(commands=['log'], func=fromAdmin)
def sendLog(message):
    try:
        bot.send_document(message.from_user.id, open(file_name, "rb"))
    except Exception as error:
        bot.send_message(message.from_user.id, "Error in sending file" + ": " + str(error))


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


@bot.message_handler(commands=['set', 'set_deck'], func=lambda mes: mes.from_user.id == AdminId[0])  # only for me
def setDeck(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    deck_list = cluedo_cfg.admin_init()[0]
    bot.send_message(pl.id, "Deck list:\n" + "\n".join(deck_list))
    mes = bot.send_message(pl.id, "Choose any deck:", reply_markup=make(deck_list))
    bot.register_next_step_handler(mes, setDeck_2)


def setDeck_2(message):  # only for me, deck setting part 2
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    elif gm.started:
        bot.send_message(pl.id, "Game has already started")
        return
    res = cluedo_cfg.admin_init(message.text)
    gm.setDeck(res[2])
    bot.send_message(pl.id, "The successful establishment of the deck")


@bot.message_handler(commands=['new_game'])
def addGame(message):
    global cnt

    if cnt > MAX_GAMES + MAX_GAMES // 2:
        pl = Player(user=message.from_user)
        bot.send_message(pl.id, "Max number of rooms created!")
        return
    gm = Game()
    games.append(gm)
    game_by_id[gm.id] = cnt
    cnt += 1
    sendAdmin('New game created')
    printLog('New game created')


@bot.message_handler(commands=['join'])
def addPlayer(message):
    pl = Player(user=message.from_user)
    if personToGame.get(pl, None) is not None:
        bot.send_message(pl.id, 'You are already in the game')
        return
    personToGame[pl] = None

    try:
        game_id = int(message.text[len('/join '):].replace('<', '').replace('>', ''))
    except Exception as error:
        suitable = []
        tmp = 0
        ind = 0
        for gm in games:
            if not gm.started and (tmp == 0 or len(gm.players) != 0):
                suitable += [ind]
                tmp += (len(gm.players) == 0)
            ind += 1
        if not suitable:
            bot.send_message(pl.id, "No suitable games")
            return
        game_id = rd.choice(suitable) + 1

    if game_id > len(games) or game_id < 1:
        bot.send_message(pl.id, "No such game!")
        return

    gm = games[game_id - 1]
    if gm is None:
        sendAdmin("Something goes wrong in joining to game. Game does not exist")
        printLog("Game number = game_id")
        sendAdmin("I reInit this game")

        games[game_id] = Game()
        game_by_id[games[game_id].id] = game_id + 1

    if gm.started:
        bot.send_message(pl.id, "This game has already started")
        return
    gm.addPlayer(pl)
    personToGame[pl] = gm
    bot.send_message(pl.id, "You join game " + str(gm), reply_markup=readyKeyboard)
    sendAll(str(gm) + ':\n' + playersList(gm), gm, bad=[pl.id])


@bot.message_handler(func=lambda message: message.text[:6] == '/join_')
def add_to_game(message):
    number = int(message.text[6:])
    try:
        gm = games[number - 1]
    except Exception as error:
        gm = None

    if gm is None:
        bot.send_message(message.from_user.id, "No such game")
        return

    pl = Player(user=message.from_user)
    if personToGame.get(pl, None) is not None:
        bot.send_message(pl.id, 'You are already in the game')
        return
    gm.addPlayer(pl)
    personToGame[pl] = gm
    bot.send_message(pl.id, "You join game " + str(gm), reply_markup=readyKeyboard)
    sendAll(str(gm) + ":\n" + playersList(gm), gm, bad=[pl.id])


@bot.message_handler(func=lambda mess: messageType(mess) == 'ready')
def readyGame(message):
    gm = getGame(message)
    pl = Player(user=message.from_user)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    if message.text == 'Yes':
        gm.ready.add(pl)
    else:
        gm.ready.discard(pl)

    if gm.ready == set(gm.players):
        sendAll('All the players are ready to start', gm)


@bot.message_handler(commands=['leave'])
def deletePlayer(message):
    gm = getGame(message)
    pl = Player(user=message.from_user)
    if gm is None:
        bot.send_message(pl.id, 'You do not take part in any game')
        return
    if gm.deletePlayer(pl):
        bot.send_message(pl.id, 'You have successfully left the room ' + str(gm))
        sendAll(str(pl) + ' leaves the room', gm)
        personToGame[pl] = None
    else:
        bot.send_message(pl.id, "The game has already started. You can't leave the room")


@bot.message_handler(commands=['game'])
def start_game(message):
    pl = Player(user=message.from_user)
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
            bot.send_message(pl.id,
                             "Not all players of the room ready to start.\nWait for them to start: " + ', '.join(ans))


@bot.message_handler(commands=['status', 'active'])
def status(message):
    print(message.text, len(games))
    id = message.from_user.id
    ans = ''
    tmp = 0
    ind = 0
    for gm in games:
        if not gm.started and (tmp == 0 or len(gm.players) != 0):
            ans += gm.status() + '\n'
            tmp += (len(gm.players) == 0)
        ind += 1
    if ans == '':
        ans = 'No suitable games\nYou can start new(see /full_help)'
    bot.send_message(id, ans)


@bot.message_handler(commands=['players'], func=lambda mess: getGame(mess) is None)
def composition(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return


@bot.message_handler(commands=['players'], func=lambda mess: getGame(mess) is not None and not getGame(mess).started)
def composition(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    ans = []
    for elem in gm.players:
        ans.append(str(elem) + ' is ready' * (elem in gm.ready))
    bot.send_message(pl.id, '\n'.join(ans))


@bot.message_handler(commands=['players'], func=lambda mess: getGame(mess) is not None and getGame(mess).started)
def composition(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    ans = []
    for elem in gm.players:
        ans.append(str(elem) + ' is ' + elem.person + ' ' + elem.place + ' is afk' * elem.auto)
    bot.send_message(pl.id, '\n'.join(ans))


@bot.message_handler(commands=['turn'])
def WhoseTurn(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    bot.send_message(pl.id, gm.players[gm.now])


@bot.message_handler(commands=['cards'])
@bot.message_handler(func=lambda message: message.text == 'Cards')
def printCards(message):
    pl = Player(user=message.from_user)
    gm = getGame(pl)
    if gm is None:
        bot.send_message(pl.id, 'Please, join any game')
        return
    pl = gm.players[gm.numberById(pl.id)]
    text = ['', '\n', '\n', '\n\nOther cards\n', 'People: ', '\nWeapons: ', '\nPlaces: ']
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
    pl = Player(user=message.from_user)
    if not (message.from_user.id in AdminId or getGame(pl) is None):
        bot.send_message(message.from_user.id, "Admin is a birch!")
        return
    elif message.from_user.id in AdminId:
        for gm in range(len(games)):
            for pl in games[gm].players:
                personToGame[pl] = None

            last_id = game_by_id[games[gm].id] - 1
            games[last_id] = Game()
            game_by_id[games[last_id].id] = last_id + 1

        broadcast("All the rooms are closed")
        return
    else:
        sendAll('Game over. Do you want to start a new game?', getGame(pl))
        sendAdmin('Game over. Do you want to start a new game?')
        gm = personToGame.get(pl)
        for per in gm.players:
            personToGame[per] = None
        last_id = game_by_id[gm.id] - 1
        games[last_id] = Game()
        game_by_id[games[last_id].id] = last_id + 1


@bot.message_handler(commands=['rules'])
def printRules(message):
    bot.send_message(message.from_user.id, open('rules.txt', 'rt', encoding="utf-8").read())


@bot.message_handler(commands=['help', 'how_use', 'start'])
def littleHelpMessege(message):
    text = ('/help - see this message again\n/full_help - see more help\n')
    text += 'Firstly send /status, after it join any suitable room'
    bot.send_message(message.from_user.id, text)


@bot.message_handler(commands=['commands'])
def myCommands(message):
    bot.send_message(message.from_user.id, open('commands.txt', 'rt', encoding="utf-8").read())


@bot.message_handler(commands=['full_help'])
def bigHelp(message):
    bot.send_message(message.from_user.id, open('help.txt', 'rt', encoding="utf-8").read())


@bot.message_handler(commands=['feedback'])
def feedback(message):
    sendAdmin("feedback by " + str(Player(message.from_user)) + ": " + message.text.replace('/feedback', '', 1))


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
    if lowercase(text).replace('/', '') == 'ask':
        gm.my_ans = 'Ask'
    if lowercase(text).replace('/', '') == 'accuse':
        gm.my_ans = 'Accuse'
    if lowercase(text).replace('/', '') in ['end turn', 'end_turn']:
        gm.my_ans = 'End turn'


@bot.message_handler(func=lambda mess: mess.text[0] == '/')
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


def getGame(User):  # raise 'TypeError'
    pl = User
    if isinstance(pl, telebot.types.Message):
        pl = pl.from_user
    if isinstance(pl, telebot.types.User):
        pl = Player(user=pl)
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
    if lowercase(message.text).replace('/', '') in ['end turn', 'ask', 'accuse', 'end_turn']:
        return 'action'

    return 'ignore'


def playersList(gm):
    ans = []
    for elem in gm.players:
        ans.append(str(elem))
    if not ans:
        ans = ['No players yet']
    return ', '.join(ans)


def make(arr):
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
        pass
    elif d == 1:
        now.row(telebot.types.KeyboardButton(arr[i + 0]))
    elif d == 2:
        now.row(telebot.types.KeyboardButton(arr[i + 0]), telebot.types.KeyboardButton(arr[i + 1]))
    return now


def checkAns(arr, gm):
    return sorted(gm.whoKilled()) == sorted(arr)


def broadcast(msg):
    for pl in personToGame:
        try:
            bot.send_message(pl.id, msg)
        except Exception as error:
            personToGame.pop(pl)
            pass


def sendAll(msg, gm, bad=None):
    if bad is None:
        bad = []
    for player in gm.players:
        if player.id not in bad:
            bot.send_message(player.id, msg)
    return


def sendAdmin(text):
    for admin in Admins:
        bot.send_message(admin.id, 'Admin {0} {1}: '.format(admin.first_name, admin.last_name) + str(text))


def sendTurn(pl, gm):
    sendAll("Now it's " + str(pl) + "'s turn", gm)
    return


def printLog(text):
    global file_name
    logs = open(file_name, "a")
    logs.write(str(text) + '\n\n')
    logs.close()


def logName():
    log = "game_of_"
    today = time.gmtime()
    year = today.tm_year
    month = today.tm_mon
    day = today.tm_mday
    hour = today.tm_hour
    minute = today.tm_min
    seconds = today.tm_sec
    log += "0" * (day < 10) + str(day) + '_' + "0" * (month < 10) + str(month) + '_' + str(year) + '__' + "0" * (
        hour < 10) + str(hour) + '_' + "0" * (minute < 10) + str(minute) + '_' + "0" * (seconds < 10) + str(
        seconds) + '.txt'
    return log


def dice():
    return rd.randrange(1, 7) + rd.randrange(1, 7)


def dist(place1, place2, gm):
    return gm.distance[gm.places.index(place1)][gm.places.index(place2)]


def main():
    global file_name, games
    cluedo_cfg.init()
    file_name = logName()
    loggs = open(file_name, "w")
    loggs.close()
    games = []
    for i in range(MAX_GAMES):
        addGame('')
    sendAdmin('Bot starts')
    while True:
        try:
            bot.polling()
        except Exception as error:
            printLog(error)
            sendAdmin(str(error))
            sendAdmin("I sleep 10 seconds and continue working")
            time.sleep(10)
            sendAdmin("I continue working")
        else:
            break


if __name__ == '__main__':
    main()
