__author__ = 'dandelion'

import random

from armies import *


class Player(object):
    def __init__(self, name, army_id, team_id):
        # self.name = name
        self.army = army_id
        self.team = team_id
        if self.army in armies:
            self.army_dict = armies[self.army]()
            self.tiles = self.army_dict.army.values()
        else:
            self.tiles = []
        self.hand = []

    def army_shuffle(self):
        """
        Performs Fisher-Yates shuffle of tiles.
        :return: nothing is returned.
        """
        for first in xrange(len(self.tiles)):
            second = random.randint(0, first)
            self.tiles[first], self.tiles[second] = self.tiles[second], self.tiles[first]

    def get_tiles(self, turn):
        turn = min(3, turn)
        num_tiles_to_get = min(turn - len(self.hand), len(self.tiles))
        for ind in xrange(num_tiles_to_get):
            self.hand.append(self.tiles.pop())


if __name__ == '__main__':
    Zq = Player('Zq', 1, 0)
    Zq.army_shuffle()
    print 'Yay!'