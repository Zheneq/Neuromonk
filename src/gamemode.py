__author__ = 'zheneq & dandelion'

import pygame

from grid import Grid, Cell, Button
from tile import *
from renderer import Renderer
from player import Player

from game.battle.buffs import compute_initiative
from game.battle.battle import give_damage_phase, take_damage_phase, refresh_units


class GameMode(object):
    """
    Main game class. Controls game process.
    """
    def __init__(self, grid_radius):
        """
        Initializes necessary data.
        :param grid_radius: radius of battlefield.
        :return: nothing is returned.
        """
        self.players = []
        self.player = None
        self.actors = []
        self.active = False
        self.timers = {}
        self.click_pending = {}
        self.click_callback = None
        self.click_selected = None
        self.renderer = Renderer(self)
        self.playground = Grid(self, grid_radius)
        self.turn_num = 0
        # DEBUG
        self.buttons = {}
        self.buttons['remove'] = Button(self, None, 0, 550, .1)
        self.buttons['apply'] = Button(self, None, 50, 550, .1)
        self.buttons['confirm'] = Button(self, None, 100, 550, .1)

    def start_game(self):
        """
        Launches the main cycle.
        :return: nothing is returned.
        """
        pygame.init()
        self.active = True
        self.begin_play()
        pygame.time.set_timer(self.EVENT_TICKER, 50)
        time = pygame.time.get_ticks()
        while self.active:
            prevtime = time
            time = pygame.time.get_ticks()
            # processing events
            pygame.event.pump()
            events = [pygame.event.wait()]
            events.extend(pygame.event.get())
            # print "Events:"
            for event in events:
                # debug print
                # if event.type < pygame.USEREVENT:
                #     print "\t" + pygame.event.event_name(event.type)
                # else:
                #     print "\t" + pygame.event.event_name(event.type) + "(%d)" % (event.type - pygame.USEREVENT)
                #
                if event.type == pygame.QUIT:
                    self.active = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    print "Click!"
                    clicked = self.locate(event.pos)
                    for c in clicked:
                        if isinstance(c, Cell) and c.tile is not None: print "\t" + str(type(c.tile)) + " " + str(c.tile.hp)
                        else: print "\t" + "None"
                    if clicked:
                        self.select(clicked)
                if event.type == self.EVENT_USEREVENT:
                    event.callback(event.parameters)
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
        Immediately stops the game.
        :return: nothing is returned.
        """
        self.active = False

    def test(self, (a, b)):
        print "test"
        if b:
            a.tile, b.tile = b.tile, a.tile
        else:
            print "b is none"

    def begin_play(self):
        # DEBUG
        Zq = Player('Zheneq', 1, 0, self)
        Zq.army_shuffle()
        Dand = Player('Dandelion', 2, 1, self)
        Dand.army_shuffle()
        self.players = [Zq, Dand]
        self.players[0].next = self.players[1]
        self.players[1].next = self.players[0]
        self.player = self.players[0]
        self.turn()
        # self.set_timer(20000, self.end_game)

    def tick(self, deltatime):
        """
        Subroutine executed every tick.
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        pass

    def add_actor(self, actor):
        self.actors.append(actor)

    def set_timer(self, time, callback, repeat = False):
        """
        Set a timer.
        :param time: Time in milliseconds. If 0, timer is unset
        :param callback: Function to call when the timer is fired
        :param repeat: Bool flag set when timer should be fired repeatedly
        :return: nothing is returned.
        """
        # COMMENT: Several timers may be set for one callback. When unsetting a timer with this function,
        #          which one will be unset is unknown.
        if time:
            for id in xrange(self.EVENT_MAX, pygame.NUMEVENTS):
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

    def event(self, callback, parameters = ()):
        pygame.event.post(pygame.event.Event(self.EVENT_USEREVENT, {"callback": callback, "parameters": parameters}))

    def pend_click(self, cells, callback):
        self.click_pending = cells
        self.click_callback = callback

    def locate(self, pos):
        result = []
        for obj in self.actors:
            try:
                if obj.mask.get_at((pos[0] - obj.maskrect.left, pos[1] - obj.maskrect.top)):
                    result.append(obj)
            except IndexError:
                pass
        return result

    def select(self, cells):
        """
        Common interface of selecting.
        :param cells: cells clicked by player.
        :return: nothing is returned.
        """
        for cell in cells:
            if self.click_selected is not None:
                # there is tile from dictionary selected by previous click
                if cell in self.click_pending[self.click_selected]:
                    # there is pair (source, dist) of action
                    s = self.click_selected
                    # reset selection dictionary
                    self.click_selected = None
                    self.click_pending = {}
                    self.event(self.click_callback, (s, cell))
                    break
            if cell in self.click_pending:
                # if player doesn't need to select second actor
                if not self.click_pending[cell]:
                    self.click_pending = {}
                    self.event(self.click_callback, (cell, None))
                else:
                    self.click_selected = cell
                break

    def callback_dispatcher(self, (s, cell)):
        #TODO choose the callback by parameters
        # DEBUG
        if isinstance(s, Button):
            # s.action()
            pass
        self.test((s, cell))
        # remove action from possible ones - it is done
        del self.action_types[s]
        if s in self.player.get_hand():
            self.player.remove_from_hand(s)
        # reconstruct values in dictionary of actions
        self.tactic()

    def turn(self):
        """
        Initialize player's hand and actions he can make.
        :return: nothing is returned.
        """
        print self.player.name + '\'s turn!'
        self.turn_num += 1
        self.player.get_tiles(self.turn_num)
        #TODO draw player's hand
        # create dictionary of actions
        self.action_types = {}
        for cell in self.playground.cells:
            if cell.tile is not None and cell.tile.army_id == self.player.army and cell.tile.mobile:
                self.action_types[cell] = []
        for cell in self.player.hand:
            if cell.tile:
                self.action_types[cell] = []
        self.action_types[self.buttons['confirm']] = []
        # fill dictionary values
        self.tactic()

    def tactic(self):
        """
        Constructs values for keys in dictionary of player's actions.
        :return: nothing is returned.
        """
        if self.turn_num > 2 and self.player.tiles_in_hand() == 1:
            # 3d tile in hand needs to be removed
            self.action_types[self.player.get_hand()[0]] = [self.buttons['remove']]
        for action_type in self.action_types:
            if action_type in self.playground.cells:
                # actor is on the battlefield - mobility
                self.action_types[action_type] = action_type.tile.maneuver_rate(action_type)
            elif action_type in self.player.hand:
                # actor is in hand - it can be removed
                self.action_types[action_type] = [self.buttons['remove']]
                if isinstance(action_type.tile, Tile):
                    # this is tile - it can be placed on the battlefield
                    self.action_types[action_type].extend(self.playground.get_free_cells())
                else:
                    # this is order - it can be applied
                    self.action_types[action_type].append(self.buttons['apply'])
        callback = self.callback_dispatcher
        self.pend_click(self.action_types, callback)

    def battle(self):
        """
        Computes units interaction during battle.
        :return: nothing is returned.
        """
        # prepare to battle
        # find max initiative
        max_initiative = 0
        for cell in self.playground.cells:
            if cell.tile is not None and isinstance(cell.tile, Unit) and cell.tile.initiative:
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
        # debug
        self.renderer.idle = False

    EVENT_TICKER = pygame.USEREVENT
    EVENT_USEREVENT = pygame.USEREVENT + 1
    EVENT_MAX = pygame.USEREVENT + 2


