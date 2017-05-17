import random as rd #i am the best translator ever!

cluedo_open = [0, 0, 0, 6, 6, 3, 6]#[0, 0, 0, 0, 2, 3, 0]
cluedo_people = ["Miss Scarlett", "Professor Plum", "Lady Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
cluedo_places = ["kitchen", "ballroom", "conservatory",  "billiard room", "library", "study", "lounge", "hall", "dining room"]
cluedo_weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
cluedo_deck_list = ['normal']

cluedo_dist =  [[ 0,  4,  9,  9,  9,  0,  8,  9,  5],
                [ 4,  0,  7,  7,  7, 10,  6,  9,  6],
                [ 9,  7,  0,  4,  5,  9,  8,  0, 10],
                [ 9,  7,  4,  0,  3,  8,  7, 10,  9],
                [ 9,  7,  5,  3,  0,  7,  6,  9,  8],
                [ 0, 10,  9,  8,  7,  0,  4,  7,  8],
                [ 8,  6,  8,  7,  6,  4,  0,  5,  6],
                [ 9,  9,  0, 10,  9,  7,  5,  0,  5],
                [ 5,  6, 10,  9,  8,  8,  6,  5,  0]]

class CluedoDeck:
    def __init__(self, ppl = [], wps = [], pls = []):
        self.people = ppl
        self.weapons = ["with a " + i for i in wps] #very bad!
        self.places = ["in the " + i for i in pls] #very very bad!

    def get(self):
        return self.people, self.weapons, self.places

def cluedo_init():
    global cluedo_people, cluedo_places, cluedo_weapons, cluedo_deck_list
    people = ["Miss Scarlett", "Professor Plum", "Lady Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
    places = ["kitchen", "ballroom", "conservatory",  "billiard room", "library", "study", "lounge", "hall", "dining room"]
    weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
    normal_deck = CluedoDeck(people, weapons, places)

    people = ["Draco Malfoy", "Bellatrix Lestrange", "Dolores Umbridge", "Peter Pettigrew", "Crabbe & Goyle", "Grindelwald"]
    places = ["Owlery", "Trophy room", "library", "DADA classroom", "Great Hall", "hospital wing", "Room of Requirements", "Potions classroom", "Divination classroom"]
    weapons = ["Bat-Bogey hex", "Stupefy", "Petrificus totalus", "Cruciatus curse", "Killing curse", "Confundus charm"]
    hp_deck = CluedoDeck(people, weapons, places)

    #people = ["Vasechka #1", "Vasechka #2", "Vasechka #3", "Vasechka #4", "Vaseckha #5", "Vaseckha #6", "Vaseckha #7", "Vaseckha #8", "Vaseckha #9"]
    #places = ["SPBAU", "ITMO", "MSU", "HSE", "MIPT", "middle of nowhere"]
    #weapons = ["Dijkstra algorithm", "DFS", "big, big treap", "CENSORED", "suffix tree", "very big segment tree"]
    #vasechka_deck = CluedoDeck(people, weapons, places)

    people = ['Darth Vader', 'Mace Windu', 'Yoda', 'Obi-Wan «Ben» Kenobi', 'Luke Skywalker', 'Leia Organa Solo']
    places = ['Naboo', 'Tatooine', 'Coruscant', 'Alderaan', 'Yavin 4', 'Kamino', 'Corellia', 'Dantooine', 'Kessel']
    weapons = ['lightsaber', 'blaster', 'thermal detonator', 'proton torpedoes', 'shotguns', 'bowcaster']
    starWars_deck = CluedoDeck(people, weapons, places)

    decks = [normal_deck, hp_deck, starWars_deck]#, vasechka_deck]
    cluedo_deck_list = ['normal', 'Harry Potter', 'Star Wars']#, vasechka_deck]
    cluedo_people, cluedo_weapons, cluedo_places = rd.choice(decks).get()
