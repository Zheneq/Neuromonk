__author__ = 'dandelion'

from tile import Medic
from armies import armies


class Medicine(object):

    def __init__(self, battlefield, pend_click, continue_battle, make_event):
        self.battlefield = battlefield
        self.pend_click = pend_click
        self.continue_battle = continue_battle
        self.event = make_event

    def assign_medic(self, cell, medic_cell):
        """
        Assigns medic to all damaged units connected to this medic.
        Tiles connected to medic are searched by recursive DFS.
        :param cell: current node of recursion.
        :param medic_cell: cell with healing medic we assign.
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
                    if isinstance(neighbour.tile, Medic) and neighbour.tile.active:
                        self.assign_medic(neighbour, medic_cell)

    def compute_medics(self):
        """
        Assigns every medic to all units connected to it. .
        :return: nothing is returned.
        """
        for cell in self.battlefield.cells:
            if cell.tile is not None and cell.tile.active and isinstance(cell.tile, Medic):
                damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
                if cell.tile.hp - cell.tile.injuries > damage:
                    # medic can heal somebody who is connected to it
                    self.assign_medic(cell, cell)

    def clean_medics(self):
        """
        Cleans assigned medics in every tile.
        :return: nothing is returned.
        """
        for cell in self.battlefield.cells:
            if cell.tile is not None:
                cell.tile.active_medics = []

    def resolve_medics(self):
        """
        Creates dictionary of (patient, list of healing medics) for user to choose from.
        If there is no patients with healing medics continues the battle.
        :return: nothing is returned.
        """
        self.clean_medics()
        self.compute_medics()
        damaged_units_to_heal = {}
        for cell in self.battlefield.cells:
            if cell.tile is not None and cell.tile.taken_damage and cell.tile.active_medics:
                # unit is able to be healed by one of medics in list
                damaged_units_to_heal[cell] = cell.tile.active_medics
        if damaged_units_to_heal:
            if len(damaged_units_to_heal.keys()) == 1 and \
                            len(damaged_units_to_heal[damaged_units_to_heal.keys()[0]]) == 1:
                self.one_medic_resolve((damaged_units_to_heal.keys()[0],
                                        damaged_units_to_heal[damaged_units_to_heal.keys()[0]][0]))
            else:
                # assign callback to dictionary
                self.pend_click(damaged_units_to_heal, self.one_medic_resolve)
        else:
            self.continue_battle()

    def one_medic_resolve(self, (patient, medic)):
        """
        Resolves one medic. Healing medic removes max damage from single instigator.
        :return: nothing is returned.
        """
        #TODO choose wound (if it is important)
        # remove max damage from single instigator
        healed_damage = max(patient.tile.taken_damage, key=lambda x: x['value'])
        print armies[medic.tile.army_id]().name, 'Medic', '(' + 'cell', str(self.battlefield.cells.index(medic)) + ')', \
            'heals', armies[patient.tile.army_id]().name, patient.tile.name, \
            '(' + 'cell', str(self.battlefield.cells.index(patient)) + ')', 'from', healed_damage['value'], 'wounds'
        patient.tile.taken_damage.remove(healed_damage)
        medic.tile = None
        self.event(self.resolve_medics)
