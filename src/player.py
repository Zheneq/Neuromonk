__author__ = 'dandelion'


class Player(object):
    def __init__(self, name, army_id, team_id):
        # self.name = name
        self.army = army_id
        self.team = team_id
        self.tiles = []
        self.hand = []

    def army_shuffle(self):
        #TODO load and shuffle army tiles from store
        pass