if __name__ == "__main__":
    game = GameMode(2)

    # Zq = Player('Zq', 1, 0, game)
    # Zq.army_shuffle()
    #
    # Zq.get_tiles(game.turn_num)
    # Zq.get_tiles(game.turn_num + 1)
    # Zq.get_tiles(game.turn_num + 2)


    outpost_kicker1 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[3, True]])
    outpost_kicker1.active = False
    outpost_kicker2 = Unit(0, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    outpost_hq = Base(0, 5, [1,1,1,1,1,1], [[0, True]], {'initiative': [1,1,0,0,0,1], 'melee': [1,1,0,0,0,1]}, {})
    outpost_mothermodule = Module(0, 1, {'add_attacks': [2,0,0,0,0,0]}, {})
    outpost_medic = Medic(0, 1, [1,1,0,0,0,1])
    moloch_fat = Unit(1, 5, None, None, None, None, None, mobility=True)
    moloch_greaver = Unit(1, 1, (1,0,0,0,0,0), None, None, None, [[4, True]])
    moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
    moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})

    game.playground.cells[0].tile = outpost_kicker1
    game.playground.cells[0].turn = 1
    game.playground.cells[1].tile = moloch_netfighter
    game.playground.cells[1].turn = 3
    game.playground.cells[2].tile = moloch_fat
    game.playground.cells[2].turn = 0
    game.playground.cells[3].tile = moloch_greaver
    game.playground.cells[3].turn = 4
    game.playground.cells[4].tile = outpost_hq
    game.playground.cells[4].turn = 0
    game.playground.cells[5].tile = outpost_mothermodule
    game.playground.cells[5].turn = 1
    game.playground.cells[6].tile = outpost_kicker2
    game.playground.cells[6].turn = 1
    game.playground.cells[13].tile = moloch_hq
    game.playground.cells[13].turn = 0
    game.playground.cells[15].tile = outpost_medic
    game.playground.cells[15].turn = 0

    game.start_game()
    
