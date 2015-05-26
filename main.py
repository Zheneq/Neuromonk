__author__ = 'dandelion'

# import statprof

from src.game.gamemode import Neuroshima
from src.game.battle.battle import Battle
from src.game.common.tile import *


def clown_explode(cell, damage_modificator):
    for neighbour in cell.neighbours:
        if neighbour is not None and neighbour.tile is not None:
            neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
    cell.tile.hp = 0


if __name__ == "__main__":
    # statprof.start()
    try:
        game = Neuroshima(2)

        moloch_hq = TileOnBoard(Base(1, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {}), 0)
        moloch_hunt_kil = TileOnBoard(Unit(1, 1, 'Hunter-killer', [1,1,0,1,0,1], None, None, None, [[3, True]]), 5)
        moloch_mm = TileOnBoard(Module(1, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {}), 4)

        hegemony_netmaster = TileOnBoard(Unit(3, 1, 'Netmaser', [1,0,0,0,0,0], None, None, [0,1,0,0,0,1], [[2, True]]), 0)
        hegemony_hq = TileOnBoard(Base(3, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'melee': [1,1,1,1,1,1]}, {}), 0)

        game.playground.cells[13].tile = moloch_hq
        game.playground.cells[4].tile = moloch_hunt_kil
        game.playground.cells[3].tile = moloch_mm

        game.playground.cells[5].tile = hegemony_hq
        game.playground.cells[14].tile = hegemony_netmaster
        game.disable_units(game.playground.cells[14])

        game.start_game(game.begin_battle, [], {'continuer': game.place_all_hq, 'period': 1})
        # game.start_game(game.place_all_hq)
    finally:
        # statprof.stop()
        # statprof.display()
        pass
