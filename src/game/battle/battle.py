__author__ = 'dandelion'

from string import letters

from src.game.common.grid import Button
from src.game.common.tile import Unit, Base, Module, DisposableModule
from src.game.common.armies import armies

from src.game.common.buffs import compute_initiative, compute_attack, compute_additional_attacks
from medics import Medicine


class Battle(object):
    """
    Class for support info in battle.
    Stores current initiative phase, the battlefield and support info for event performing.
    """
    def __init__(self,
                 playground,
                 pend_click,
                 buttons,
                 releaser,
                 event,
                 timer,
                 period,
                 continue_game,
                 init_phase=1000):
        """
        Battle constructor.
        :param playground: battlefield.
        :param pend_click: function assigning callback to dictionary of actors.
        :param buttons: buttons of game menu to get user choice.
        :param event: event poster.
        :param timer: function creating delay before action.
        :param period: time of delay in milliseconds.
        :param releaser: function releasing disable by net units.
        :param continue_game: function continuing game after battle.
        :param init_phase: phase of battle in special cases (such as airstrike, sniper, grenade, etc.).
        """
        self.battlefield = playground
        self.active = True

        self.pend_click = pend_click
        self.buttons = buttons
        self.event = event
        self.set_timer = timer
        self.period = period
        self.release_disable_units = releaser
        self.continue_game = continue_game

        self.actions = {}
        self.converting_unit = None

        if init_phase == 1000:
            print _("Let the Battle Begin!!!")
            self.initiative_phase = 0
            for cell in self.battlefield.cells:
                # reset disposable modules
                if cell.tile is not None and isinstance(cell.tile.hex, DisposableModule):
                    cell.tile.used = []
                if cell.tile is not None and isinstance(cell.tile.hex, Unit) and cell.tile.hex.initiative:
                    # reset additional attacks
                    cell.tile.add_attacks_used = 0
                    # reset initiative
                    for initiative_ind in xrange(len(cell.tile.hex.initiative)):
                        cell.tile.hex.initiative[initiative_ind][1] = True
                    # find max initiative to start form
                    initiative_modificator = compute_initiative(cell)
                    if cell.tile.hex.initiative[0][0] + initiative_modificator > self.initiative_phase:
                        self.initiative_phase = cell.tile.hex.initiative[0][0] + initiative_modificator
            print _("Maximum initiative is %d") % self.initiative_phase
            print ' '
        else:
            self.initiative_phase = init_phase

    def battle_phase(self):
        """
        Actions during one initiative phase in battle.
        :return: nothing is returned.
        """
        for cell in self.battlefield.cells:
            if cell.tile is not None and isinstance(cell.tile.hex, Unit) and cell.tile.hex.initiative:
                # reset unit converters
                for ind in xrange(len(cell.tile.convert)):
                    if cell.tile.hex.melee and cell.tile.hex.melee[ind] or \
                            cell.tile.hex.range and cell.tile.hex.range[ind]:
                        cell.tile.convert[ind] = 'able'
        print _("Battle phase %d begins.") % self.initiative_phase
        # phase of giving damage
        self.resolve_converts()

    def end_battle(self):
        """
        Finishes battle and continues game.
        :return: nothing is returned.
        """
        self.active = False
        self.event(self.continue_game)

