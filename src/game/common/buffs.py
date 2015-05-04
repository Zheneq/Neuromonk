__author__ = 'dandelion'


def compute_initiative(cell):
    """
    Gets all buffs and debuffs of initiative for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    return cell.tile.get_modificator(cell, 'initiative')


def compute_attack(cell):
    """
    Gets all buffs and debuffs of attack for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    attack_mod = {'melee': 0, 'range': 0}
    attack_mod['melee'] += cell.tile.get_modificator(cell, 'melee')
    attack_mod['range'] += cell.tile.get_modificator(cell, 'range')
    return attack_mod


def compute_additional_attacks(cell):
    """
    Gets all buffs and debuffs of additional attacks for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    return cell.tile.get_modificator(cell, 'add_attacks')


def compute_mobility(cell):
    """
    Gets all buffs and debuffs of additional attacks for 'cell'
    :param cell: cell with tile, collecting bonuses.
    :return: returns sum of all modificators
    """
    return cell.tile.get_modificator(cell, 'mobility')
