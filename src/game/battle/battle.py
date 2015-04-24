__author__ = 'dandelion'

from tile import Unit, Base

from buffs import compute_initiative, compute_attack, compute_additional_attacks
from medics import resolve_medics


def give_damage_phase(playground, phase):
    """
    In this phase units give damage to all directions they can.
    Adsorbed damage is stored in "taken_damage" field if avery tile.
    :param playground: battlefield.
    :param phase: number of battle phase.
    :return: nothing is returned.
    """
    for cell in playground.cells:
        if cell.tile is not None and cell.tile.active and isinstance(cell.tile, Unit):
            # gathering all buffs of initiative and add. attacks
            initiative_modificator = compute_initiative(cell)
            min_initiative = 100
            if cell.tile.initiative:
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    if cell.tile.initiative[initiative_ind][0] + initiative_modificator < min_initiative:
                        min_initiative = cell.tile.initiative[initiative_ind][0]
                    if cell.tile.initiative[initiative_ind][1] and \
                                    phase == cell.tile.initiative[initiative_ind][0] + initiative_modificator:
                        # gathering all buffs of attack strength
                        damage_modificator = compute_attack(cell)
                        # giving damage
                        cell.tile.action(cell, damage_modificator)
                        # disable attack in this phase
                        cell.tile.initiative[initiative_ind][1] = False
                        break
                else:
                    additional_atacks = compute_additional_attacks(cell)
                    if additional_atacks > cell.tile.add_attacks_used:
                        for add_attack in range(additional_atacks):
                            if phase == min_initiative - (add_attack + 1):
                                # gathering all buffs of attack strength
                                damage_modificator = compute_attack(cell)
                                # giving damage
                                cell.tile.action(cell, damage_modificator)
                                # mark used additional attack
                                cell.tile.add_attacks_used += 1
                                break


def take_damage_phase(playground):
    """
    In this phase medics heal their patients and unhealed damage converts to injuries.
    If unit's HP is over, it's corpse is removed from battlefield.
    :param playground: battlefield.
    :return: nothing is returned.
    """
    # for avery HQ remove damage taken from other HQ
    for cell in playground.cells:
        if cell.tile is not None and isinstance(cell.tile, Base):
            cleaned_taken_damage = []
            for damage in cell.tile.taken_damage:
                if not isinstance(damage['instigator'], Base):
                    cleaned_taken_damage.append(damage)
            cell.tile.taken_damage = cleaned_taken_damage
    # resolve possible medic conflicts
    resolve_medics(playground)
    for cell in playground.cells:
        if cell.tile is not None:
            damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
            if cell.tile.hp - cell.tile.injuries > damage:
                cell.tile.injuries += damage
                # reset "taken_damage"
                cell.tile.taken_damage = []
            else:
                # if died unit is net fighter release all units caught by him
                if isinstance(cell.tile, Unit) and cell.tile.nets:
                    for ind in xrange(len(cell.neighbours)):
                        if cell.tile.nets[(ind + 6 - cell.turn) % 6] and \
                                    cell.neighbours[ind] is not None and \
                                    cell.neighbours[ind].tile is not None and \
                                    cell.neighbours[ind].tile.army_id != cell.tile.army_id:
                            # release unit if there is no other net fighters
                            neighbour = cell.neighbours[ind]
                            for ind in xrange(len(neighbour.neighbours)):
                                if cell.neighbours[ind] is not None and \
                                            cell.neighbours[ind].tile is not None and \
                                            cell.neighbours[ind].tile.army_id != cell.tile.army_id and \
                                            isinstance(cell.neighbours[ind].tile, Unit) and \
                                            cell.neighbours[ind].tile.nets and \
                                            cell.neighbours[ind].tile.nets[(ind + 9 - cell.turn) % 6]:
                                    break
                            else:
                                neighbour.tile.active = True
                cell.tile = None


def refresh_units(playground):
    """
    Resets initiative if every unit to prepare their to future battle.
    :param playground: battlefield.
    :return: nothing is returned.
    """
    for cell in playground.cells:
        if cell.tile is not None and isinstance(cell.tile, Unit):
            cell.tile.add_attacks_used = 0
            if cell.tile.initiative:
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    cell.tile.initiative[initiative_ind][1] = True
