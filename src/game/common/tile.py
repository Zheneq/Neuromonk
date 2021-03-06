__author__ = 'dandelion'


class Hex(object):
    """Abstract game entity class.
    Contains attributes common to all entities players can manipulate.

    :param int id: ID of army this entity belongs to
    :param string name: Name of entity
    """
    def __init__(self, id, name):
        self.army_id = id
        self.name = name
        self.gfx = {}

    def invalidate(self):
        """Refreshes visual representation of the tile."""
        self.gfx = {}

    def initialize_wrapper(self, wrapper):
        """Adds temporary data to :py:class:`TileOnBoard()`
        Abstract method. Must be overridden in particular tile.
        """
        pass


class Order(Hex):
    """Action type class.
    It's used when player performes actions during game.

    :param int id: ID of army this Order belongs to
    :param string type: Type of Order
    """
    def __init__(self, id, type):
        Hex.__init__(self, id, type)
        self.type = type
        self.name = type


class Tile(Hex):
    """Basic tile class.
    Tile is entity that can be placed onto the board. Has common to all tiles constant attributes: HP, default mobility, etc.

    :param int id: ID of army this tile belongs to
    :param int hp: Hitpoints of tile
    :param string name: Name of tile
    :param int mobility: Amount of times tile can perform Move action during single turn
    :param bool immovable: Whether tile can move on board or not
    """

    def __init__(self, id, hp, name, mobility=0, immovable=False):
        Hex.__init__(self, id, name)
        self.hp = hp
        self.default_mobility = mobility
        self.immovable = immovable


