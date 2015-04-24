__author__ = 'dandelion'

from tile import Module


def get_modificator(cell, mod_type):
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
            if type(cell.neighbours[ind].tile) == Module:
                # TODO add buffs from allies
                if cell.neighbours[ind].tile.army_id == cell.tile.army_id:  # it can buff
                    buffs = cell.neighbours[ind].tile.get_buffs(ind - cell.neighbours[ind].turn)
                    if mod_type in buffs:
                        mod += buffs[mod_type]
                else:  # it can debuff
                    debuffs = cell.neighbours[ind].tile.get_debuffs(ind - cell.neighbours[ind].turn)
                    if mod_type in debuffs:
                        mod -= debuffs[mod_type]
    return mod


def compute_initiative(cell):
    """
    Gets all buffs and debuffs of initiative for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    return get_modificator(cell, 'initiative')


def compute_attack(cell):
    """
    Gets all buffs and debuffs of attack for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    attack_mod = {'melee': 0, 'range': 0}
    attack_mod['melee'] += get_modificator(cell, 'melee')
    attack_mod['range'] += get_modificator(cell, 'range')
    return attack_mod


def compute_additional_attacks(cell):
    """
    Gets all buffs and debuffs of additional attacks for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    return get_modificator(cell, 'add_attacks')
