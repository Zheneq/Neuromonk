__author__ = 'dandelion'


class Order(object):
    def __init__(self, type):
        self.type = type


class Tile(object):
    """
    Basic tile class. Has common to all tiles attributes: army id, HP and injuries, taken in battle,
    is unit under the net or not. Also stores support battle info such as damage taken in battle phase and medics
    healing unit.
    """
    def __init__(self ,id, hp):
        """
        Tile constructor.
        :param id: id of army this unit belongs to.
        :param hp: HP of unit.
        :return: nothing is returned.
        """
        self.army_id = id
        self.taken_damage = []
        self.active_medics = []
        self.hp = hp
        self.active = True
        self.injuries = 0
        self.gfx = None

    def invalidate(self):
        """
        Refreshes visual representation of the tile
        :return: nothing is returned.
        """
        self.gfx = None


class Unit(Tile):
    """
    Standard unit class. Besides of common tile info stores initiative, attack, armor and using nets.
    """
    def __init__(self, id, hp, melee, range, armor, nets, initiative,
                 row_attack=False, melee_buff=True, range_buff=True, mobility=False):
        """
        Unit constructor.
        :param id: id of army this unit belongs to.
        :param hp: HP of unit.
        :param melee: list of melee damage unit can deal. Every item of list is wounds in one direction.
        None if unit can't attack in melee.
        :param range: list of range damage unit can deal. Similar to 'melee' parameter.
        None if unit can't attack in range.
        :param armor: list of armor unit has. Similar to 'melee' and 'range' parameters.
        None if unit hasn't armor.
        :param nets: list of directions unit can throw a net. Item of list is 1 if unit can throw and 0 otherwise.
        None if unit can't use nets.
        :param initiative: list of initiative phases unit can action in battle. Every item of list is pair
        (number, used), where 'number' is phase number and 'used' is a boolean flag reset when unit action in this phase.
        None if unit is passive during battle.
        :param row_attack: boolean flag set when ranged attacks of unit deal damage to all enemies in a row of attack.
        :param melee_buff: boolean flag set when unit can be influenced by melee damage modificators.
        :param range_buff: boolean flag set when unit can be influenced by range damage modificators.
        :param mobility: boolean flag set when unit is mobile.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp)
        self.initiative = initiative
        self.melee = melee
        self.range = range
        self.armor = armor
        self.nets = nets
        self.row_attack = row_attack
        self.can_melee_buffed = melee_buff
        self.can_range_buffed = range_buff
        self.mobile = mobility
        self.add_attacks_used = 0

    def damage(self, direction):
        """
        Gets damage of unit in 'direction'
        :param direction: direction of attack.
        :return: returns dictionary with two keys: 'melee' and 'range'. Values are wounds.
        """
        result = {}
        if self.melee:
            result['melee'] = self.melee[direction % 6]
        else:
            result['melee'] = 0
        if self.range:
            result['range'] = self.range[direction % 6]
        else:
            result['range'] = 0
        return result

    def get_armor(self, direction):
        """
        Gets armor unit has in 'direction'
        :param direction: direction of armor.
        :return: returns value of armor strength.
        """
        if self.armor:
            return self.armor[(direction + 3) % 6]
        return 0

    def attack(self, cell, damage_modificator):
        """
        Performs unit's action during battle.
        :param cell: cell where unit is on the battlefield.
        :param damage_modificator: all bonuses influence unit.
        :return: nothing is returned.
        """
        for ind in xrange(len(cell.neighbours)):
            damage = self.damage(ind - cell.turn)
            if self.can_melee_buffed and 'melee' in damage_modificator:
                damage['melee'] += damage_modificator['melee']
            if self.can_range_buffed and 'range' in damage_modificator:
                damage['range'] += damage_modificator['range']
            if damage['melee'] > 0:
                if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
                    if cell.neighbours[ind].tile.army_id != self.army_id:
                        damage_to_unit = {'value': damage['melee'], 'type': 'melee', 'instigator': self}
                        cell.neighbours[ind].tile.taken_damage.append(damage_to_unit)
            if damage['range'] > 0:
                neighbour = cell.neighbours[ind]
                while neighbour is not None:
                    if neighbour.tile is not None and neighbour.tile.army_id != self.army_id:
                        range_damage = damage['range'] - neighbour.tile.get_armor(ind - neighbour.turn)
                        if range_damage > 0:
                            damage_to_unit = {'value': range_damage,
                                              'type': 'range',
                                              'instigator': self}
                            neighbour.tile.taken_damage.append(damage_to_unit)
                        if not self.row_attack:
                            break
                    neighbour = neighbour.neighbours[ind]

    def maneuver_rate(self, cell, depth=1, result=None):
        if not result:
            result = [cell]
        if depth > 0:
            for neighbour in cell.neighbours:
                if neighbour in result:
                    #visited cell
                    continue
                else:
                    # unvisited cell
                    if neighbour.tile is None:
                        # free cell
                        result.append(neighbour)
                        self.maneuver_rate(neighbour, depth - 1, result)
            return result
        return result


class Module(Tile):
    """
    Standard module class. Modules buff allies and debuff enemies
    """
    def __init__(self, id, hp, buff, debuff):
        """
        Module constructor.
        :param id: id of army this module belongs to.
        :param hp: HP of module.
        :param buff: dictionary of buffs of module. Key is type of bonus, value is list of bonus' values in directions.
        :param debuff: dictionary of debuffs of module. Similar to 'buff' parameter.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp)
        self.buff = buff
        self.debuff = debuff

    def get_buffs(self, direction):
        """
        Gets buffs of module in 'direction'
        :param direction: direction of buffing.
        :return: returns dictionary of values of each buff type
        """
        result = {}
        for bufftype in self.buff:
            result[bufftype] = self.buff[bufftype][(direction + 3) % 6]
        return result

    def get_debuffs(self, direction):
        """
        Gets debuffs of module in 'direction'
        :param direction: direction of debuffing.
        :return: returns dictionary of values of each debuff type
        """
        result = {}
        for debufftype in self.debuff:
            result[debufftype] = self.debuff[debufftype][(direction + 3) % 6]
        return result