class Unit(Tile):
    """Standard unit class.
    This is :py:class:`Tile()' that can perform different actions. Besides of common tile info stores initiative, attack, armor and using nets.

    :param int id: ID of army this tile belongs to
    :param int hp: Hitpoints of tile
    :param string name: Name of tile
    :param list melee: List of melee damage unit can deal. Every item of list is wounds in one direction.
    ``None`` if unit can't attack in melee
    :param list range: List of range damage unit can deal. Similar to `melee` parameter.
    ``None`` if unit can't attack in range
    :param list armor: List of armor unit has. Similar to `melee` and `range` parameters.
    ``None`` if unit hasn't armor
    :param list nets: List of directions unit can throw a net. Item of list is ``1`` if unit can throw and ``0`` otherwise.
    ``None`` if unit can't use nets
    :param list initiative: List of initiative phases unit can action in battle. Every item of list is pair
    `(number, used)`, where `number` is phase number and `used` is a boolean flag reset when unit action in this phase.
    ``None`` if unit is passive during battle
    :param bool row_attack: Whether unit can attack in range all enemies in it's line of sight or not
    :param bool melee_buff: Whether unit can be influenced by melee damage modificators or not
    :param bool range_buff: Whether unit can be influenced by range damage modificators or not
    :param int mobility: Amount of times tile can perform Move action during single turn
    :param function unique_action: Unique action unit can perform during his turn in battle
    :param bool immovable: Whether tile can move on board or not
    """

    def __init__(self, id, hp, name, melee, range, armor, nets, initiative,
                 row_attack=False, melee_buff=True, range_buff=True, mobility=0, unique_action=None, immovable=False):
        Tile.__init__(self, id, hp, name, mobility=mobility, immovable=immovable)
        self.initiative = initiative
        self.melee = melee
        self.range = range
        self.armor = armor
        self.nets = nets
        self.row_attack = row_attack
        self.can_melee_buffed = melee_buff
        self.can_range_buffed = range_buff
        self.unique_attack = unique_action

    def initialize_wrapper(self, wrapper):
        """Initializes temporary info of unit
        Overridden base method :py:meth:`Hex.initialize_wrapper()`. Initializes current mobility of unit, additional atacks
        unit has used in battle, table of attack type converts.

        :param TileOnBoard wrapper: Wrapper containing all temporary info of unit that is used in battle
        """
        wrapper.attack = self.usual_attack
        wrapper.add_attacks_used = 0
        wrapper.convert = [None, None, None, None, None, None]
        for ind in xrange(len(wrapper.convert)):
            if self.melee and self.melee[ind] or self.range and self.range[ind]:
                wrapper.convert[ind] = 'able'

    def damage(self, convert, direction):
        """Gets damage of unit in `direction`

        :param list convert: Table of current convertions of attack type of unit
        :param int direction: Direction of attack
        :return dict: Dicttionary of damage by different type attacks performed in given `direction`
        """
        result = {}
        if convert[direction % 6] is 'melee':
            if self.melee:
                result['melee'] = self.melee[direction % 6]
            else:
                result['melee'] = 0
            if self.range:
                # converted to melee
                result['melee'] += self.range[direction % 6]
            result['range'] = 0
        elif convert[direction % 6] is 'range':
            if self.range:
                result['range'] = self.range[direction % 6]
            else:
                result['range'] = 0
            if self.melee:
                # converted to range
                result['range'] += self.melee[direction % 6]
            result['melee'] = 0
        else:
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
        """Gets armor unit has in `direction`.

        :param int direction: Direction of armor
        :return int: Value of armor strength.
        """
        if self.armor:
            return self.armor[(direction + 3) % 6]
        return 0

    def usual_attack(self, cell, damage_modificator):
        """Performs usual unit's action during battle

        :param Cell cell: Cell where unit is on the battlefield
        :param dict damage_modificator: all bonuses influence unit
        """
        for ind in xrange(len(cell.neighbours)):
            damage = self.damage(cell.tile.convert, ind - cell.tile.turn)
            if damage['melee'] > 0:
                if self.can_melee_buffed and 'melee' in damage_modificator:
                    damage['melee'] += damage_modificator['melee']
                if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
                    if cell.neighbours[ind].tile.hex.army_id != self.army_id:
                        damage_to_unit = {'value': damage['melee'], 'type': 'melee', 'instigator': cell}
                        cell.neighbours[ind].tile.taken_damage.append(damage_to_unit)
            if damage['range'] > 0:
                if self.can_range_buffed and 'range' in damage_modificator:
                    damage['range'] += damage_modificator['range']
                neighbour = cell.neighbours[ind]
                while neighbour is not None:
                    if neighbour.tile is not None and neighbour.tile.hex.army_id != self.army_id:
                        range_damage = damage['range']
                        if isinstance(neighbour.tile.hex, Unit):
                            range_damage -= neighbour.tile.hex.get_armor(ind - neighbour.tile.turn)
                        if range_damage > 0:
                            damage_to_unit = {'value': range_damage,
                                              'type': 'range',
                                              'instigator': cell}
                            neighbour.tile.taken_damage.append(damage_to_unit)
                        if not self.row_attack:
                            break
                    neighbour = neighbour.neighbours[ind]


class Module(Tile):
    """Standard module class.
    Modules buff allies and debuff enemies.
    """

    def __init__(self, id, hp, name, buff, debuff, mobility=0, immovable=False):
        """
        Module constructor.
        :param id: id of army this module belongs to.
        :param hp: HP of module.
        :param name: name of module.
        :param buff: dictionary of buffs of module. Key is type of bonus, value is list of bonus' values in directions.
        :param debuff: dictionary of debuffs of module. Similar to 'buff' parameter.
        :param immovable: boolean flag set when unit can't move.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp, name, mobility=mobility, immovable=immovable)
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


class DisposableModule(Module):
    """
    Disposable module is module influencing each unit only once in turn.
    """

    def __init__(self, id, hp, name, buff, debuff, mobility=0, immovable=False):
        """
        Module constructor.
        :param id: id of army this module belongs to.
        :param hp: HP of module.
        :param name: name of module.
        :param buff: dictionary of buffs of module. Key is type of bonus, value is list of bonus' values in directions.
        :param debuff: dictionary of debuffs of module. Similar to 'buff' parameter.
        :param immovable: boolean flag set when unit can't move.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp, name, mobility=mobility, immovable=immovable)
        self.buff = buff
        self.debuff = debuff

    def initialize_wrapper(self, wrapper):
        wrapper.used = []


