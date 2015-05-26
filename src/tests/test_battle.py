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

        self.game.begin_battle()

        # check state

        # Moloch hunter-killer
        assert self.game.playground.cells[4].tile.active
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
