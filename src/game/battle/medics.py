__author__ = 'dandelion'

from tile import Medic


def assign_medic(cell, medic_cell):
    """
    Assigns medic to all damaged units connected to this medic.
    Tiles connected to medic are searched by recursive DFS.
    :param playground: battlefield.
    :return: nothing is returned.
    """
    # mark all units connected with medic in "cell" as able be healed by this medic
    for ind in xrange(len(cell.neighbours)):
        if cell.tile.direction[(ind + 6 - cell.turn) % 6] and \
                        cell.neighbours[ind] is not None and \
                        cell.neighbours[ind].tile is not None:
            # this tile is connected to medic
            neighbour = cell.neighbours[ind]
            if neighbour is not medic_cell and medic_cell not in neighbour.tile.active_medics:
                neighbour.tile.active_medics.append(medic_cell)  # mark this tile
                # if tile is another medic continue chain
                if type(neighbour.tile) is Medic and neighbour.tile.active:
                    assign_medic(neighbour, medic_cell)


def compute_medics(playground):
    """
    Assigns every medic to all units connected to it. .
    :param playground: battlefield.
    :return: returns True, if there is healing medic. False, otherwise.
    """
    active_medic_found = False
    for cell in playground.cells:
        if cell.tile is not None and cell.tile.active and type(cell.tile) is Medic:
            damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
            if cell.tile.hp - cell.tile.injuries > damage:
                # medic can heal somebody who is connected to it
                active_medic_found = True
                assign_medic(cell, cell)
    return active_medic_found


def clean_medics(playground):
    """
    Cleans assigned medics in every tile.
    :param playground: battlefield.
    :return: nothing is returned.
    """
    for cell in playground.cells:
        if cell.tile is not None:
            cell.tile.active_medics = []


def one_medic_resolve(playground):
    """
    Resolves one medic conflict. After that reassign of medics is necessary.
    :param playground: battlefield.
    :return: returns list of tiles having damage to heal.
    """
    damaged_units_to_heal = []
    for cell in playground.cells:
        if cell.tile is not None and cell.tile.taken_damage and cell.tile.active_medics:
            # unit is able to be healed by one of medics in list
            damaged_units_to_heal.append(cell.tile)
    if damaged_units_to_heal:
        #TODO choose medic to heal
        # first available medic saves first available unit from first damage in "taken_damage"
        damaged_units_to_heal[0].taken_damage.remove(damaged_units_to_heal[0].taken_damage[0])
        damaged_units_to_heal[0].active_medics[1].tile = None
    return damaged_units_to_heal


def resolve_medics(playground):
    """
    Resolve all medic conflicts.
    :param playground: battlefield.
    :return: nothing is returned.
    """
    active_medic_found = compute_medics(playground)
    candidates = True
    while active_medic_found and candidates:
        candidates = one_medic_resolve(playground)
        clean_medics(playground)
        active_medic_found = compute_medics(playground)