#-------------------------------resolving-converters-------------------------------------------
    def get_converts(self, cell, initiative_ind, add_attack=False):
        for ind in xrange(len(cell.neighbours)):
            if cell.neighbours[ind] is not None and \
                    cell.neighbours[ind].tile is not None and \
                    cell.neighbours[ind].tile.active and \
                    cell.neighbours[ind].tile.hex.army_id == cell.tile.hex.army_id:
                if isinstance(cell.neighbours[ind].tile.hex, Module) and \
                        not isinstance(cell.neighbours[ind].tile.hex, DisposableModule) or \
                        isinstance(cell.neighbours[ind].tile.hex, DisposableModule) and \
                        cell.tile.hex not in cell.neighbours[ind].tile.used:
                    buffs = cell.neighbours[ind].tile.hex.get_buffs(ind - cell.neighbours[ind].tile.turn)
                    if 'convert' in buffs and buffs['convert']:
                        if cell.neighbours[ind] not in self.actions:
                            self.actions[cell.neighbours[ind]] = []
                        self.actions[cell.neighbours[ind]].append(cell)

    def resolve_converts(self):
        self.actions = {}
        self.units_actions_in_phase(self.get_converts)
        if self.actions:
            for module in self.actions:
                self.actions[module].append(self.buttons['confirm'])
            self.pend_click(self.actions, self.resolve_convert_for_unit)
        else:
            self.choose_actions()

    def resolve_convert_for_unit(self, (converter_cell, unit_cell)):
        if isinstance(unit_cell, Button):
            # converter resolved
            del self.actions[converter_cell]
            if self.actions:
                self.pend_click(self.actions, self.resolve_convert_for_unit)
            else:
                self.choose_actions()
            return
        else:
            # mark unit as given bonus from converter if necessary
            if isinstance(converter_cell.tile.hex, DisposableModule):
                converter_cell.tile.used.append(unit_cell.tile.hex)
            # mark converting unit
            self.converting_unit = unit_cell
            self.actions[converter_cell].remove(unit_cell)
            if len(self.actions[converter_cell]) == 1:
                # all units resolved - module resolved
                del self.actions[converter_cell]
            # find directions
            directions = []
            for ind in xrange(len(unit_cell.tile.convert)):
                if unit_cell.neighbours[(ind + unit_cell.tile.turn) % 6] is None or \
                        unit_cell.tile.convert[ind] != 'able':
                    continue
                directions.append(unit_cell.neighbours[(ind + unit_cell.tile.turn) % 6])
            if len(directions) == 1:
                self.choose_attack((unit_cell, directions[0]))
            else:
                self.pend_click({unit_cell: directions}, self.choose_attack)

    def choose_attack(self, (unit_cell, direction)):
        attack_types = []
        if unit_cell.tile.hex.melee and \
                unit_cell.tile.hex.melee[(unit_cell.neighbours.index(direction) + 6 - unit_cell.tile.turn) % 6]:
            attack_types.append(self.buttons['confirm'])
        if unit_cell.tile.hex.range and \
                unit_cell.tile.hex.range[(unit_cell.neighbours.index(direction) + 6 - unit_cell.tile.turn) % 6]:
            attack_types.append(self.buttons['apply'])
        if len(attack_types) == 1:
            self.convert_attack((direction, attack_types[0]))
        else:
            self.pend_click({direction: attack_types}, self.convert_attack)

    def convert_attack(self, (direction, type)):
        ind = (self.converting_unit.neighbours.index(direction) + 6 - self.converting_unit.tile.turn) % 6
        if type is self.buttons['apply']:
            print _("%(army)s %(hex)s converted his attack of direction %(dir)d to melee") % \
                  { 'army': _(filter(lambda x: x in letters, str(armies[self.converting_unit.tile.hex.army_id]).split('.')[-1])),
                    'hex': _(self.converting_unit.tile.hex.name),
                    'dir': self.converting_unit.neighbours.index(direction) }
            self.converting_unit.tile.convert[ind] = 'melee'
        else:
            print _("%(army)s %(hex)s converted his attack of direction %(dir)d to range") % \
                  { 'army': _(filter(lambda x: x in letters, str(armies[self.converting_unit.tile.hex.army_id]).split('.')[-1])),
                    'hex': _(self.converting_unit.tile.hex.name),
                    'dir': self.converting_unit.neighbours.index(direction) }
            self.converting_unit.tile.convert[ind] = 'range'
        if self.actions:
            self.pend_click(self.actions, self.resolve_convert_for_unit)
        else:
            self.choose_actions()

