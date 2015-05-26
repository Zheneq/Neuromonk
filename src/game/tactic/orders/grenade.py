__author__ = 'dandelion'

from src.game.common.tile import Base, Order


class Grenade(object):
    def __init__(self, game):
        self.game = game

    def begin_grenade(self):
        targets = {}
        for cell in self.game.playground.cells:
            if cell.tile is self.game.player.hq and cell.tile.active:
                for neighbour in cell.neighbours:
                    if neighbour is not None and \
                            neighbour.tile is not None and \
                            neighbour.tile.hex.army_id != self.game.player.army and \
                            not isinstance(neighbour.tile.hex, Base):
                        targets[neighbour] = []
        if targets:
            self.game.clicker.pend_click(targets, self.grenade)
        else:
            if not self.game.player.hq.active:
                print '\t\tYour HQ is disabled by net. You can\'t use Grenade order.'
            else:
                print '\t\tThere is no enemy near your HQ. You can\'t use Grenade order.'
            cell = self.game.player.take_to_hand(Order(self.game.player.army, 'grenade'))
            self.game.action_types[cell] = []
            self.game.event(self.game.tactic)

    def grenade(self, (target, empty)):
        print '\t\t' + self.game.player.name, 'thrown grenade to the', str(self.game.playground.cells.index(target)), 'cell.'
        print '\t\t' + target.tile.name, 'is destroyed.'
        self.game.release_disable_units(target)
        target.tile = None
        self.game.event(self.game.tactic)
