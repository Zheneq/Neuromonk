__author__ = 'dandelion'

# import statprof

from src.game.gamemode import Neuroshima
from src.game.battle.battle import Battle
from src.game.common.tile import *


if __name__ == "__main__":
    # statprof.start()
    try:
        def clown_explode(cell, damage_modificator):
            for neighbour in cell.neighbours:
                if neighbour is not None and neighbour.tile is not None:
                    neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
            cell.tile.hex.hp = 0

        game = Neuroshima(2)

        moloch_hq = TileOnBoard(Base(1, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {}), 0)
        moloch_clown1 = TileOnBoard(Unit(1, 3, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode), 5)
        moloch_clown2 = TileOnBoard(Unit(1, 3, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode), 0)
        moloch_mm = TileOnBoard(Module(1, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {}), 5)

        hegemony_meat = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_med1 = TileOnBoard(Medic(3, 1, 'Medic', [1,0,1,0,1,0]), 1)
        hegemony_med2 = TileOnBoard(Medic(3, 1, 'Medic', [1,0,1,0,1,0]), 0)
        hegemony_qm = TileOnBoard(DisposableModule(3, 1, 'Quartermaster', {'convert': [1,1,1,1,1,1]}, {}), 0)
        hegemony_universal = TileOnBoard(Unit(3, 1, 'Universal soldier', [1,0,0,0,0,0], [1,0,0,0,0,0], None, None, [[2, True], [1, True]]), 3)
        hegemony_archer = TileOnBoard(Unit(3, 2, 'Universal soldier', None, [1,0,0,0,0,0], None, None, [[1, True]]), 3)
        hegemony_hq = TileOnBoard(Base(3, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'melee': [1,1,1,1,1,1]}, {}), 0)

        game.playground.cells[13].tile = moloch_hq
        game.playground.cells[4].tile = moloch_clown1
        game.playground.cells[16].tile = moloch_clown2
        game.playground.cells[15].tile = moloch_mm

        game.playground.cells[5].tile = hegemony_hq
        game.playground.cells[17].tile = hegemony_meat
        game.playground.cells[18].tile = hegemony_med1
        game.playground.cells[9].tile = hegemony_med2
        game.playground.cells[2].tile = hegemony_qm
        game.playground.cells[0].tile = hegemony_archer
        game.playground.cells[8].tile = hegemony_universal

        game.start_game(game.begin_battle, [], {'continuer': game.end_game, 'period': 1})
        # game.start_game(game.place_all_hq, [], {})
    finally:
        # statprof.stop()
        # statprof.display()
        pass