#-------------------------------Choosing-action-for-unit---------------------------------------

    def add_choice(self, cell, initiative_ind, add_attack=False):
        if cell.tile.hex.unique_attack:
            # make choice what actions unit will do in this phase
            self.actions[cell] = [self.buttons['apply'], self.buttons['confirm']]

    def choose_actions(self):
        self.actions = {}
        self.units_actions_in_phase(self.add_choice)
        if self.actions:
            self.pend_click(self.actions, self.choose_action_for_unit)
        else:
            self.give_damage_phase()

    def choose_action_for_unit(self, (unit_cell, button)):
        del self.actions[unit_cell]
        if button is self.buttons['apply']:
            unit_cell.tile.attack = unit_cell.tile.hex.unique_attack
        else:
            unit_cell.tile.attack = unit_cell.tile.hex.usual_attack
        if self.actions:
            self.pend_click(self.actions, self.choose_action_for_unit)
        else:
            self.give_damage_phase()

    def units_actions_in_phase(self, unit_actions):
        for cell in self.battlefield.cells:
            if cell.tile is not None and cell.tile.active and isinstance(cell.tile.hex, Unit):
                # gathering all buffs of initiative and add. attacks
                initiative_modificator = compute_initiative(cell)
                min_initiative = 100
                if cell.tile.hex.initiative:
                    for initiative_ind in xrange(len(cell.tile.hex.initiative)):
                        if cell.tile.hex.initiative[initiative_ind][0] + initiative_modificator < min_initiative:
                            min_initiative = cell.tile.hex.initiative[initiative_ind][0]
                        if cell.tile.hex.initiative[initiative_ind][1] and \
                                        self.initiative_phase == cell.tile.hex.initiative[initiative_ind][0] + \
                                        initiative_modificator:
                            unit_actions(cell, initiative_ind, add_attack=False)
                            break
                    else:
                        additional_atacks = compute_additional_attacks(cell)
                        if additional_atacks > cell.tile.add_attacks_used:
                            for add_attack in range(additional_atacks):
                                if self.initiative_phase == min_initiative - (add_attack + 1):
                                    unit_actions(cell, 0, add_attack=True)
                                    break

    def unit_attack(self, cell, initiative_ind, add_attack=False):
        # mark initiative as used
        if add_attack:
            cell.tile.add_attacks_used += 1
        else:
            cell.tile.hex.initiative[initiative_ind][1] = False
        # gathering all buffs of attack strength
        damage_modificator = compute_attack(cell)
        # giving damage
        cell.tile.attack(cell, damage_modificator)

    def give_damage_phase(self):
        """
        In this phase units give damage to all directions they can.
        Adsorbed damage is stored in "taken_damage" field if avery tile.
        :return: nothing is returned.
        """
        self.units_actions_in_phase(self.unit_attack)
        self.take_damage_phase()

    def take_damage_phase(self):
        """
        Removes damage from HQ to another HQ and resolves medics.
        :return: nothing is returned.
        """
        damage_to_units = {}
        for cell in self.battlefield.cells:
            if cell.tile is not None:
                if isinstance(cell.tile.hex, Base):
                    # for every HQ remove damage taken from other HQ
                    cleaned_taken_damage = []
                    for damage in cell.tile.taken_damage:
                        if not isinstance(damage['instigator'].tile.hex, Base):
                            if damage['instigator'] not in damage_to_units:
                                damage_to_units[damage['instigator']] = []
                            damage_to_units[damage['instigator']].append({'value': damage['value'],
                                                                          'type': damage['type'],
                                                                          'target': cell})
                            cleaned_taken_damage.append(damage)
                    cell.tile.taken_damage = cleaned_taken_damage
                else:
                    for damage in cell.tile.taken_damage:
                        if damage['instigator'] not in damage_to_units:
                            damage_to_units[damage['instigator']] = []
                        damage_to_units[damage['instigator']].append({'value': damage['value'],
                                                                      'type': damage['type'],
                                                                      'target': cell})
        # print all actions of units in this phase
        for instigator in damage_to_units:
            print _("%(army)s %(hex)s (cell %(index)d) damaged:") %\
                  { 'army': _(filter(lambda x: x in letters, str(armies[instigator.tile.hex.army_id]).split('.')[-1])),
                    'hex': _(instigator.tile.hex.name),
                    'index': self.battlefield.cells.index(instigator) }
            for target in damage_to_units[instigator]:
                print _("\t%(army)s %(hex)s (cell %(index)d) (%(type)s, %(value)d wounds)") %\
                      { 'army': _(filter(lambda x: x in letters, str(armies[target['target'].tile.hex.army_id]).split('.')[-1])),
                        'hex': _(target['target'].tile.hex.name),
                        'index': self.battlefield.cells.index(target['target']),
                        'type': _(target['type']),
                        'value': target['value'] }
        # resolve possible medic conflicts
        medicine = Medicine(self.battlefield, self.pend_click, self.compute_injuries, self.event)
        medicine.resolve_medics()

    def compute_injuries(self):
        """
        Converts unhealed taken damage to injuries and clears corpses, after that continues battle.
        :return: nothing is returned
        """
        for cell in self.battlefield.cells:
            if cell.tile is not None:
                damage = reduce(lambda res, x: res + x['value'], cell.tile.taken_damage, 0)
                if cell.tile.hex.hp - cell.tile.injuries > damage:
                    cell.tile.injuries += damage
                    # reset "taken_damage"
                    cell.tile.taken_damage = []
                else:
                    if not cell.tile.hex.hp:
                        print _("%s died because of natural causes.\n" +
                                "Indeed, he was scattered by explosion. It's just natural he died") % cell.tile.hex.name
                    else:
                        print _("%s died.") % cell.tile.hex.name
                    # if died unit is net fighter release all units caught by him
                    self.release_disable_units(cell)
                    cell.tile = None
        self.initiative_phase -= 1
        print ' '
        if self.initiative_phase < 0:
            self.end_battle()
        else:
            self.set_timer(self.period, self.battle_phase)