class Medic(Tile):
    """
    Medic class. Stores directions medic can heal allies.
    """
    def __init__(self, id, hp, direction):
        """
        Medic constructor.
        :param id: id of army this medic belongs to.
        :param hp: HP of medic.
        :param direction: list of directions medic can heal. Item is 1 if medic can heal and 0 otherwise.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp)
        self.direction = direction


class Base(Unit, Module):
    """
    Standard Headquarter class. HQ has features of unit (it can move and fight) and module (it can buff).
    """
    def __init__(self, id, hp, melee, initiative, buff, debuff, melee_buff=True):
        """
        Base constructor.
        :param id: id of army this unit belongs to.
        :param hp: HP of unit.
        :param melee: list of melee damage HQ can deal. Every item of list is wounds in one direction.
        None if HQ can't attack in melee.
        :param initiative: list of initiative phases HQ can action in battle. Every item of list is pair
        (number, used), where 'number' is phase number and 'used' is a boolean flag reset when HQ action in this phase.
        None if HQ is passive during battle.
        :param buff: dictionary of buffs of HQ. Key is type of bonus, value is list of bonus' values in directions.
        :param debuff: dictionary of debuffs of HQ. Similar to 'buff' parameter.
        :param melee_buff: boolean flag set when HQ can be influenced by melee damage modificators.
        :return: nothing is returned.
        """
        Unit.__init__(self, id, hp, melee, None, None, None, initiative, melee_buff=melee_buff)
        Module.__init__(self, id, hp, buff, debuff)


if __name__ == "__main__":
    borgo_mutant1 = Unit(0, (2,1,0,0,0,1), 1, 2)
    borgo_mutant2 = Unit(0, (2,1,0,0,0,1), 1, 2)
    borgo_killer1 = Unit(0, (3,0,0,0,0,0), 2, 2)
    moloch_hunter1 = Unit(1, (1,1,1,1,1,1), 1, 3)
