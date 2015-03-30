__author__ = 'dandelion'

from grid import Grid
from tile import *


def battle(grid):
    # find max initiative
    max_initiative = 0
    for cell in grid.cells:
        if cell.tile is not None and type(cell.tile) == Unit:
            # TODO get buffs and debuffs of initiative
            # for neighbour in cell.neighbours:
            # if neighbour is not None and neighbour.tile is not None and type(neighbour)
            if cell.tile.initiative > max_initiative:
                max_initiative = cell.tile.initiative
    # battle
    for phase in range(max_initiative + 1)[::-1]:
        # phase of giving damage
        give_damage_phase(grid, phase)
        # phase of taking damage and cleaning corpses
        take_damage_phase(grid)


def give_damage_phase(grid, phase):
    for cell in grid.cells:
        if cell.tile is not None and type(cell.tile) == Unit:
            # TODO get all buffs and debuffs
            # for neighbour in cell.neighbours:
            # if neighbour is not None and neighbour.tile is not None and type(neighbour)
            if cell.tile.initiative == phase:
                for ind in xrange(len(cell.neighbours)):
                    damage = cell.tile.damage(ind - cell.turn)
                    if damage['melee'] > 0:
                        if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
                            if cell.neighbours[ind].tile.army_id != cell.tile.army_id:
                                damage_to_unit = {'value': damage['melee'], 'type': 'melee', 'instigator': cell.tile}
                                cell.neighbours[ind].tile.taken_damage.append(damage_to_unit)
                    if damage['range'] > 0:
                        # TODO range damage
                        pass


def take_damage_phase(grid):
    for cell in grid.cells:
        if cell.tile is not None:
            # TODO if there is connected medic resolve it's possible conflicts
            damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
            if cell.tile.hp - cell.tile.injuries > damage:
                cell.tile.injuries += damage
                cell.tile.taken_damage = []
            else:
                # TODO release disabled units (by nets)
                cell.tile = None


if __name__ == "__main__":
    playground = Grid(1)

    borgo_mutant1 = Unit(0, (2, 1, 0, 0, 0, 1), 1, 2)
    borgo_mutant2 = Unit(0, (2, 1, 0, 0, 0, 1), 1, 2)
    borgo_killer1 = Unit(0, (3, 0, 0, 0, 0, 0), 2, 2)
    moloch_hunter1 = Unit(1, (1, 1, 1, 1, 1, 1), 1, 3)

    playground.cells[0].tile = moloch_hunter1
    playground.cells[0].turn = 0
    playground.cells[1].tile = borgo_mutant1
    playground.cells[1].turn = 3
    playground.cells[4].tile = borgo_mutant2
    playground.cells[4].turn = 0
    playground.cells[5].tile = borgo_killer1
    playground.cells[5].turn = 1

    battle(playground)

    print "Yay!"