__author__ = 'dandelion'

from src.game.gamemode import Neuroshima
from src.game.common.tile import *


class TestBattle(object):
    def test_simple_battle(self):
        self.game = Neuroshima(2)

        moloch_hq = TileOnBoard(Base(1, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {}), 0)
        moloch_hunt_kil = TileOnBoard(Unit(1, 1, 'Hunter-killer', [1,1,0,1,0,1], None, None, None, [[3, True]]), 5)
        moloch_mm = TileOnBoard(Module(1, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {}), 4)

        hegemony_netmaster = TileOnBoard(Unit(3, 1, 'Netmaser', [1,0,0,0,0,0], None, None, [0,1,0,0,0,1], [[2, True]]), 0)
        hegemony_hq = TileOnBoard(Base(3, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'melee': [1,1,1,1,1,1]}, {}), 0)

        self.game.playground.cells[13].tile = moloch_hq
        self.game.playground.cells[4].tile = moloch_hunt_kil
        self.game.playground.cells[3].tile = moloch_mm

        self.game.playground.cells[5].tile = hegemony_hq
        self.game.playground.cells[14].tile = hegemony_netmaster
        self.game.disable_units(self.game.playground.cells[14])

        self.game.start_game(self.game.begin_battle, [], {'continuer': self.game.end_game, 'period': 1})

        # check state

        # Moloch hunter-killer
        assert self.game.playground.cells[4].tile is None
        # Moloch mother module
        assert self.game.playground.cells[3].tile.active
        assert self.game.playground.cells[3].tile.injuries == 0
        # Hegemony net master
        assert self.game.playground.cells[14].tile.active
        assert self.game.playground.cells[14].tile.injuries == 0
        # Hegemony HQ
        assert self.game.playground.cells[5].tile.active
        assert self.game.playground.cells[5].tile.injuries == 2
        # Moloch HQ
        assert not self.game.playground.cells[13].tile.active
        assert self.game.playground.cells[13].tile.injuries == 0

    def test_interaction(self):
        def clown_explode(cell, damage_modificator):
            for neighbour in cell.neighbours:
                if neighbour is not None and neighbour.tile is not None:
                    neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
            cell.tile.hex.hp = 0

        self.game = Neuroshima(2)

        moloch_hq = TileOnBoard(Base(1, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {}), 0)
        moloch_clown1 = TileOnBoard(Unit(1, 3, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode), 5)
        moloch_clown2 = TileOnBoard(Unit(1, 3, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=clown_explode), 0)
        moloch_mm = TileOnBoard(Module(1, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {}), 5)
        moloch_meat = TileOnBoard(Unit(1, 2, 'Blocker', None, None, None, None, None), 0)

        hegemony_meat = TileOnBoard(Unit(3, 2, 'Gladiator', None, None, None, None, None), 0)
        hegemony_med1 = TileOnBoard(Medic(3, 1, 'Medic', [1,0,1,0,1,0]), 1)
        hegemony_med2 = TileOnBoard(Medic(3, 1, 'Medic', [1,0,1,0,1,0]), 0)
        hegemony_qm1 = TileOnBoard(DisposableModule(3, 1, 'Quartermaster', {'convert': [1,1,1,1,1,1]}, {}), 0)
        hegemony_qm2 = TileOnBoard(DisposableModule(3, 1, 'Quartermaster', {'convert': [1,1,1,1,1,1]}, {}), 0)
        hegemony_universal1 = TileOnBoard(Unit(3, 1, 'Universal soldier', [1,0,0,0,0,0], [1,0,0,0,0,0], None, None, [[2, True], [1, True]]), 3)
        hegemony_universal2 = TileOnBoard(Unit(3, 1, 'Universal soldier', [1,1,0,0,0,0], None, None, None, [[2, True], [1, True]]), 4)
        hegemony_archer = TileOnBoard(Unit(3, 2, 'Universal soldier', None, [1,0,0,0,0,0], None, None, [[1, True]]), 3)
        hegemony_hq = TileOnBoard(Base(3, 20, 'HQ', [1,1,1,1,1,1], [[0, True]], {'melee': [1,1,1,1,1,1]}, {}), 0)

        self.game.playground.cells[13].tile = moloch_hq
        self.game.playground.cells[4].tile = moloch_clown1
        self.game.playground.cells[16].tile = moloch_clown2
        self.game.playground.cells[15].tile = moloch_mm
        self.game.playground.cells[1].tile = moloch_meat

        self.game.playground.cells[5].tile = hegemony_hq
        self.game.playground.cells[17].tile = hegemony_meat
        self.game.playground.cells[18].tile = hegemony_med1
        self.game.playground.cells[9].tile = hegemony_med2
        self.game.playground.cells[2].tile = hegemony_qm1
        self.game.playground.cells[12].tile = hegemony_qm2
        self.game.playground.cells[0].tile = hegemony_archer
        self.game.playground.cells[8].tile = hegemony_universal1
        self.game.playground.cells[11].tile = hegemony_universal2

        self.game.start_game(self.game.begin_battle, [], {'continuer': self.game.end_game, 'period': 1})

        # check state

        # Moloch Meat
        assert self.game.playground.cells[1].tile.injuries == 1
        # Moloch Clown 1
        assert not self.game.playground.cells[4].tile
        # Moloch Clown 2
        assert not self.game.playground.cells[16].tile
        # Moloch Mother Module
        assert not self.game.playground.cells[15].tile
        # Hegemony Meat
        assert self.game.playground.cells[17].tile.injuries == 0
        # Hegemony Medic 1
        assert not self.game.playground.cells[18].tile
        # Hegemony Medic 2
        assert not self.game.playground.cells[9].tile
        # Hegemony Archer
        assert self.game.playground.cells[0].tile.injuries == 1
        # Hegemony QM 1
        assert self.game.playground.cells[2].tile.injuries == 0
        # Hegemony QM 2
        assert not self.game.playground.cells[12].tile
        # Hegemony Universal 1
        assert self.game.playground.cells[8].tile.injuries == 0
        # Hegemony Universal 2
        assert self.game.playground.cells[11].tile.injuries == 0
        # Hegemony HQ
        assert self.game.playground.cells[5].tile.injuries == 3
        # Moloch HQ
        assert self.game.playground.cells[13].tile.injuries == 3

