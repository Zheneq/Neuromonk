__author__ = 'dandelion'

from src.game.gamemode import Neuroshima
from src.game.common.tile import *


class TestOrders(object):
    def test_net_pushback(self):
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

    def test_attack_orders(self):
        def hand_init(game):
            game.buttons['confirm'].action = game.end_game
            game.turn_num = 0

            game.player.hand[0].tile = TileOnBoard(Order(game.player.army, 'airstrike'), 0)
            game.player.hand[1].tile = TileOnBoard(Order(game.player.army, 'grenade'), 0)
            game.player.hand[2].tile = TileOnBoard(Order(game.player.army, 'sniper'), 0)

            game.playground.cells[13].tile = game.player.hq
            game.playground.cells[5].tile = game.player.next.hq

            # actions during the whole turn
            actions = []
            # action 1
            # apply airstrike order
            actions.append([game.player.hand[0], game.buttons['apply']])
            # airstrike at 0 cell
            actions.append([game.playground.cells[0]])
            # action 2
            # apply grenade order
            actions.append([game.player.hand[1], game.buttons['apply']])
            # throw grenade to 12 cell
            actions.append([game.playground.cells[12]])
            # action 3
            # apply sniper order
            actions.append([game.player.hand[2], game.buttons['apply']])
            # there is no enemies on the board - return Sniper to hand
            # finish turn
            actions.append([game.buttons['confirm']])

            game.clicker.test(actions)

            game.turn()

        self.game = Neuroshima(2)

        moloch_meat = TileOnBoard(Unit(1, 2, 'Blocker', None, None, [1,0,0,0,0,0], None, None), 3)

        hegemony_meat1 = TileOnBoard(Unit(3, 1, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat2 = TileOnBoard(Unit(3, 1, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat3 = TileOnBoard(Unit(3, 1, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat4 = TileOnBoard(Unit(3, 1, 'Gladiator', None, None, None, None, None), 0)
        hegemony_meat5 = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)

        self.game.playground.cells[4].tile = moloch_meat

        self.game.playground.cells[0].tile = hegemony_meat1
        self.game.playground.cells[1].tile = hegemony_meat2
        self.game.playground.cells[2].tile = hegemony_meat3
        self.game.playground.cells[6].tile = hegemony_meat4
        self.game.playground.cells[12].tile = hegemony_meat5

        self.game.start_game(hand_init, [self.game], {}, test_actions='blank')

        # check state

        # Moloch Meat
        assert self.game.playground.cells[4].tile.injuries == 1
        # Hegemony Meat 1
        assert not self.game.playground.cells[1].tile
        # Hegemony Meat 2
        assert not self.game.playground.cells[2].tile
        # Hegemony Meat 3
        assert not self.game.playground.cells[6].tile
        # Hegemony Meat 4
        assert not self.game.playground.cells[7].tile
        # Hegemony Meat 5
        assert not self.game.playground.cells[12].tile
        # Player1 Sniper Order
        assert self.game.player.hand[0].tile.hex.name == 'sniper'
        # Hegemony HQ
        assert self.game.playground.cells[5].tile.injuries == 0
        # Moloch HQ
        assert self.game.playground.cells[13].tile.injuries == 0

    def test_ext_attack_orders(self):
        def hand_init(game):
            game.buttons['confirm'].action = game.end_game
            game.turn_num = 0

            game.player.hand[0].tile = TileOnBoard(Order(game.player.army, 'grenade'), 0)
            game.player.hand[1].tile = TileOnBoard(Order(game.player.army, 'pushback'), 0)
            game.player.hand[2].tile = TileOnBoard(Order(game.player.army, 'sniper'), 0)

            game.playground.cells[13].tile = game.player.hq
            game.playground.cells[5].tile = game.player.next.hq

            # actions during the whole turn
            actions = []
            # action 1
            # apply Grenade order
            actions.append([game.player.hand[0], game.buttons['apply']])
            # HQ is under the net - return Grenade to hand
            # action 2
            # apply Sniper order
            actions.append([game.player.hand[2], game.buttons['apply']])
            # attack 7 cell
            actions.append([game.playground.cells[14]])
            # action 3
            # apply Grenade order
            actions.append([game.player.hand[0], game.buttons['apply']])
            # There is no enemies near HQ - return Grenade to hand
            # action 4
            # apply Pushback order
            actions.append([game.player.hand[1], game.buttons['apply']])
            # push enemy Meat back by Meat
            actions.append([game.playground.cells[10], game.playground.cells[11]])
            # enemy Meat retreat to 12 cell
            actions.append([game.playground.cells[11], game.playground.cells[12]])
            # action 5
            # apply Grenade order
            actions.append([game.player.hand[0], game.buttons['apply']])
            # throw grenade to 12 cell
            actions.append([game.playground.cells[12]])
            # finish turn
            actions.append([game.buttons['confirm']])

            game.clicker.test(actions)

            game.turn()

        self.game = Neuroshima(2)

        moloch_meat = TileOnBoard(Unit(1, 2, 'Blocker', None, None, [1,0,0,0,0,0], None, None), 3)

        hegemony_meat = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_net = TileOnBoard(Unit(3, 1, 'Netfighter', None, None, None, [1,0,0,0,0,0], None), 1)

        self.game.playground.cells[10].tile = moloch_meat

        self.game.playground.cells[11].tile = hegemony_meat
        self.game.playground.cells[14].tile = hegemony_net

        self.game.start_game(hand_init, [self.game], {}, test_actions='blank')

        # check state

        # Moloch Meat
        assert self.game.playground.cells[10].tile.injuries == 0
        # Hegemony Meat old place
        assert not self.game.playground.cells[11].tile
        # Hegemony Meat new place
        assert not self.game.playground.cells[12].tile
        # Hegemony Net Fighter
        assert not self.game.playground.cells[14].tile
        # There is no Grenade in Player1 hand
        assert not self.game.player.hand[0].tile
        # Hegemony HQ
        assert self.game.playground.cells[5].tile.injuries == 0
        # Moloch HQ
        assert self.game.playground.cells[13].tile.injuries == 0

    def test_maneuvers(self):
        def hand_init(game):
            game.buttons['confirm'].action = game.end_game
            game.turn_num = 0

            # Switch first player as Hegemony
            game.player = game.player.next

            game.player.hand[0].tile = TileOnBoard(Order(game.player.army, 'move'), 0)
            game.player.hand[1].tile = TileOnBoard(Unit(game.player.army, 1, 'Ganger', [1,0,0,0,0,0], None, None, None, [[2, True]], mobility=1), 0)
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
            # action 4
            # try to move Runner to 9 cell
            # place Sprinter to 2 cell with turn 0
            actions.append([game.playground.cells[1], game.playground.cells[9], game.player.hand[1], game.playground.cells[2]])
            actions.append(0)
            # action 5
            # move Sprinter to 8 cell with turn 5
            actions.append([game.playground.cells[2], game.playground.cells[8]])
            actions.append(5)
            # action 6
            # move Sprinter to 7 cell with turn 4
            actions.append([game.playground.cells[8], game.playground.cells[7]])
            actions.append(4)
            # action 7
            # try to move Runner to 9 cell
            # apply Move order
            actions.append([game.playground.cells[7], game.playground.cells[9], game.player.hand[0], game.buttons['apply']])
            # action 8
            # try to move Transport to 4 cell
            # move HQ to 15 cell with turn 0
            actions.append([game.playground.cells[0], game.playground.cells[4], game.playground.cells[5], game.playground.cells[15]])
            actions.append(0)
            # finish turn
            actions.append([game.buttons['confirm']])

            game.clicker.test(actions)

            game.turn()

        self.game = Neuroshima(2)

        hegemony_run = TileOnBoard(Unit(3, 1, 'Runner', [1,0,0,0,0,0], None, None, None, [[2, True]], mobility=1), 1)

        self.game.playground.cells[17].tile = hegemony_run

        self.game.start_game(hand_init, [self.game], {}, test_actions='blank')

        # check state

        # Hegemony Runner
        assert self.game.playground.cells[1].tile.turn == 0
        # Hegemony Sprinter
        assert self.game.playground.cells[7].tile.turn == 4
        # Hegemony Transport
        assert self.game.playground.cells[0].tile.turn == 0
        # Hegemony HQ
        assert self.game.playground.cells[15].tile.injuries == 0
        # Moloch HQ
        assert self.game.playground.cells[13].tile.injuries == 0