class Medic(Tile):
    """
    Medic class. Stores directions medic can heal allies.
    """

    def __init__(self, id, hp, name, direction, mobility=0):
        """
        Medic constructor.
        :param id: id of army this medic belongs to.
        :param hp: HP of medic.
        :param name: name of medic.
        :param direction: list of directions medic can heal. Item is 1 if medic can heal and 0 otherwise.
        :return: nothing is returned.
        """
        Tile.__init__(self, id, hp, name, mobility=mobility)
        self.direction = direction


class Base(Unit, Module):
    """
    Standard Headquarter class. HQ has features of unit (it can move and fight) and module (it can buff).
    """

    def __init__(self, id, hp, name, melee, initiative, buff, debuff, melee_buff=True, mobility=0):
        """
        Base constructor.
        :param id: id of army this unit belongs to.
        :param hp: HP of unit.
        :param name: name of HQ.
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
        Unit.__init__(self, id, hp, name, melee, None, None, None, initiative, melee_buff=melee_buff, mobility=mobility)
        Module.__init__(self, id, hp, name, buff, debuff, mobility=mobility)


class TileOnBoard(object):
    """
    Wrapper for tile on the board. Contains support info that can change during the game.
    """

    def __init__(self, tile, turn):
        self.hex = tile
        self.turn = turn
        self.taken_damage = []
        self.active_medics = []
        if hasattr(self.hex, 'default_mobility'):
            self.mobility = self.hex.default_mobility
        else:
            self.mobility = 0
        self.active = True
        self.injuries = 0

        self.hex.initialize_wrapper(self)

    def get_modificator(self, cell, mod_type):
        """
        Gets all buffs and debuffs of type 'modtype' for 'cell'
        :param cell: cell with tile, collecting bonuses.
        :param mod_type: type of bonuses. Now can be 'melee', 'range', 'initiative' or 'add_attacks'.
        :return: returns sum of all modificators
        """
        mod = 0
        for ind in xrange(len(cell.neighbours)):
            if cell.neighbours[ind] is not None and \
                    cell.neighbours[ind].tile is not None and \
                    cell.neighbours[ind].tile.active:
                if isinstance(cell.neighbours[ind].tile.hex, Module):
                    # TODO add buffs from allies
                    if cell.neighbours[ind].tile.hex.army_id == cell.tile.hex.army_id:  # it can buff
                        if not (isinstance(cell.neighbours[ind].tile.hex, DisposableModule) and
                                cell.tile.hex in cell.neighbours[ind].tile.used):
                            buffs = cell.neighbours[ind].tile.hex.get_buffs(ind - cell.neighbours[ind].tile.turn)
                            if mod_type in buffs and buffs[mod_type]:
                                mod += buffs[mod_type]
                                if isinstance(cell.neighbours[ind].tile.hex, DisposableModule) and \
                                        cell.tile.hex not in cell.neighbours[ind].tile.used:
                                    cell.neighbours[ind].tile.used.append(cell.tile.hex)
                    else:  # it can debuff
                        if not (isinstance(cell.neighbours[ind].tile.hex, DisposableModule) and
                                cell.tile.hex in cell.neighbours[ind].tile.used):
                            debuffs = cell.neighbours[ind].tile.hex.get_debuffs(ind - cell.neighbours[ind].tile.turn)
                            if mod_type in debuffs and debuffs[mod_type]:
                                mod -= debuffs[mod_type]
                                if isinstance(cell.neighbours[ind].tile.hex, DisposableModule) and \
                                        cell.tile.hex not in cell.neighbours[ind].tile.used:
                                    cell.neighbours[ind].tile.used.append(cell.tile.hex)
        return mod

    def maneuver_rate(self, cell, depth=1, result=None):
        if not result:
            result = [cell]
        if depth > 0:
            for neighbour in cell.neighbours:
                if neighbour in result:
                    # visited cell
                    continue
                else:
                    # unvisited cell
                    if neighbour is not None and neighbour.tile is None:
                        # free cell
                        result.append(neighbour)
                        self.maneuver_rate(neighbour, depth - 1, result)
            return result
        return result


if __name__ == "__main__":
    pass
