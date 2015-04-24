__author__ = 'dandelion'

from grid import Grid
from tile import *
from renderer import Renderer

from game.battle.buffs import compute_initiative
from game.battle.battle import give_damage_phase, take_damage_phase, refresh_units


class GameMode(object):
    def __init__(self, grid_radius):
        self.playground = Grid(grid_radius)
        self.renderer = Renderer(None)
        self.players = []

    def battle(self):
        # prepare to battle
        # find max initiative
        max_initiative = 0
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) == Unit:
                # reset initiative
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    cell.tile.initiative[initiative_ind][1] = True
                # find max initiative
                initiative_modificator = compute_initiative(cell)
                if cell.tile.initiative[0][0] + initiative_modificator > max_initiative:
                    max_initiative = cell.tile.initiative[0][0] + initiative_modificator
        # battle
        for phase in range(max_initiative, -1, -1):
            # phase of giving damage
            give_damage_phase(self.playground, phase)
            # phase of taking damage and cleaning corpses
            take_damage_phase(self.playground)
        # refresh support info
        refresh_units(self.playground)


if __name__ == "__main__":
    battle = GameMode(2)

    outpost_kicker1 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[3, True]])
    outpost_kicker1.active = False
    outpost_kicker2 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    outpost_scout = Module(0, 1, {'initiative': [1,1,0,0,0,1]}, {})
    outpost_mothermodule = Module(0, 1, {'add_attacks': [2,0,0,0,0,0]}, {})
    moloch_fat = Unit(1, 5, None, None, None, None, [[0, True]])
    moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])

    # outpost_medic1 = Medic(0, 1, [1,1,0,0,0,1])
    # outpost_medic2 = Medic(0, 1, [0,1,0,0,0,1])
    # outpost_medic3 = Medic(0, 1, [0,0,0,1,0,0])
    # outpost_medic4 = Medic(0, 1, [1,1,0,0,0,1])
    # moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])


    battle.playground.cells[0].tile = outpost_kicker1
    battle.playground.cells[0].turn = 1
    battle.playground.cells[1].tile = moloch_netfighter
    battle.playground.cells[1].turn = 3
    battle.playground.cells[2].tile = moloch_fat
    battle.playground.cells[2].turn = 0
    battle.playground.cells[3].tile = moloch_greaver
    battle.playground.cells[3].turn = 4
    battle.playground.cells[4].tile = outpost_scout
    battle.playground.cells[4].turn = 0
    battle.playground.cells[5].tile = outpost_mothermodule
    battle.playground.cells[5].turn = 1
    battle.playground.cells[6].tile = outpost_kicker2
    battle.playground.cells[6].turn = 1

    battle.renderer.render_board(battle.playground)

    battle.battle()

    battle.renderer.render_board(battle.playground)

    print "Yay!"
