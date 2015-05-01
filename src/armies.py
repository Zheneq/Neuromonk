__author__ = 'dandelion'

from tile import *


class Army(object):
    def __init__(self, id, mode):
        self.army_id = id
        self.hq = None
        self.army = {}
        if mode == '2vs2':
            self.base_hp = 13
        elif mode == 'dm':
            self.base_hp = 5


class Borgo(Army):
    def __init__(self, mode='dm'):
        Army.__init__(self, 2, mode)
        self.hq = Base(self.army_id, self.base_hp, [1,1,1,1,1,1], [[0, True]], {'initiative': [1,1,1,1,1,1]}, {})
        for i in xrange(6):
            mutant = Unit(self.army_id, 1, [1,1,0,0,0,1], None, None, None, [[2, True]])
            self.army['mutant' + str(i)] = mutant
        for i in xrange(4):
            claws = Unit(self.army_id, 1, [1,1,0,0,0,0], None, None, None, [[3, True]])
            self.army['claws' + str(i)] = claws
        supermutant = Unit(self.army_id, 2, [2,1,0,0,0,1], None, [1,1,0,0,0,1], None, [[2, True]])
        self.army['supermutant'] = supermutant
        for i in xrange(2):
            netfighter = Unit(self.army_id, 1, [3,0,0,0,0,0], None, None, [1,0,0,0,0,0], [[1, True]])
            self.army['netfighter' + str(i)] = netfighter
        for i in xrange(2):
            brawler = Unit(self.army_id, 1, [2,0,0,0,0,0], None, None, None, [[2, True]])
            self.army['brawler' + str(i)] = brawler
        for i in xrange(2):
            assassin = Unit(self.army_id, 1, None, [1,0,0,0,0,0], None, None, [[2, True]], mobility=True)
            self.army['assassin' + str(i)] = assassin
        medic = Medic(self.army_id, 1, [1,1,0,0,0,1])
        self.army['medic'] = medic
        for i in xrange(2):
            officer = Module(self.army_id, 1, {'melee': [1,1,0,0,0,1]}, {})
            self.army['officer' + str(i)] = officer
        superofficer = Module(self.army_id, 2, {'melee': [1,1,0,0,0,1]}, {})
        self.army['superofficer'] = superofficer
        for i in xrange(2):
            scout = Module(self.army_id, 1, {'initiative': [1,1,0,0,0,1]}, {})
            self.army['scout' + str(i)] = scout
        grenade = Order(self.army_id, 'gernade')
        self.army['grenade'] = grenade
        for i in xrange(6):
            battle = Order(self.army_id, 'battle')
            self.army['battle' + str(i)] = battle
        for i in xrange(4):
            move = Order(self.army_id, 'move')
            self.army['move' + str(i)] = move


class Moloch(Army):
    def __init__(self, mode='dm'):
        Army.__init__(self, 1, mode)
        self.hq = Base(self.army_id, self.base_hp, [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {})
        for i in xrange(2):
            blocker = Unit(self.army_id, 3, None, None, [1,0,0,0,0,0], None, None)
            self.army['blocker' + str(i)] = blocker
        for i in xrange(2):
            hybrid = Unit(self.army_id, 1, None, [1,0,0,0,0,0], None, None, [[3, True]])
            self.army['hybrid' + str(i)] = hybrid
        gauss = Unit(self.army_id, 2, None, [1,0,0,0,0,0], None, None, [[1, True]], row_attack=True, range_buff=False)
        self.army['gauss'] = gauss
        juggernaut = Unit(self.army_id, 2, [2,0,0,0,0,0], [0,1,0,0,0,0], [1,0,1,0,1,0], None, [[1, True]])
        self.army['juggernaut'] = juggernaut
        for i in xrange(2):
            hunter_killer = Unit(self.army_id, 1, [1,1,0,1,0,1], None, None, None, [[3, True]])
            self.army['hunter_killer' + str(i)] = hunter_killer
        for i in xrange(2):
            armored_hunter = Unit(self.army_id, 1, [1,1,1,1,1,1], None, [1,0,0,0,0,1], None, [[2, True]])
            self.army['armored_hunter' + str(i)] = armored_hunter
        armored_guard = Unit(self.army_id, 1, None, [0,1,0,0,0,1], [1,0,0,0,0,0], None, [[2, True]])
        self.army['armored_guard'] = armored_guard
        guard = Unit(self.army_id, 1, None, [1,0,0,0,0,1], None, None, [[2, True]])
        self.army['guard'] = guard
        protector = Unit(self.army_id, 2, None, [1,1,0,0,0,1], None, None, [[1, True]])
        self.army['protector'] = protector
        hornet = Unit(self.army_id, 1, [2,0,0,0,0,0], None, None, None, [[2, True]])
        self.army['hornet'] = hornet
        netfighter = Unit(self.army_id, 1, None, None, None, [1,0,0,0,0,1], [[0, True]])
        self.army['netfighter'] = netfighter
        stormtrooper = Unit(self.army_id, 2, None, [1,0,0,0,0,0], None, None, [[2, True], [1, True]])
        self.army['stormtrooper'] = stormtrooper
        mothermodule = Module(self.army_id, 1, {'add_attacks': [1,0,0,0,0,0]}, {})
        self.army['mothermodule'] = mothermodule
        for i in xrange(2):
            medic = Medic(self.army_id, 1, [1,0,1,0,1,0])
            self.army['medic' + str(i)] = medic
        brain = Module(self.army_id, 1, {'melee': [1,0,1,0,1,0], 'range': [1,0,1,0,1,0]}, {})
        self.army['brain'] = brain
        officer = Module(self.army_id, 1, {'range': [0,1,0,1,0,1]}, {})
        self.army['officer'] = officer
        scout = Module(self.army_id, 1, {'initiative': [1,0,1,0,1,0]}, {})
        self.army['scout'] = scout
        airstrike = Order(self.army_id, 'airstrike')
        self.army['airstrike'] = airstrike
        for i in xrange(4):
            battle = Order(self.army_id, 'battle')
            self.army['battle' + str(i)] = battle
        move = Order(self.army_id, 'move')
        self.army['move'] = move
        for i in xrange(5):
            pushback = Order(self.army_id, 'pushback')
            self.army['pushback' + str(i)] = pushback


armies = {}
armies[1] = Moloch
armies[2] = Borgo


if __name__ == '__main__':
    moloch_army = Moloch('dm')
    borgo_army = Borgo('dm')
