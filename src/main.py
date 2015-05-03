__author__ = 'dandelion'

from src.game.gamemode import Neuroshima


if __name__ == "__main__":
    game = Neuroshima(2)

    # # moloch_medic1 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # # moloch_medic2 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # # moloch_medic3 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # # moloch_medic4 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_hybrid1 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # moloch_hybrid2 = Unit(1, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
    # # moloch_greaver1 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # # moloch_greaver2 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # borgo_mutant = Unit(2, 1, 'Mutant', [1,1,0,0,0,1], None, None, None, [[2, True]])
    # borgo_claws = Unit(2, 1, 'Claws', [1,1,0,0,0,0], None, None, None, [[3, True]])
    # # borgo_fighter2 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # # borgo_fighter3 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # # borgo_fighter4 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # # borgo_fighter5 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # # borgo_fighter6 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # # moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
    # # moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})
    # #
    # game.playground.cells[12].tile = moloch_hybrid1
    # game.playground.cells[12].turn = 5
    # game.playground.cells[14].tile = moloch_hybrid2
    # game.playground.cells[14].turn = 0
    # game.playground.cells[11].tile = borgo_mutant
    # game.playground.cells[11].turn = 4
    # game.playground.cells[0].tile = borgo_claws
    # game.playground.cells[0].turn = 2
    # # game.playground.cells[5].tile = borgo_fighter5
    # # game.playground.cells[5].turn = 1
    # # game.playground.cells[6].tile = borgo_fighter6
    # # game.playground.cells[6].turn = 1

    game.start_game()
