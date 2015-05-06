from src.game.common.tile import DisposableModule, Unit, Module

__author__ = 'dandelion'

from src.game.gamemode import Neuroshima


def clown_explode(cell, damage_modificator):
    for neighbour in cell.neighbours:
        if neighbour is not None and neighbour.tile is not None:
            neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
    cell.tile.hp = 0


if __name__ == "__main__":
    game = Neuroshima(2)

    # moloch_medic4 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_hybrid1 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # moloch_hybrid2 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # moloch_greaver1 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # moloch_clown = clown = Unit(1, 2, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode)
    # moloch_mm = Module(1, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {})
    # borgo_mutant = Unit(2, 1, 'Mutant', [1,1,0,0,0,1], None, None, None, [[2, True]])
    # borgo_claws = Unit(2, 1, 'Claws', [1,1,0,0,0,0], None, None, None, [[3, True]])
    # hegeony_quartermaster = DisposableModule(3, 1, 'Quartermaster', {'convert': [1,1,1,1,1,1]}, {}, immovable=True)
    # hegeony_ganger1 = Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[3, True], [2, True]])
    # hegeony_ganger2 = Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[3, True], [2, True]])
    # moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
    # moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})
    #
    # game.playground.cells[0].tile = moloch_clown
    # game.playground.cells[0].turn = 0
    # game.playground.cells[1].tile = moloch_mm
    # game.playground.cells[1].turn = 3
    # game.playground.cells[4].tile = hegeony_ganger1
    # game.playground.cells[4].turn = 0
    # game.playground.cells[8].tile = moloch_fat1
    # game.playground.cells[8].turn = 4
    # game.playground.cells[3].tile = moloch_crip
    # game.playground.cells[3].turn = 4
    # game.playground.cells[12].tile = moloch_fat2
    # game.playground.cells[12].turn = 4
    # game.playground.cells[11].tile = borgo_mutant
    # game.playground.cells[11].turn = 4
    # game.playground.cells[0].tile = borgo_claws
    # game.playground.cells[0].turn = 2
    # game.playground.cells[5].tile = borgo_fighter5
    # game.playground.cells[5].turn = 1
    # game.playground.cells[6].tile = borgo_fighter6
    # game.playground.cells[6].turn = 1

    game.start_game()
