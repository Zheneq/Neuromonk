__author__ = 'dandelion'

import pygame
from grid import Grid
from tile import *
from renderer import Renderer

from game.battle.buffs import compute_initiative
from game.battle.battle import give_damage_phase, take_damage_phase, refresh_units


class GameMode(object):
    """
    Main game class. Controls game process.
    """
    def __init__(self, grid_radius):
        """
        Initializes necessary data
        :param grid_radius: radius of battlefield.
        :return: nothing is returned.
        """
        self.playground = Grid(self, grid_radius)
        self.renderer = Renderer(self)
        self.players = []
        self.actors = []
        self.active = False
        self.timers = {}

    def start_game(self):
        """
        Launches the main cycle
        :return: nothing is returned.
        """
        pygame.init()
        self.active = True
        self.begin_play()
        time = pygame.time.get_ticks()
        while self.active:
            prevtime = time
            time = pygame.time.get_ticks()
            # processing events
            pygame.event.pump()
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                self.active = False
            if event.type in self.timers:
                self.timers[event.type][0]()
                if not self.timers[event.type][1]:
                    pygame.time.set_timer(event.type, 0)
                    del self.timers[event.type]
            # ticking actors
            deltatime = time - prevtime
            self.tick(deltatime)
            self.renderer.tick(deltatime)
        # unintialization
        pygame.quit()

    def end_game(self):
        """
        Immediately stops the game
        :return: nothing is returned.
        """
        self.active = False

    def begin_play(self):
        # DEBUG
        self.set_timer(5000, self.battle)

    def tick(self, deltatime):
        """
        Subroutine executed every tick
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        pass

    def add_actor(self, actor):
        self.actors.append(actor)

    def set_timer(self, time, callback, repeat = False):
        """
        Set a timer
        :param time: Time in milliseconds. If 0, timer is unset
        :param callback: Function to call when the timer is fired
        :param repeat: Bool flag set when timer should be fired repeatedly
        :return: nothing is returned.
        """
        # COMMENT: Several timers may be set for one callback. When unsetting a timer with this function,
        #          which one will be unset is unknown.
        if time:
            for id in xrange(pygame.USEREVENT, pygame.NUMEVENTS):
                if id not in self.timers:
                    pygame.time.set_timer(id, time)
                    self.timers[id] = (callback, repeat)
                    break
            else:
                raise ValueError("GameMode.settimer: Too many timers!")
        else:
            for timer in self.timers:
                if self.timers[timer][0] is callback:
                    pygame.time.set_timer(timer, 0)
                    del self.timers[timer]
                    break

    def battle(self):
        """
        Computes units interaction during battle.
        :return: nothing is returned.
        """
        # prepare to battle
        # find max initiative
        max_initiative = 0
        for cell in self.playground.cells:
            if cell.tile is not None and type(cell.tile) == Unit and cell.tile.initiative:
                # reset initiative
                for initiative_ind in xrange(len(cell.tile.initiative)):
                    cell.tile.initiative[initiative_ind][1] = True
                # find max initiative
                initiative_modificator = compute_initiative(cell)
                if cell.tile.initiative[0][0] + initiative_modificator > max_initiative:
                    max_initiative = cell.tile.initiative[0][0] + initiative_modificator
        # battle
        for phase in range(max_initiative, -1, -1):
            # phase of giving damage
            give_damage_phase(self.playground, phase)
            # phase of taking damage and cleaning corpses
            take_damage_phase(self.playground)
        # refresh support info
        refresh_units(self.playground)


if __name__ == "__main__":
    battle = GameMode(2)

    outpost_kicker1 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[3, True]])
    outpost_kicker1.active = False
    outpost_kicker2 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    outpost_scout = Module(0, 1, {'initiative': [1,1,0,0,0,1]}, {})
    outpost_mothermodule = Module(0, 1, {'add_attacks': [2,0,0,0,0,0]}, {})
    moloch_fat = Unit(1, 5, None, None, None, None, None)
    moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])

    # outpost_medic1 = Medic(0, 1, [1,1,0,0,0,1])
    # outpost_medic2 = Medic(0, 1, [0,1,0,0,0,1])
    # outpost_medic3 = Medic(0, 1, [0,0,0,1,0,0])
    # outpost_medic4 = Medic(0, 1, [1,1,0,0,0,1])
    # moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), (0,0,0,0,0,0), (0,0,0,0,0,0), [[3, True]])


    battle.playground.cells[0].tile = outpost_kicker1
    battle.playground.cells[0].turn = 1
    battle.playground.cells[1].tile = moloch_netfighter
    battle.playground.cells[1].turn = 3
    battle.playground.cells[2].tile = moloch_fat
    battle.playground.cells[2].turn = 0
    battle.playground.cells[3].tile = moloch_greaver
    battle.playground.cells[3].turn = 4
    battle.playground.cells[4].tile = outpost_scout
    battle.playground.cells[4].turn = 0
    battle.playground.cells[5].tile = outpost_mothermodule
    battle.playground.cells[5].turn = 1
    battle.playground.cells[6].tile = outpost_kicker2
    battle.playground.cells[6].turn = 1

    battle.start_game()

    print "Yay!"
