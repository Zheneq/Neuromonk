__author__ = 'dandelion'

from src.game.battle.battle import Battle

from src.game.common.tile import Base, Order


class Sniper(object):
    def __init__(self, game):
        self.game = game

    def begin_sniper(self):
        targets = {}
        for cell in self.game.playground.cells:
            if cell.tile is not None and cell.tile.army_id != self.game.player.army and not isinstance(cell.tile, Base):
                        targets[cell] = []
        if targets:
            self.game.clicker.pend_click(targets, self.sniper)
        else:
            print 'There is no enemy on the battlefield. You can\'t use Sniper order.'
            cell = self.game.player.take_to_hand(Order(self.game.player.army, 'sniper'))
            self.game.action_types[cell] = []
            self.game.event(self.game.tactic)

    def sniper(self, (target, empty)):
        base_cell = None
        for cell in self.game.playground.cells:
            if cell.tile is not None and cell.tile.army_id == self.game.player.army and isinstance(cell.tile, Base):
                base_cell = cell
                break
        target.tile.taken_damage.append({'value': 1, 'type': 'pure', 'instigator': base_cell})
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