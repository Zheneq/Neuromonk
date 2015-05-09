from game.common.tile import DisposableModule, Unit, Medic

__author__ = 'dandelion'

# import statprof

from game.gamemode import Neuroshima


def clown_explode(cell, damage_modificator):
    for neighbour in cell.neighbours:
        if neighbour is not None and neighbour.tile is not None:
            neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
    cell.tile.hp = 0


if __name__ == "__main__":
    # statprof.start()
    try:
        game = Neuroshima(2)

        # moloch_medic = Medic(1, 1, 'Medic', [1,0,1,0,1,0])
        # moloch_hunterkiller = Unit(1, 1, 'Hunter-killer', [1,1,0,1,0,1], None, None, None, [[3, True]])
        # moloch_greaver1 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
        # moloch_clown = clown = Unit(1, 2, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode)
        # borgo_mutant = Unit(2, 1, 'Mutant', [1,1,0,0,0,1], None, None, None, [[2, True]])
        # borgo_claws = Unit(2, 1, 'Claws', [1,1,0,0,0,0], None, None, None, [[3, True]])
        # hegemony_quartermaster = DisposableModule(3, 1, 'Quartermaster', {'convert': [1,0,0,0,0,0]}, {}, immovable=True)
        # hegemony_ganger = Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[3, True]])
        # moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
        # moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})
        #
        # game.playground.cells[0].tile = moloch_clown
        # game.playground.cells[0].turn = 0
        # game.playground.cells[1].tile = moloch_mm
        # game.playground.cells[1].turn = 3
        # game.playground.cells[4].tile = moloch_hunterkiller
        # game.playground.cells[4].turn = 5
        # game.playground.cells[8].tile = moloch_fat1
        # game.playground.cells[8].turn = 4
        # game.playground.cells[3].tile = moloch_medic
        # game.playground.cells[3].turn = 4
        # game.playground.cells[12].tile = moloch_fat2
        # game.playground.cells[12].turn = 4
        # game.playground.cells[11].tile = borgo_mutant
        # game.playground.cells[11].turn = 4
        # game.playground.cells[0].tile = borgo_claws
        # game.playground.cells[0].turn = 2
        # game.playground.cells[5].tile = borgo_fighter5
        # game.playground.cells[5].turn = 1
        # game.playground.cells[15].tile = hegemony_ganger
        # game.playground.cells[15].turn = 1
        # game.playground.cells[16].tile = hegemony_quartermaster
        # game.playground.cells[16].turn = 2

        game.start_game()
    finally:
        # statprof.stop()
        # statprof.display()
        pass
