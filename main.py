__author__ = 'dandelion'

# import statprof

from src.game.gamemode import Neuroshima
from src.game.battle.battle import Battle
from src.game.common.tile import *


if __name__ == "__main__":
    # statprof.start()
    try:
        def hand_init(game):
            game.buttons['confirm'].action = game.end_game
            game.turn_num = 0

            # Switch first player as Hegemony
            game.player = game.player.next

            game.player.hand[0].tile = TileOnBoard(Order(game.player.army, 'move'), 0)
            game.player.hand[1].tile = TileOnBoard(Unit(game.player.army, 1, 'Runner', [1,0,0,0,0,0], None, None, None, [[2, True]], mobility=1), 0)
            game.player.hand[2].tile = TileOnBoard(DisposableModule(game.player.army, 1, 'Transport', {'mobility': [1,1,1,1,1,1]}, {}, immovable=True), 0)

            game.playground.cells[5].tile = game.player.hq
            game.playground.cells[13].tile = game.player.next.hq

            # actions during the whole turn
            actions = []
            # action 1
            # move Runner to 6 cell with turn 1
            actions.append([game.playground.cells[17], game.playground.cells[6]])
            actions.append(1)
            # action 2
            # place Transport to 0 cell with turn 0
            actions.append([game.player.hand[2], game.playground.cells[0]])
            actions.append(0)
            # action 3
            # move Runner to 1 cell with turn 0
            actions.append([game.playground.cells[6], game.playground.cells[1]])
            actions.append(0)
            # try to move Runner to 9 cell
            actions.append([game.playground.cells[1], game.playground.cells[9]])
            # action 4
            # place Sprinter to 2 cell with turn 0
            actions.append([game.player.hand[1], game.playground.cells[2]])
            actions.append(0)
            # action 5
            # move Sprinter to 8 cell with turn 5
            actions.append([game.playground.cells[2], game.playground.cells[8]])
            actions.append(5)
            # action 6
            # move Sprinter to 7 cell with turn 4
            actions.append([game.playground.cells[8], game.playground.cells[7]])
            actions.append(4)
            # try to move Runner to 9 cell
            actions.append([game.playground.cells[7], game.playground.cells[9]])
            # action 7
            # apply Move order
            actions.append([game.player.hand[0], game.buttons['apply']])
            # action 8
            # try to move Transport to 4 cell
            actions.append([game.playground.cells[0], game.playground.cells[4]])
            # move HQ to 15 cell with turn 0
            actions.append([game.playground.cells[5], game.playground.cells[15]])
            actions.append(0)
            # finish turn
            actions.append([game.buttons['confirm']])

            game.clicker.test(actions)

            game.turn()

        game = Neuroshima(2)

        hegemony_run = TileOnBoard(Unit(3, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[2, True]], mobility=1), 1)

        game.playground.cells[17].tile = hegemony_run

        game.start_game(hand_init, [game], {})
        # game.start_game(game.place_all_hq, [], {})
    finally:
        # statprof.stop()
        # statprof.display()
        pass
