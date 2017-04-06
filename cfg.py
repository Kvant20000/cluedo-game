import random as rd #i am the best translator ever!


cluedo_open = [0, 0, 0, 6, 6, 3, 6] #[0, 0, 0, 0, 2, 3, 0]

class deck:
	def __init__(self, ppl = [], wps = [], pls = []):
		self.people = ppl
		self.weapons = ["with a " + i for i in wps] #very bad!
		self.places = ["in the " + i for i in pls] #very very bad!

	def get(self):
		return self.people, self.weapons, self.places


people = ["Miss Scarlett", "Professor Plum", "Mrs. Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
places = ["kitchen", "ballroom", "conservatory", "dining room", "billiard room", "library", "lounge", "hall", "study"]
weapons = ["candlestick", "dagger", "lead pipe", "revolver", "rope", "wrench"]
normal_deck = deck(people, weapons, places)

people = ["Draco Malfoy", "Bellatrix Lestrange", "Dolores Umbridge", "Peter Pettigrew", "Crabbe & Goyle", "Grindelwald"]
places = ["Owlery", "Trophy room", "library", "DADA classroom", "Great Hall", "hospital wing", "Room of Requirements", "Potions classroom", "Divination classroom"]
weapons = ["Bat-Bogey hex", "Stupefy", "Petrificus totalus", "Cruciatus curse", "Killing curse", "Confundus charm"]
hp_deck = deck(people, weapons, places)

people = ["Vasechka #1", "Vasechka #2", "Vasechka #3", "Vasechka #4", "Vaseckha #5", "Vaseckha #6", "Vaseckha #7", "Vaseckha #8", "Vaseckha #9"]
places = ["SPBAU", "ITMO", "MSU", "HSE", "MIPT", "middle of nowhere"]
weapons = ["Dijkstra algorithm", "DFS", "big, big treap", "CENSORED", "suffix tree", "very big segment tree"]
vasechka_deck = deck(people, weapons, places)

decks = [normal_deck, hp_deck, vasechka_deck]
cluedo_people, cluedo_weapons, cluedo_places = rd.choice(decks).get()
print(rd.choice(decks).get())
