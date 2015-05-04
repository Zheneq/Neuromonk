__author__ = 'dandelion'


class March(object):
    def __init__(self, game):
        self.game = game

    def begin_march(self):
        maneuvers = {}
        for cell in self.game.playground.cells:
            if cell.tile is not None and cell.tile.active and cell.tile.army_id == self.game.player.army:
                maneuvers[cell] = cell.tile.maneuver_rate(cell)
        if maneuvers:
            self.game.clicker.pend_click(maneuvers, self.game.march)
        else:
            self.game.event(self.game.tactic)
