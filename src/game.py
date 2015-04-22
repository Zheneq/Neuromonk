__author__ = 'dandelion'

from grid import Grid
from tile import *
from renderer import Renderer


class GameMode(object):
    def __init__(self, grid_radius):
        self.playground = Grid(grid_radius)
        self.renderer = Renderer(None)

    def get_modificator(self, cell, mod_type):
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

    def compute_initiative(self, cell):
        return self.get_modificator(cell, 'initiative')

    def compute_attack(self, cell):
        attack_mod = {'melee': 0, 'range': 0}
        attack_mod['melee'] += self.get_modificator(cell, 'melee')
        attack_mod['range'] += self.get_modificator(cell, 'range')
        return attack_mod

    def compute_additional_attacks(self, cell):
        return self.get_modificator(cell, 'add_attacks')

    def assign_medic(self, cell, medic_cell):
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
                    if type(neighbour.tile) is Medic:
                        self.assign_medic(neighbour, medic_cell)

    def compute_medics(self):
        active_medic_found = False
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) is Medic:
                damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
                if cell.tile.hp - cell.tile.injuries > damage:
                    # medic can heal somebody who is connected to it
                    active_medic_found = True
                    self.assign_medic(cell, cell)
        return active_medic_found

    def clean_medics(self):
        for cell in self.playground.cells:
            if cell.tile is not None:
                cell.tile.active_medics = []

    def one_medic_resolve(self):
        damaged_units_to_heal = []
        for cell in self.playground.cells:
            if cell.tile is not None and cell.tile.taken_damage and cell.tile.active_medics:
                # unit is able to be healed by one of medics in list
                damaged_units_to_heal.append(cell.tile)
        #TODO choose medic to heal
        if damaged_units_to_heal:
            # first available medic saves first available unit from first damage in "taken_damage"
            damaged_units_to_heal[0].taken_damage.remove(damaged_units_to_heal[0].taken_damage[0])
            damaged_units_to_heal[0].active_medics[0].tile = None
        return damaged_units_to_heal

    def resolve_medics(self):
        active_medic_found = self.compute_medics()
        candidates = True
        while(active_medic_found and candidates):
            candidates = self.one_medic_resolve()
            self.clean_medics()
            active_medic_found = self.compute_medics()

    def battle(self):
        # prepare to battle
        # find max initiative
        max_initiative = 0
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) == Unit:
                # reset initiative
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    cell.tile.initiative[initiative_ind][1] = True
                # find max initiative
                initiative_modificator = self.compute_initiative(cell)
                if cell.tile.initiative[0][0] + initiative_modificator > max_initiative:
                    max_initiative = cell.tile.initiative[0][0] + initiative_modificator
        # battle
        for phase in range(max_initiative, -1, -1):
            # phase of giving damage
            self.give_damage_phase(phase)
            # phase of taking damage and cleaning corpses
            self.take_damage_phase()
        # refresh support info
        self.refresh_units()

    def give_damage_phase(self, phase):
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) == Unit:
                # gathering all buffs of initiative and add. attacks
                initiative_modificator = self.compute_initiative(cell)
                min_initiative = 100
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    if cell.tile.initiative[initiative_ind][0] + initiative_modificator < min_initiative:
                        min_initiative = cell.tile.initiative[initiative_ind][0]
                    if cell.tile.initiative[initiative_ind][1] and \
                                    phase == cell.tile.initiative[initiative_ind][0] + initiative_modificator:
                        # gathering all buffs of attack strength
                        damage_modificator = self.compute_attack(cell)
                        # giving damage
                        cell.action(damage_modificator)
                        # disable attack in this phase
                        cell.tile.initiative[initiative_ind][1] = False
                        break
                else:
                    additional_atacks = self.compute_additional_attacks(cell)
                    if additional_atacks > cell.tile.add_attacks_used:
                        for add_attack in range(additional_atacks):
                            if phase == min_initiative - (add_attack + 1):
                                # gathering all buffs of attack strength
                                damage_modificator = self.compute_attack(cell)
                                # giving damage
                                cell.action(damage_modificator)
                                # mark used additional attack
                                cell.tile.add_attacks_used += 1
                                break

    def take_damage_phase(self):
        self.resolve_medics()
        for cell in self.playground.cells:
            if cell.tile is not None:
                damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
                if cell.tile.hp - cell.tile.injuries > damage:
                    cell.tile.injuries += damage
                    cell.tile.taken_damage = []
                else:
                    # TODO release disabled units (by nets)
                    cell.tile = None

    def refresh_units(self):
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) == Unit:
                cell.tile.add_attacks_used = 0
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    cell.tile.initiative[initiative_ind][1] = True


if __name__ == "__main__":
    battle = GameMode(1)

    # outpost_kicker = Unit(0, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])
    # outpost_scout = Module(0, 1, {'initiative': [1,1,0,0,0,1]}, {})
    # outpost_mothermodule = Module(0, 1, {'add_attacks': [2,0,0,0,0,0]}, {})
    # moloch_fat = Unit(1, 5, (0,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[0, True]])
    # moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])

    outpost_medic1 = Medic(0, 1, [1,1,0,0,0,1])
    outpost_medic2 = Medic(0, 1, [0,1,0,0,0,1])
    outpost_medic3 = Medic(0, 1, [0,0,0,1,0,0])
    outpost_medic4 = Medic(0, 1, [1,1,0,0,0,1])


    battle.playground.cells[0].tile = outpost_medic3
    battle.playground.cells[0].turn = 4
    battle.playground.cells[2].tile = outpost_medic4
    battle.playground.cells[2].turn = 3
    battle.playground.cells[5].tile = outpost_medic2
    battle.playground.cells[5].turn = 0
    battle.playground.cells[6].tile = outpost_medic1
    battle.playground.cells[6].turn = 2

    battle.renderer.render_board(battle.playground)

    battle.battle()

    battle.renderer.render_board(battle.playground)

    print "Yay!"
