__author__ = 'dandelion'

# import statprof

from src.game.gamemode import Neuroshima
from src.game.battle.battle import Battle
from src.game.common.tile import *


if __name__ == "__main__":
    # statprof.start()
    try:
        game = Neuroshima(2)

        game.playground.cells[0].tile = TileOnBoard(DisposableModule(3, 1, 'Transport', {'mobility': [1,1,1,1,1,1]}, {}), 0)

        game.start_game(game.place_all_hq, [], {})
    finally:
        # statprof.stop()
        # statprof.display()
        pass
