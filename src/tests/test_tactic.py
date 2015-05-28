__author__ = 'dandelion'

from src.game.gamemode import Neuroshima
from src.game.common.tile import *


class TestTactic(object):
    def test_turn(self):
        def hand_init(game):
            game.buttons['confirm'].action = game.end_game
            game.turn_num = 3

            game.player.hand[0].tile = TileOnBoard(Unit(game.player.army, 1, 'Netfighter', None, None, None, [1,1,0,0,0,0], None), 0)
            game.player.hand[1].tile = TileOnBoard(Order(game.player.army, 'pushback'), 0)
            game.player.hand[2].tile = TileOnBoard(Unit(game.player.army, 3, 'Blocker', None, None, [1,0,0,0,0,0], None, None), 0)

            # actions during the whole turn
            actions = []
            # action 1
            # place netmaster on 4 cell with turn 5 to catch enemy base
            actions.append([game.player.hand[0], game.playground.cells[4]])
            actions.append(5)
            # action 2
            # apply pushback
            actions.append([game.player.hand[1], game.buttons['apply']])
            # push back enemy Meat1 from Meat to netmaster
            actions.append([game.playground.cells[7], game.playground.cells[1]])
            # action 3
            # try to confirm, then remove blocker from hand
            actions.append([game.buttons['confirm'], game.player.hand[2], game.buttons['remove']])
            # retry confirm
            actions.append([game.buttons['confirm']])

            game.clicker.test(actions)

            game.turn()

        self.game = Neuroshima(2)

        moloch_hq = TileOnBoard(Base(1, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {}), 0)
        moloch_meat = TileOnBoard(Unit(1, 2, 'Blocker', None, None, [1,0,0,0,0,0], None, None), 3)

        hegemony_meat1 = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat2 = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat3 = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_hq = TileOnBoard(Base(3, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'melee': [1,1,1,1,1,1]}, {}), 0)

        self.game.playground.cells[13].tile = moloch_hq
        self.game.playground.cells[7].tile = moloch_meat

        self.game.playground.cells[5].tile = hegemony_hq
        self.game.playground.cells[1].tile = hegemony_meat1
        self.game.playground.cells[2].tile = hegemony_meat2
        self.game.playground.cells[6].tile = hegemony_meat3

        self.game.start_game(hand_init, [self.game], {}, test_actions='blank')

        # check state

        # Moloch Meat
        assert self.game.playground.cells[7].tile.active
        # Moloch Net Fighter
        assert self.game.playground.cells[4].tile.active
        assert self.game.playground.cells[4].tile.turn == 5
        # Hegemony Meat 1
        assert not self.game.playground.cells[1].tile
        assert not self.game.playground.cells[0].tile.active
        assert self.game.playground.cells[0].tile.turn == 0
        # Hegemony Meat 2
        assert self.game.playground.cells[2].tile.active
        assert self.game.playground.cells[2].tile.turn == 0
        # Hegemony Meat 3
        assert self.game.playground.cells[6].tile.active
        assert self.game.playground.cells[6].tile.turn == 0
        # Hegemony HQ
        assert not self.game.playground.cells[5].tile.active
        # Moloch HQ
        assert self.game.playground.cells[13].tile.active
