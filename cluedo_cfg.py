import random as rd
from copy import copy

'''
CLUEDO
'''

cluedo_open = [0, 0, 0, 6, 6, 3, 6]  # , [0, 0, 0, 0, 2, 3, 0]
cluedo_people = ["Miss Scarlett", "Professor Plum", "Lady Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
cluedo_places = ["kitchen", "ballroom", "conservatory", "billiard room", "library", "study", "lounge", "hall",
                 "dining room"]
cluedo_weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
cluedo_deck_list = ["classic"]

distance = [[0, 4, 9, 9, 9, 0, 8, 9, 5],
            [4, 0, 7, 7, 7, 10, 6, 9, 6],
            [9, 7, 0, 4, 5, 9, 8, 0, 10],
            [9, 7, 4, 0, 3, 8, 7, 10, 9],
            [9, 7, 5, 3, 0, 7, 6, 9, 8],
            [0, 10, 9, 8, 7, 0, 4, 7, 8],
            [8, 6, 8, 7, 6, 4, 0, 5, 6],
            [9, 9, 0, 10, 9, 7, 5, 0, 5],
            [5, 6, 10, 9, 8, 8, 6, 5, 0]]


class CluedoDeck:
    def __init__(self, ppl=[], wps=[], pls=[]):
        self.people = ppl
        self.weapons = ["with a " + i for i in wps]  # very bad!
        self.places = pls  # very very bad!

    def get(self):
        return copy(self.people), copy(self.weapons), copy(self.places)

    def deck(self):
        return self.people + self.weapons + self.places


def init():
    global cluedo_people, cluedo_places, cluedo_weapons, cluedo_deck_list
    people = ["Miss Scarlett", "Professor Plum", "Lady Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
    places = ["in the kitchen", "in the ballroom", "in the conservatory", "in the billiard room", "in the library",
              "in the study", "in the lounge", "in the hall", "in the dining room"]
    weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
    classic_deck = CluedoDeck(people, weapons, places)

    people = ["Draco Malfoy", "Bellatrix Lestrange", "Dolores Umbridge", "Peter Pettigrew", "Crabbe & Goyle",
              "Grindelwald"]
    places = ["in the Owlery", "in the Trophy room", "in the library", "in the DADA classroom", "in the Great Hall",
              "in the hospital wing", "in the Room of Requirements", "in the Potions classroom",
              "in the Divination classroom"]
    weapons = ["Bat-Bogey hex", "Stupefy", "Petrificus totalus", "Cruciatus curse", "Killing curse", "Confundus charm"]
    Harry_Potter_deck = CluedoDeck(people, weapons, places)

    people = ["Darth Vader", "Han Solo", "Yoda", "Obi-Wan «Ben» Kenobi", "Luke Skywalker", "Leia Organa Solo"]
    places = ["on the Naboo", "on the Tatooine", "on the Coruscant", "on the Alderaan", "on the Yavin 4",
              "on the Kamino", "on the Corellia", "on the Dantooine", "on the Kessel"]
    weapons = ["lightsaber", "blaster", "thermal detonator", "proton torpedoes", "shotguns", "bowcaster"]
    Star_Wars_deck = CluedoDeck(people, weapons, places)

    people = ["Indy", "Han Solo", "Rick Deckard", "Dr. Richard Kimble", "John Book", "Colonel Graff"]
    places = ["in Egypt", "in the Temple of Doom", "in Alexandretta", "in Los Angeles", "in Lancaster County",
              "in Chicago", "a long time ago in a galaxy far, far away...", "on Eros", "on Lusitania"]
    weapons = ["whip", "blaster", "shotgun", "pistol", "airplane", "small child"]
    Harrison_Ford_deck = CluedoDeck(people, weapons, places)

    decks = [classic_deck, Harry_Potter_deck, Star_Wars_deck, Harrison_Ford_deck]  # , SIS_deck]#, vasechka_deck]
    cluedo_deck_list = ["classic", "Harry Potter", "Star Wars", "Harrison Ford"]  # , SIS_deck]#, vasechka_deck]
    return rd.choice(decks)


def admin_init(name=None):
    people = ["Miss Scarlett", "Professor Plum", "Lady Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
    places = ["in the kitchen", "in the ballroom", "in the conservatory", "in the billiard room", "in the library",
              "in the study", "in the lounge", "in the hall", "in the dining room"]
    weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
    classic_deck = CluedoDeck(people, weapons, places)

    people = ["Draco Malfoy", "Bellatrix Lestrange", "Dolores Umbridge", "Peter Pettigrew", "Crabbe & Goyle",
              "Grindelwald"]
    places = ["in the Owlery", "in the Trophy room", "in the library", "in the DADA classroom", "in the Great Hall",
              "in the hospital wing", "in the Room of Requirements", "in the Potions classroom",
              "in the Divination classroom"]
    weapons = ["Bat-Bogey hex", "Stupefy", "Petrificus totalus", "Cruciatus curse", "Killing curse", "Confundus charm"]
    Harry_Potter_deck = CluedoDeck(people, weapons, places)

    people = ["Darth Vader", "Han Solo", "Yoda", "Obi-Wan «Ben» Kenobi", "Luke Skywalker", "Leia Organa Solo"]
    places = ["on the Naboo", "on the Tatooine", "on the Coruscant", "on the Alderaan", "on the Yavin 4",
              "on the Kamino", "on the Corellia", "on the Dantooine", "on the Kessel"]
    weapons = ["lightsaber", "blaster", "thermal detonator", "proton torpedoes", "shotguns", "bowcaster"]
    Star_Wars_deck = CluedoDeck(people, weapons, places)

    people = ["Indy", "Han Solo", "Rick Deckard", "Dr. Richard Kimble", "John Book", "Colonel Graff"]
    places = ["in Egypt", "in the Temple of Doom", "in Alexandretta", "in Los Angeles", "in Lancaster County",
              "in Chicago", "a long time ago in a galaxy far, far away...", "on Eros", "on Lusitania"]
    weapons = ["whip", "blaster", "shotgun", "pistol", "airplane", "small child"]
    Harrison_Ford_deck = CluedoDeck(people, weapons, places)

    people = ["Vasechka #1", "Vasechka #2", "Vasechka #3", "Vasechka #4", "Vasechka #5", "Vasechka #6", "Vasechka #7",
              "Vasechka #8", "Vasechka #9"]
    places = ["in the SPBAU", "in the ITMO", "in the MSU", "in the HSE", "in the MIPT", "in the middle of nowhere"]
    weapons = ["Dijkstra algorithm", "DFS", "big, big treap", "CENSORED", "suffix tree", "very big segment tree"]
    vasechka_deck = CluedoDeck(people, weapons, places)

    people = ["Andrew", "DK", "SES", "Demid", "Kopeliovich", "Administration"]
    places = ["in the main building", "in the 10th house", "in the dining room", "in the computer class",
              "in the medical center", "in the ship", "in the necromantic", "on the Khutor", "on the football field"]
    weapons = ["ejudge", "polygon", "hole punch", "bike", "computer", "test"]
    SIS_deck = CluedoDeck(people, weapons, places)

    decks = [classic_deck, Harry_Potter_deck, Star_Wars_deck, Harrison_Ford_deck, vasechka_deck, SIS_deck]
    deck_list = ["classic", "Harry Potter", "Star Wars", "Harrison Ford", "vasechka", "SIS"]
    if name not in deck_list:
        return [deck_list, False, None]
    else:
        return [deck_list, True, decks[deck_list.index(name)]]
