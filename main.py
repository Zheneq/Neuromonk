__author__ = 'dandelion'

# import statprof

from src.game.gamemode import Neuroshima
from src.game.common.tile import DisposableModule, Unit, Medic


def clown_explode(cell, damage_modificator):
    for neighbour in cell.neighbours:
        if neighbour is not None and neighbour.tile is not None:
            neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
    cell.tile.hp = 0


if __name__ == "__main__":
    # statprof.start()
    try:
        game = Neuroshima(2)
        game.start_game()
    finally:
        # statprof.stop()
        # statprof.display()
        pass
