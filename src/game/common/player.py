__author__ = 'dandelion'

import random

from game.common.armies import *
from game.common.grid import Cell


class Player(object):
    def __init__(self, name, army_id, team_id, game):
        self.name = name
        self.remove_in_turn = False
        self.army = army_id
        self.team = team_id
        self.next = None
        if self.army in armies:
            self.army_dict = armies[self.army]()
            self.tiles = self.army_dict.army.values()
        else:
            self.tiles = []
        self.hq = self.army_dict.hq
        self.hand = []
        for ind in xrange(3):
            self.hand.append(Cell(game))
            self.hand[ind].x = (ind - 1) * 1.05
            self.hand[ind].y = 0

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

    def refresh_hand(self):
        self.hand[0].tile = None
        self.hand[1].tile = None
        self.hand[2].tile = None
        self.get_tiles(3)

    def remove_from_hand(self, tile):
        for cell in self.hand:
            if cell.tile is tile:
                cell.tile = None
                break

    def take_to_hand(self, tile):
        for cell in self.hand:
            if cell.tile is None:
                cell.tile = tile
                return cell


    def get_tiles(self, turn):
        turn = min(3, turn)
        num_tiles_to_get = min(turn - self.tiles_in_hand(), len(self.tiles))
        self.hand.sort(key=lambda x: x.tile)
        for ind in xrange(num_tiles_to_get):
            self.hand[ind].tile = self.tiles.pop()


if __name__ == '__main__':
    print 'Yay!'