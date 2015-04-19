__author__ = 'dandelion'

from grid import Grid
from tile import *
from renderer import Renderer


def get_modificator(cell, mod_type):
    mod = 0
    for ind in xrange(len(cell.neighbours)):
        if cell.neighbours[ind] is not None and cell.neighbours[ind].tile is not None:
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
    return get_modificator(cell, 'initiative')


def compute_attack(cell):
    attack_mod = {'melee': 0, 'range': 0}
    attack_mod['melee'] += get_modificator(cell, 'melee')
    attack_mod['range'] += get_modificator(cell, 'range')
    return attack_mod


def compute_additional_attacks(cell):
    return get_modificator(cell, 'add_attacks')


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
    # refresh support info
    refresh_units(grid)


def give_damage_phase(grid, phase):
    for cell in grid.cells:
        if cell.tile is not None and type(cell.tile) == Unit:
            # gathering all buffs of initiative and add. attacks
            initiative_modificator = compute_initiative(cell)
            min_initiative = 100
            for initiative_ind in xrange(len(cell.tile.initiative)):
                if cell.tile.initiative[initiative_ind][0] < min_initiative:
                    min_initiative = cell.tile.initiative[initiative_ind][0]
                if cell.tile.initiative[initiative_ind][1] and \
                                phase == cell.tile.initiative[initiative_ind][0] + initiative_modificator:
                    # gathering all buffs of attack strength
                    damage_modificator = compute_attack(cell)
                    # giving damage
                    cell.action(damage_modificator)
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
                            cell.action(damage_modificator)
                            # mark used additional attack
                            cell.tile.add_attacks_used += 1
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


def refresh_units(grid):
    for cell in grid.cells:
        if cell.tile is not None and type(cell.tile) == Unit:
            cell.tile.add_attacks_used = 0
            for initiative_ind in xrange(len(cell.tile.initiative)):
                cell.tile.initiative[initiative_ind][1] = True


if __name__ == "__main__":
    playground = Grid(1)

    outpost_kicker = Unit(0, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])
    outpost_scout = Module(0, 1, {'initiative': [1,1,0,0,0,1]}, {})
    outpost_mothermodule = Module(0, 1, {'add_attacks': [2,0,0,0,0,0]}, {})
    moloch_fat = Unit(1, 5, (0,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[0, True]])
    moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[4, True]])

    playground.cells[0].tile = outpost_kicker
    playground.cells[0].turn = 1
    playground.cells[2].tile = moloch_fat
    playground.cells[2].turn = 0
    playground.cells[3].tile = moloch_greaver
    playground.cells[3].turn = 4
    playground.cells[4].tile = outpost_scout
    playground.cells[4].turn = 0
    playground.cells[5].tile = outpost_mothermodule
    playground.cells[5].turn = 1

    renderer = Renderer(None)
    renderer.render_board(playground)

    battle(playground)

    print "Yay!"