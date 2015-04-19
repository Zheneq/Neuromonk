__author__ = 'dandelion'

from grid import Grid
from tile import *
from renderer import Renderer


def compute_initiative(cell):
    initiative_mod = 0
    for ind in xrange(len(cell.neighbours)):
        if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
            if type(cell.neighbours[ind].tile) == Module:
                # TODO add buffs from allies
                if cell.neighbours[ind].tile.army_id == cell.tile.army_id:  # it can buff
                    buffs = cell.neighbours[ind].tile.get_buffs(ind - cell.neighbours[ind].turn)
                    if 'initiative' in buffs:
                        initiative_mod += buffs['initiative']
                else:  # it can debuff
                    debuffs = cell.neighbours[ind].tile.get_debuffs(ind - cell.neighbours[ind].turn)
                    if 'initiative' in debuffs:
                        initiative_mod -= debuffs['initiative']
    return initiative_mod


def battle(grid):
    # prepare to battle
    # find max initiative
    max_initiative = 0
    for cell in grid.cells:
        if cell.tile is not None and type(cell.tile) == Unit:
            # reset initiative
            for initiative_ind in xrange(len(cell.tile.initiative)):
                cell.tile.initiative[initiative_ind][1] = True
            # find max initiative
            initiative_modificator = compute_initiative(cell)
            if cell.tile.initiative[0][0] + initiative_modificator > max_initiative:
                max_initiative = cell.tile.initiative[0][0] + initiative_modificator
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
            # gathering all buffs of initiative
            initiative_modificator = compute_initiative(cell)
            for initiative_ind in xrange(len(cell.tile.initiative)):
                if cell.tile.initiative[initiative_ind][1] and \
                                phase == cell.tile.initiative[initiative_ind][0] + initiative_modificator:
                    # give damage
                    for ind in xrange(len(cell.neighbours)):
                        damage = cell.tile.damage(ind - cell.turn)
                        if damage['melee'] > 0:
                            if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
                                if cell.neighbours[ind].tile.army_id != cell.tile.army_id:
                                    damage_to_unit = {'value': damage['melee'], 'type': 'melee', 'instigator': cell.tile}
                                    cell.neighbours[ind].tile.taken_damage.append(damage_to_unit)
                        if damage['range'] > 0:
                            neighbour = cell.neighbours[ind]
                            while neighbour is not None:
                                if neighbour.tile is not None and neighbour.tile.army_id != cell.tile.army_id:
                                    range_damage = damage['range'] - neighbour.tile.get_armor(ind - neighbour.turn)
                                    if range_damage > 0:
                                        damage_to_unit = {'value': range_damage,
                                                          'type': 'range',
                                                          'instigator': cell.tile}
                                        neighbour.tile.taken_damage.append(damage_to_unit)
                                    if not cell.tile.row_attack:
                                        break
                                neighbour = neighbour.neighbours[ind]
                    # disable attack in this phase
                    cell.tile.initiative[initiative_ind][1] = False
                    break


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

    outpost_kicker = Unit(0, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[2, True], [1, True]])
    outpost_scout = Module(0, 1, {'initiative': [1,1,0,0,0,1]}, {})
    moloch_fat = Unit(1, 3, (0,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[0, True]])
    moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])

    playground.cells[0].tile = outpost_kicker
    playground.cells[0].turn = 1
    playground.cells[2].tile = moloch_fat
    playground.cells[2].turn = 0
    playground.cells[3].tile = moloch_greaver
    playground.cells[3].turn = 4
    playground.cells[4].tile = outpost_scout
    playground.cells[4].turn = 0

    renderer = Renderer(None)
    renderer.render_board(playground)

    battle(playground)

    print "Yay!"