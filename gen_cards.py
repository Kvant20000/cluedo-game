import random as rd


am_open = [0, 0, 0, 0, 2, 3, 0] # other option is [0, 0, 0, 6, 6, 3, 6]
people = ["Ворона", "Берёза", "Князь Пожарский", "Васечка", "Афганский мафиози", "СВ"] #КТО?
weapons = ["Тихим Доном", "клавиатурой", "выносом мозга", "тупыми мемами", "коробкой из-под пиццы", "огнетушителем"] #ЧЕМ?
places = ["в 209", "у психолога", "в Маке", "на футбольном поле", "в электричке", "в актовом зале", "в ТЦ Охотный", "у выхода из метро", "в офисе 1С"] #ГДЕ?

class Player:
    def __init__(self, A):
        self.cards = A
        
    def __str__(self):
        return ', '.join(self.cards)

class Game:
    def __init__(self, n): # n players
        self.ans = (rd.choice(people), rd.choice(weapons), rd.choice(places)) #the answer
        
        deck = people + weapons + places
        for i in self.ans:
            deck.remove(i)
        rd.shuffle(deck) #so i shuffled
        
        self.opencrds = deck[:am_open[n]]
        am_per_player = (len(deck) - am_open[n]) // n
        self.players = [Player(deck[i: i + am_per_player]) for i in range(am_open[n], len(deck), am_per_player)]
        
    def __str__(self):
        s = "Убийство совершил " + ' '.join(self.ans) + '\n'
        s += "Открытые карты: " + ', '.join(self.opencrds) + '\n'
        for i in range(len(self.players)):
            s += "У игрока " + str(i + 1) + " карты: " + str(self.players[i]) +  '\n'
        return s
    
            
game = Game(3)
print(game)
