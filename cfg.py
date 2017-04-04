import random as rd #i am the best translator ever!


cluedo_open = [0, 0, 0, 6, 6, 3, 6] #[0, 0, 0, 0, 2, 3, 0]
cluedo_people = ["Miss Scarlett", "Professor Plum", "Mrs. Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
cluedo_weapons = ["Candlestick", "Dagger", "Lead pipe", "Revolver", "Rope", "Wrench"]
cluedo_places = ["Kitchen", "Ballroom", "Conservatory", "Dining room", "Billiard room", "Library", "Lounge", "Hall", "Study"]


class CluedoDeck:
	def __init__(self, ppl = [], wps = [], pls = []):
		self.people = ppl
		self.weapons = ["with a " + i for i in wps] #very bad!
		self.places = ["in the " + i for i in pls] #very very bad!

	def get(self):
		return self.people, self.weapons, self.places

def cluedo_init():
    global cluedo_people, cluedo_places, cluedo_weapons
    people = ["Miss Scarlett", "Professor Plum", "Mrs. Peacock", "Mr. Green", "Colonel Mustard", "Mrs. White"]
    places = ["Kitchen", "Ballroom", "Conservatory", "Dining room", "Billiard room", "Library", "Lounge", "Hall", "Study"]
    weapons = ["Candlestick", "Dagger", "Lead pipe", "Revolver", "Rope", "Wrench"]
    normal_deck = CluedoDeck(people, weapons, places)

    people = ["Draco Malfoy", "Bellatrix Lestrange", "Dolores Umbridge", "Peter Pettigrew", "Crabbe & Goyle", "Grindelwald"]
    places = ["Owlery", "Trophy room", "Library", "DADA classroom", "Great Hall", "Hospital wing", "Room of Requirements", "Potions classroom", "Divination classroom"]
    weapons = ["Sleeping draught", "Cursed necklace", "Petrificus totalus", "Crucio", "Avada Kedavra", "Vanishing cabinet"]
    hp_deck = CluedoDeck(people, weapons, places)

    people = ["Vasechka #1", "Vasechka #2", "Vasechka #3", "Vasechka #4", "Vaseckha #5", "Vaseckha #6", "Vaseckha #7", "Vaseckha #8", "Vaseckha #9"]
    places = ["209 classroom", "216 classroom", "Corridor", "St. Petersburg", "Kazan", "MSU"]
    weapons = ["Keyboard", "Mouse", "Big, big, birch", "Broken heart", "Dumb memes", "Very big birch"]
    vasechka_deck = CluedoDeck(people, weapons, places)

    decks = [normal_deck, hp_deck, vasechka_deck]
    cluedo_people, cluedo_weapons, cluedo_places = rd.choice(decks).get()
