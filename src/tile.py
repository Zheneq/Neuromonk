__author__ = 'dandelion'


class Tile(object):
    def __init__(self ,id, hp):
        self.army_id = id
        self.taken_damage = []
        self.hp = hp
        self.injuries = 0


class Unit(Tile):
    def __init__(self, id, melee, range, armor, hp, initiative, row_attack=False, melee_buff=True):
        Tile.__init__(self, id, hp)
        self.initiative = initiative
        self.melee = melee
        self.range = range
        self.armor = armor
        self.row_attack = row_attack
        self.melee_buffed = melee_buff

    def damage(self, direction):
        result = {'melee': self.melee[direction % 6], 'range': self.range[direction % 6]}
        return result

    def get_armor(self, direction):
        return self.armor[(direction + 3) % 6]


class Base(Tile):
    def __init__(self, id, melee, hp, initiative, melee_buff=True):
        Tile.__init__(self, id, hp)


class Module(Tile):
    def __init__(self, id, hp, buff):
        Tile.__init__(self, id, hp)


if __name__ == "__main__":
    borgo_mutant1 = Unit(0, (2,1,0,0,0,1), 1, 2)
    borgo_mutant2 = Unit(0, (2,1,0,0,0,1), 1, 2)
    borgo_killer1 = Unit(0, (3,0,0,0,0,0), 2, 2)
    moloch_hunter1 = Unit(1, (1,1,1,1,1,1), 1, 3)
