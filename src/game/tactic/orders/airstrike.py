__author__ = 'dandelion'

from src.game.common.tile import Base

from src.game.battle.battle import Battle


class AirStrike(object):
    def __init__(self, game):
        self.game = game

    def begin_airstrike(self):
        targets = {}
        for cell in self.game.playground.cells:
            if None not in cell.neighbours:
                targets[cell] = []
        self.game.clicker.pend_click(targets, self.airstrike)

    def airstrike(self, (target, empty)):
        base_cell = None
        print '\t\t' + self.game.player.name, 'strikes to the', str(self.game.playground.cells.index(target)), 'cell.'
        for cell in self.game.playground.cells:
            if cell.tile is not None and cell.tile.hex.army_id == self.game.player.army and isinstance(cell.tile.hex, Base):
                base_cell = cell
                break
        if target.tile is not None and not isinstance(target.tile.hex, Base):
            target.tile.taken_damage.append({'value': 1, 'type': 'pure', 'instigator': base_cell})
        for cell in target.neighbours:
            if cell.tile is not None and not isinstance(cell.tile.hex, Base):
                cell.tile.taken_damage.append({'value': 1, 'type': 'pure', 'instigator': base_cell})
        battle = Battle(self.game.playground,
                        self.game.clicker.pend_click,
                        self.game.buttons,
                        self.game.release_disable_units,
                        self.game.event,
                        self.game.set_timer,
                        2000,
                        self.game.renderer,
                        self.game.tactic,
                        init_phase=0)
        self.game.set_timer(2000, battle.take_damage_phase)
