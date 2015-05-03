__author__ = 'dandelion'

from tile import *


class Army(object):
    def __init__(self, id, name, mode):
        self.army_id = id
        self.name = name
        self.hq = None
        self.army = {}
        if mode == '2vs2':
            self.base_hp = 13
        elif mode == 'dm':
            self.base_hp = 20


class Borgo(Army):
    def __init__(self, mode='dm'):
        Army.__init__(self, 2, 'Borgo', mode)
        self.hq = Base(self.army_id, self.base_hp, 'HQ', [1,1,1,1,1,1], [[0, True]], {'initiative': [1,1,1,1,1,1]}, {})
        for i in xrange(6):
            mutant = Unit(self.army_id, 1, 'Mutant', [1,1,0,0,0,1], None, None, None, [[2, True]])
            self.army['mutant' + str(i)] = mutant
        for i in xrange(4):
            claws = Unit(self.army_id, 1, 'Claws', [1,1,0,0,0,0], None, None, None, [[3, True]])
            self.army['claws' + str(i)] = claws
        supermutant = Unit(self.army_id, 2, 'Supermutant', [2,1,0,0,0,1], None, [1,1,0,0,0,1], None, [[2, True]])
        self.army['supermutant'] = supermutant
        for i in xrange(2):
            netfighter = Unit(self.army_id, 1, 'Netfighter', [3,0,0,0,0,0], None, None, [1,0,0,0,0,0], [[1, True]])
            self.army['netfighter' + str(i)] = netfighter
        for i in xrange(2):
            brawler = Unit(self.army_id, 1, 'Brawler', [2,0,0,0,0,0], None, None, None, [[2, True]])
            self.army['brawler' + str(i)] = brawler
        for i in xrange(2):
            assassin = Unit(self.army_id, 1, 'Assassin', None, [1,0,0,0,0,0], None, None, [[2, True]], mobility=True)
            self.army['assassin' + str(i)] = assassin
        medic = Medic(self.army_id, 1, 'Medic', [1,1,0,0,0,1])
        self.army['medic'] = medic
        for i in xrange(2):
            officer = Module(self.army_id, 1, 'Officer', {'melee': [1,1,0,0,0,1]}, {})
            self.army['officer' + str(i)] = officer
        superofficer = Module(self.army_id, 2, 'Superofficer', {'melee': [1,1,0,0,0,1]}, {})
        self.army['superofficer'] = superofficer
        for i in xrange(2):
            scout = Module(self.army_id, 1, 'Scout', {'initiative': [1,1,0,0,0,1]}, {})
            self.army['scout' + str(i)] = scout
        grenade = Order(self.army_id, 'grenade')
        self.army['grenade'] = grenade
        for i in xrange(6):
            battle = Order(self.army_id, 'battle')
            self.army['battle' + str(i)] = battle
        for i in xrange(4):
            move = Order(self.army_id, 'move')
            self.army['move' + str(i)] = move


class Moloch(Army):
    def __init__(self, mode='dm'):
        Army.__init__(self, 1, 'Moloch', mode)
        self.hq = Base(self.army_id, self.base_hp, 'HQ', [1,1,1,1,1,1], [[0, True]], {'range': [1,1,1,1,1,1]}, {})
        for i in xrange(2):
            blocker = Unit(self.army_id, 3, 'Blocker', None, None, [1,0,0,0,0,0], None, None)
            self.army['blocker' + str(i)] = blocker
        for i in xrange(2):
            hybrid = Unit(self.army_id, 1, 'Hybrid', None, [1,0,0,0,0,0], None, None, [[3, True]])
            self.army['hybrid' + str(i)] = hybrid
        gauss = Unit(self.army_id, 2, 'Gauss', None, [1,0,0,0,0,0], None, None, [[1, True]], row_attack=True, range_buff=False)
        self.army['gauss'] = gauss
        juggernaut = Unit(self.army_id, 2, 'Juggernaut', [2,0,0,0,0,0], [0,1,0,0,0,0], [1,0,1,0,1,0], None, [[1, True]])
        self.army['juggernaut'] = juggernaut
        for i in xrange(2):
            hunter_killer = Unit(self.army_id, 1, 'Hunter-killer', [1,1,0,1,0,1], None, None, None, [[3, True]])
            self.army['hunter_killer' + str(i)] = hunter_killer
        for i in xrange(2):
            armored_hunter = Unit(self.army_id, 1, 'Armored hunter', [1,1,1,1,1,1], None, [1,0,0,0,0,1], None, [[2, True]])
            self.army['armored_hunter' + str(i)] = armored_hunter
        armored_guard = Unit(self.army_id, 1, 'Armored guard', None, [0,1,0,0,0,1], [1,0,0,0,0,0], None, [[2, True]])
        self.army['armored_guard'] = armored_guard
        guard = Unit(self.army_id, 1, 'Guard', None, [1,0,0,0,0,1], None, None, [[2, True]])
        self.army['guard'] = guard
        protector = Unit(self.army_id, 2, 'Protector', None, [1,1,0,0,0,1], None, None, [[1, True]])
        self.army['protector'] = protector
        hornet = Unit(self.army_id, 1, 'Hornet', [2,0,0,0,0,0], None, None, None, [[2, True]])
        self.army['hornet'] = hornet
        clown = Unit(self.army_id, 2, 'Clown', [1,1,0,0,0,0], None, None, None, [[2, True]], unique_action=self.clown_explode)
        self.army['clown'] = clown
        netfighter = Unit(self.army_id, 1, 'Netfighter', None, None, None, [1,0,0,0,0,1], None)
        self.army['netfighter'] = netfighter
        stormtrooper = Unit(self.army_id, 2, 'Stormtrooper', None, [1,0,0,0,0,0], None, None, [[2, True], [1, True]])
        self.army['stormtrooper'] = stormtrooper
        mothermodule = Module(self.army_id, 1, 'Mother module', {'add_attacks': [1,0,0,0,0,0]}, {})
        self.army['mothermodule'] = mothermodule
        for i in xrange(2):
            medic = Medic(self.army_id, 1, 'Medic', [1,0,1,0,1,0])
            self.army['medic' + str(i)] = medic
        brain = Module(self.army_id, 1, 'Brain', {'melee': [1,0,1,0,1,0], 'range': [1,0,1,0,1,0]}, {})
        self.army['brain'] = brain
        officer = Module(self.army_id, 1, 'Officer', {'range': [0,1,0,1,0,1]}, {})
        self.army['officer'] = officer
        scout = Module(self.army_id, 1, 'Scout', {'initiative': [1,0,1,0,1,0]}, {})
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

    def clown_explode(self, cell, damage_modificator):
        for neighbour in cell.neighbours:
            if neighbour is not None and neighbour.tile is not None:
                neighbour.tile.taken_damage.append({'value': 1, 'type': 'explosion', 'instigator': cell})
        cell.tile.hp = 0


armies = {}
armies[1] = Moloch
armies[2] = Borgo


if __name__ == '__main__':
    moloch_army = Moloch('dm')
    borgo_army = Borgo('dm')
