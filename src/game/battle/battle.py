__author__ = 'dandelion'

from tile import Unit, Base

from buffs import compute_initiative, compute_attack, compute_additional_attacks
from medics import Medicine


class Battle(object):
    """
    Class for support info in battle.
    Stores current initiative phase, the battlefield and support info for event performing.
    """
    def __init__(self,
                 playground,
                 pend_click,
                 releaser,
                 event,
                 timer,
                 period,
                 renderer,
                 continue_game,
                 init_phase=1000):
        """
        Battle constructor.
        :param playground: battlefield.
        :param pend_click: function assigning callback to dictionary of actors.
        :param event: event poster.
        :param timer: function creating delay before action.
        :param period: time of delay in milliseconds.
        :param releaser: function releasing disable by net units.
        :param renderer: for debug reasons (don't know why).
        :param continue_game: function continuing game after battle.
        :param init_phase: phase of battle in special cases (such as airstrike, sniper, grenade, etc.).
        """
        self.battlefield = playground

        self.pend_click = pend_click
        self.event = event
        self.set_timer = timer
        self.period = period
        self.release_disable_units = releaser
        self.renderer = renderer
        self.continue_game = continue_game

        if init_phase == 1000:
            self.initiative_phase = 0
            for cell in self.battlefield.cells:
                if cell.tile is not None and isinstance(cell.tile, Unit) and cell.tile.initiative:
                    # reset additional attacks
                    cell.tile.add_attacks_used = 0
                    # reset initiative
                    for initiative_ind in xrange(len(cell.tile.initiative)):
                        cell.tile.initiative[initiative_ind][1] = True
                    # find max initiative to start form
                    initiative_modificator = compute_initiative(cell)
                    if cell.tile.initiative[0][0] + initiative_modificator > self.initiative_phase:
                        self.initiative_phase = cell.tile.initiative[0][0] + initiative_modificator
        else:
            self.initiative_phase = init_phase

    def battle_phase(self):
        """
        Actions during one initiative phase in battle.
        :return: nothing is returned.
        """
        # phase of giving damage
        self.give_damage_phase()
        # phase of taking damage and cleaning corpses
        self.take_damage_phase()

    def end_battle(self):
        """
        Finishes battle and continues game.
        :return: nothing is returned.
        """
        # debug
        self.renderer.idle = False
        self.event(self.continue_game)

    def give_damage_phase(self):
        """
        In this phase units give damage to all directions they can.
        Adsorbed damage is stored in "taken_damage" field if avery tile.
        :return: nothing is returned.
        """
        for cell in self.battlefield.cells:
            if cell.tile is not None and cell.tile.active and isinstance(cell.tile, Unit):
                # gathering all buffs of initiative and add. attacks
                initiative_modificator = compute_initiative(cell)
                min_initiative = 100
                if cell.tile.initiative:
                    for initiative_ind in xrange(len(cell.tile.initiative)):
                        if cell.tile.initiative[initiative_ind][0] + initiative_modificator < min_initiative:
                            min_initiative = cell.tile.initiative[initiative_ind][0]
                        if cell.tile.initiative[initiative_ind][1] and \
                                        self.initiative_phase == cell.tile.initiative[initiative_ind][0] + \
                                        initiative_modificator:
                            # gathering all buffs of attack strength
                            damage_modificator = compute_attack(cell)
                            # giving damage
                            cell.tile.attack(cell, damage_modificator)
                            # disable attack in this phase
                            cell.tile.initiative[initiative_ind][1] = False
                            break
                    else:
                        additional_atacks = compute_additional_attacks(cell)
                        if additional_atacks > cell.tile.add_attacks_used:
                            for add_attack in range(additional_atacks):
                                if self.initiative_phase == min_initiative - (add_attack + 1):
                                    # gathering all buffs of attack strength
                                    damage_modificator = compute_attack(cell)
                                    # giving damage
                                    cell.tile.attack(cell, damage_modificator)
                                    # mark used additional attack
                                    cell.tile.add_attacks_used += 1
                                    break

    def take_damage_phase(self):
        """
        Removes damage from HQ to another HQ and resolves medics.
        :return: nothing is returned.
        """
        # for every HQ remove damage taken from other HQ
        for cell in self.battlefield.cells:
            if cell.tile is not None and isinstance(cell.tile, Base):
                cleaned_taken_damage = []
                for damage in cell.tile.taken_damage:
                    if not isinstance(damage['instigator'], Base):
                        cleaned_taken_damage.append(damage)
                cell.tile.taken_damage = cleaned_taken_damage
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
                if cell.tile.hp - cell.tile.injuries > damage:
                    cell.tile.injuries += damage
                    # reset "taken_damage"
                    cell.tile.taken_damage = []
                else:
                    # if died unit is net fighter release all units caught by him
                    self.release_disable_units(cell)
                    cell.tile = None
        self.initiative_phase -= 1
        if self.initiative_phase < 0:
            self.event(self.end_battle)
        else:
            self.set_timer(self.period, self.battle_phase)
