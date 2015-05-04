from src.game.common.tile import DisposableModule, Unit

__author__ = 'dandelion'

from src.game.gamemode import Neuroshima


if __name__ == "__main__":
    game = Neuroshima(2)

    # # moloch_medic4 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_hybrid1 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # moloch_hybrid2 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # # moloch_greaver1 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # moloch_fat1 = Unit(1, 3, 'Fat 1', None, None, None, None, None)
    # moloch_crip = Unit(1, 1, 'Crip', None, None, None, None, None)
    # moloch_fat2 = Unit(1, 3, 'Fat 2', None, None, None, None, None)
    # # borgo_mutant = Unit(2, 1, 'Mutant', [1,1,0,0,0,1], None, None, None, [[2, True]])
    # # borgo_claws = Unit(2, 1, 'Claws', [1,1,0,0,0,0], None, None, None, [[3, True]])
    # hegeony_quartermaster = DisposableModule(3, 1, 'Quartermaster', {'convert': [1,1,1,1,1,1]}, {}, immovable=True)
    # hegeony_ganger1 = Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[3, True], [2, True]])
    # hegeony_ganger2 = Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[3, True], [2, True]])
    # # # moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
    # # # moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})
    # # #
    # game.playground.cells[5].tile = hegeony_quartermaster
    # game.playground.cells[5].turn = 0
    # game.playground.cells[6].tile = hegeony_ganger1
    # game.playground.cells[6].turn = 1
    # game.playground.cells[0].tile = hegeony_ganger2
    # game.playground.cells[0].turn = 2
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
    # # game.playground.cells[5].tile = borgo_fighter5
    # # game.playground.cells[5].turn = 1
    # # game.playground.cells[6].tile = borgo_fighter6
    # # game.playground.cells[6].turn = 1

    game.start_game()
