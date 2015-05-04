__author__ = 'dandelion'


class PushBack(object):
    def __init__(self, game):
        self.game = game

    def begin_pushback(self):
        pushes = {}
        for cell in self.game.playground.cells:
            if cell.tile is not None and cell.tile.active and cell.tile.army_id == self.game.player.army:
                # if there is unit to push back we add cell in actions dictionary
                enemies = []
                for ind in xrange(len(cell.neighbours)):
                    neighbour = cell.neighbours[ind]
                    if neighbour is not None and \
                                    neighbour.tile is not None and \
                            neighbour.tile.active and \
                                    neighbour.tile.army_id != self.game.player.army:
                        # neighbour is enemy tile
                        for retreat_ind in xrange(ind + 5, ind + 8):
                            if neighbour.neighbours[retreat_ind % 6] is not None and \
                                            neighbour.neighbours[retreat_ind % 6].tile is None:
                                # neighbour tile can retreat here
                                enemies.append(neighbour)
                                break
                if enemies:
                    pushes[cell] = enemies
        if pushes:
            self.game.clicker.pend_click(pushes, self.pushback)
        else:
            self.game.event(self.game.tactic)

    def pushback(self, (who, whom)):
        retreat_ways = []
        ind = who.neighbours.index(whom)
        for retreat_ind in xrange(ind + 5, ind + 8):
            if whom.neighbours[retreat_ind % 6] is not None and \
                            whom.neighbours[retreat_ind % 6].tile is None:
                # whom tile can retreat here
                retreat_ways.append(whom.neighbours[retreat_ind % 6])
        if len(retreat_ways) > 1:
            possible_retreats = {whom: retreat_ways}
            self.game.clicker.pend_click(possible_retreats, self.retreat)
        else:
            self.retreat((whom, retreat_ways[0]))

    def retreat(self, (who, where)):
        self.game.swap((who, where))
        self.game.event(self.game.tactic)

