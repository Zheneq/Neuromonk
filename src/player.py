__author__ = 'dandelion'

import random

from armies import *
from grid import Cell


class Player(object):
    def __init__(self, name, army_id, team_id, game):
        self.name = name
        self.next = None
        self.remove_in_turn = False
        self.army = army_id
        self.team = team_id
        if self.army in armies:
            self.army_dict = armies[self.army]()
            self.tiles = self.army_dict.army.values()
        else:
            self.tiles = []
        self.hand = []
        for ind in xrange(3):
            cell = Cell(game)
            self.hand.append(cell)
            # DEBUG
            game.actors.remove(cell)

    def army_shuffle(self):
        """
        Performs Fisher-Yates shuffle of tiles.
        :return: nothing is returned.
        """
        for first in xrange(len(self.tiles)):
            second = random.randint(0, first)
            self.tiles[first], self.tiles[second] = self.tiles[second], self.tiles[first]

    def tiles_in_hand(self):
        return len(self.get_hand())

    def get_hand(self):
        return filter(lambda x: x.tile, self.hand)

    def remove_from_hand(self, tile):
        for cell in self.hand:
            if cell.tile is tile:
                cell.tile = None
                break
        self.remove_in_turn = True

    def get_tiles(self, turn):
        turn = min(3, turn)
        num_tiles_to_get = min(turn - self.tiles_in_hand(), len(self.tiles))
        self.hand.sort(key=lambda x: x.tile)
        for ind in xrange(num_tiles_to_get):
            self.hand[ind].tile = self.tiles.pop()


if __name__ == '__main__':
    print 'Yay!'