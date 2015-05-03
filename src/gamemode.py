__author__ = 'zheneq & dandelion'

import pygame
import math

from grid import Grid, Cell, Button
from tile import *
from renderer import Renderer
from player import Player

from game.battle.battle import Battle


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
        self.rot_pending = None
        self.renderer = Renderer(self)
        self.playground = Grid(self, grid_radius)
        self.turn_num = 0
        # DEBUG
        self.buttons = {'remove': Button(self, None, 0, 550, .1), 'apply': Button(self, None, 50, 550, .1),
                        'confirm': Button(self, None, 100, 550, .1)}

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
                if event.type == pygame.QUIT:
                    self.active = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    print "Click!"
                    clicked = self.locate(event.pos)
                    for c in clicked:
                        if isinstance(c, Cell) and isinstance(c.tile, Tile):
                            print "\t" + str(type(c.tile)) + " " + str(c.tile.hp)
                        else:
                            print "\t" + "None"
                    if clicked:
                        self.select(clicked)
                if self.rot_pending and event.type == pygame.MOUSEMOTION:
                    self.rotate_tile(event.pos)
                if event.type == self.EVENT_USEREVENT:
                    if event.parameters:
                        event.callback(event.parameters)
                    else:
                        event.callback()
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

    def swap(self, (a, b)):
        print "test"
        if b:
            # release units disabled by nets of a.tile (if there are)
            self.release_disable_units(a)
            # move tile from a to b
            a.tile, b.tile = b.tile, a.tile
            a.turn, b.turn = 0, a.turn
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

        self.buttons['remove'].action = self.remove_tile_from_hand
        self.buttons['apply'].action = self.resolve_order
        self.buttons['confirm'].action = self.new_turn

        self.place_all_hq()
        # self.turn()

    def tick(self, deltatime):
        """
        Subroutine executed every tick.
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        pass

    def add_actor(self, actor):
        self.actors.append(actor)

    def set_timer(self, time, callback, repeat=False):
        """
        Set a timer.
        :param time: Time in milliseconds. If 0, timer is unset
        :param callback: Function to call when the timer is fired
        :param repeat: Bool flag set when timer should be fired repeatedly
        :return: nothing is returned.
        """
        # COMMENT: Several timers may be set for one callback. When unsetting a timer with this function,
        # which one will be unset is unknown.
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

    def event(self, callback, parameters=()):
        pygame.event.post(pygame.event.Event(self.EVENT_USEREVENT, {"callback": callback, "parameters": parameters}))

    def pend_click(self, cells, callback):
        self.rot_pending = None
        self.click_pending = cells
        self.click_callback = callback

    def pend_rotation(self, cell, callback):
        self.click_pending = None
        self.rot_pending = cell
        self.click_callback = callback

    def rotate_tile(self, mousepos):
        x = self.rot_pending.maskrect.center[0] - mousepos[0]
        y = self.rot_pending.maskrect.center[1] - mousepos[1]
        self.rot_pending.turn = int(math.floor(11 + math.atan2(y, x) * 3 / math.pi)) % 6

    def locate(self, pos):
        result = []
        for obj in self.actors:
            try:
                if obj.mask.get_at((pos[0] - obj.maskrect.left, pos[1] - obj.maskrect.top)):
                    result.append(obj)
            except IndexError:
                pass
        return result

    def release_disable_units(self, cell):
        if isinstance(cell.tile, Unit) and cell.tile.nets:
            for ind in xrange(len(cell.neighbours)):
                if cell.tile.nets[(ind + 6 - cell.turn) % 6] and \
                                cell.neighbours[ind] is not None and \
                                cell.neighbours[ind].tile is not None and \
                                cell.neighbours[ind].tile.army_id != cell.tile.army_id:
                    # release unit if there is no other net fighters
                    neighbour = cell.neighbours[ind]
                    for ind in xrange(len(neighbour.neighbours)):
                        if cell.neighbours[ind] is not None and \
                                        cell.neighbours[ind].tile is not None and \
                                        cell.neighbours[ind].tile.army_id != cell.tile.army_id and \
                                isinstance(cell.neighbours[ind].tile, Unit) and \
                                cell.neighbours[ind].tile.nets and \
                                cell.neighbours[ind].tile.nets[(ind + 9 - cell.turn) % 6]:
                            break
                    else:
                        neighbour.tile.active = True

    def disable_units(self, cell):
        if isinstance(cell.tile, Unit) and cell.tile.active and cell.tile.nets:
            for ind in xrange(len(cell.neighbours)):
                if cell.tile.nets[(ind + 6 - cell.turn) % 6] and \
                                cell.neighbours[ind] is not None and \
                                cell.neighbours[ind].tile is not None and \
                                cell.neighbours[ind].tile.army_id != cell.tile.army_id:
                    # disable unit
                    cell.neighbours[ind].tile.active = False

    def resolve_order(self, order):
        if order.type == 'battle':
            self.begin_battle()
        elif order.type == 'airstrike':
            self.begin_airstrike()
        elif order.type == 'grenade':
            self.begin_grenade()
        elif order.type == 'move':
            self.begin_march()
        elif order.type == 'pushback':
            self.begin_pushback()

    def begin_airstrike(self):
        targets = {}
        for cell in self.playground.cells:
            if None not in cell.neighbours:
                targets[cell] = []
        self.pend_click(targets, self.airstrike)

    def airstrike(self, (target, empty)):
        base_cell = None
        for cell in self.playground.cells:
            if cell.tile is not None and cell.tile.army_id == self.player.army and isinstance(cell.tile, Base):
                base_cell = cell
                break
        if target.tile is not None and not isinstance(target.tile, Base):
            target.tile.taken_damage.append({'value': 1, 'type': 'pure', 'instigator': base_cell})
        for cell in target.neighbours:
            if cell.tile is not None and not isinstance(cell.tile, Base):
                cell.tile.taken_damage.append({'value': 1, 'type': 'pure', 'instigator': base_cell})
        battle = Battle(self.playground,
                        self.pend_click,
                        self.buttons,
                        self.release_disable_units,
                        self.event,
                        self.set_timer,
                        2000,
                        self.renderer,
                        self.tactic,
                        init_phase=0)
        self.set_timer(2000, battle.take_damage_phase)

    def begin_grenade(self):
        targets = {}
        for cell in self.playground.cells:
            if cell.tile is not None and \
                        isinstance(cell.tile, Base) and \
                        cell.tile.army_id == self.player.army and \
                        cell.tile.active:
                for neighbour in cell.neighbours:
                    if neighbour is not None and \
                                neighbour.tile is not None and \
                                neighbour.tile.army_id != self.player.army and \
                                not isinstance(neighbour.tile, Base):
                        targets[neighbour] = []
        self.pend_click(targets, self.grenade)

    def grenade(self, (target, empty)):
        self.release_disable_units(target)
        target.tile = None
        self.event(self.tactic)

    def begin_pushback(self):
        pushes = {}
        for cell in self.playground.cells:
            if cell.tile is not None and cell.tile.active and cell.tile.army_id == self.player.army:
                # if there is unit to push back we add cell in actions dictionary
                enemies = []
                for ind in xrange(len(cell.neighbours)):
                    neighbour = cell.neighbours[ind]
                    if neighbour is not None and \
                                    neighbour.tile is not None and \
                            neighbour.tile.active and \
                                    neighbour.tile.army_id != self.player.army:
                        # neighbour is enemy tile
                        for retreat_ind in xrange(ind + 5, ind + 8):
                            if neighbour.neighbours[retreat_ind % 6] is not None and \
                                            neighbour.neighbours[retreat_ind % 6].tile is None:
                                # neighbour tile can retreat here
                                enemies.append(neighbour)
                                break
                if enemies:
                    pushes[cell] = enemies
        if pushes:
            self.pend_click(pushes, self.pushback)
        else:
            self.event(self.tactic)

    def pushback(self, (who, whom)):
        retreat_ways = []
        ind = who.neighbours.index(whom)
        for retreat_ind in xrange(ind + 5, ind + 8):
            if whom.neighbours[retreat_ind % 6] is not None and \
                            whom.neighbours[retreat_ind % 6].tile is None:
                # whom tile can retreat here
                retreat_ways.append(whom.neighbours[retreat_ind % 6])
        possible_retreats = {whom: retreat_ways}
        self.pend_click(possible_retreats, self.retreat)

    def retreat(self, (who, where)):
        self.swap((who, where))
        self.event(self.tactic)

    def begin_march(self):
        maneuvers = {}
        for cell in self.playground.cells:
            if cell.tile is not None and cell.tile.active and cell.tile.army_id == self.player.army:
                maneuvers[cell] = cell.tile.maneuver_rate(cell)
        if maneuvers:
            self.pend_click(maneuvers, self.march)
        else:
            self.event(self.tactic)

    def march(self, (who, where)):
        if who in self.action_types and who is not where:
            # move mobile unit - change cell in dictionary
            values = self.action_types[who]
            del self.action_types[who]
            self.action_types[where] = values
        self.swap((who, where))
        self.pend_rotation(where, self.tactic)

    def remove_tile_from_hand(self, tile):
        self.player.remove_in_turn = True
        self.action_types[self.buttons['confirm']] = []
        self.event(self.tactic)

    def new_turn(self):
        self.player = self.player.next
        self.event(self.turn)

    def select(self, cells):
        """
        Common interface of selecting.
        :param cells: cells clicked by player.
        :return: nothing is returned.
        """
        if self.rot_pending:
            self.rot_pending = None
            self.event(self.click_callback)
        else:
            for cell in cells:
                if self.click_selected is not None:
                    # there is tile from dictionary selected by previous click
                    if cell in self.click_pending[self.click_selected]:
                        # there is pair (source, dist) of action
                        self.event(self.click_callback, (self.click_selected, cell))
                        # reset selection dictionary
                        self.click_selected = None
                        self.click_pending = {}
                        break
                if cell in self.click_pending:
                    # if player doesn't need to select second actor
                    if not self.click_pending[cell]:
                        self.event(self.click_callback, (cell, None))
                        self.click_selected = None
                        self.click_pending = {}
                    else:
                        self.click_selected = cell
                    break

    def callback_dispatcher(self, (s, cell)):
        # DEBUG
        if isinstance(s, Button):
            if s is self.buttons['confirm']:
                if self.turn_num > 2 and not self.player.remove_in_turn:
                    # must remove one first
                    print 'You must remove one tile from hand first!'
                    self.event(self.tactic)
                else:
                    s.action()
            else:
                # unlucky draw
                self.player.refresh_hand()
                self.event(self.tactic)
        elif isinstance(s, Cell):
            # remove action from possible ones - it is done
            if isinstance(s.tile, Order) and \
                            s.tile.type is 'battle' and \
                            cell is self.buttons['apply'] and \
                            not self.player.remove_in_turn:
                # must remove one before battle start
                print 'You must remove one tile from hand first!'
                self.event(self.tactic)
            else:
                del self.action_types[s]
                tile = s.tile
                if isinstance(cell, Button):
                    # apply/remove
                    self.player.remove_from_hand(tile)
                    cell.action(tile)
                    return
                else:
                    # marsh/mobility resolve
                    self.march((s, cell))

    def place_hq(self, (who, where)):
        self.swap((who, where))
        self.event(self.next_hq)

    def next_hq(self):
        self.player = self.player.next
        if self.player is self.players[0]:
            self.event(self.turn)
        else:
            self.event(self.place_all_hq)

    def place_all_hq(self):
        print self.player.name + '\'s turn!'
        self.player.hand[0].tile = self.player.hq
        self.action_types = {self.player.hand[0]: self.playground.get_free_cells()}
        self.pend_click(self.action_types, self.place_hq)

    def turn(self):
        """
        Initialize player's hand and actions he can make.
        :return: nothing is returned.
        """
        for player in self.players:
            if player.hq is None:
                print player.name + '\'s HQ is destroyed'
                print 'Congratulations,', player.next.name + '!!!'
                self.set_timer(3000, self.end_game)
                return
        print self.player.name + '\'s turn!'
        self.turn_num += 1
        self.player.get_tiles(self.turn_num)
        self.player.remove_in_turn = False
        if self.player.tiles_in_hand() < 3:
            self.player.remove_in_turn = True
        # create dictionary of actions
        self.action_types = {}
        for cell in self.playground.cells:
            if cell.tile is not None and \
                    cell.tile.active and \
                    cell.tile.army_id == self.player.army and \
                    cell.tile.mobile:
                self.action_types[cell] = []
        for cell in self.player.hand:
            if cell.tile:
                self.action_types[cell] = []
        if self.player.remove_in_turn:
            self.action_types[self.buttons['confirm']] = []
        # fill dictionary values
        self.tactic()

    def tactic(self):
        """
        Constructs values for keys in dictionary of player's actions.
        :return: nothing is returned.
        """
        # if all battlefield is full begin the battle
        if not self.playground.get_free_cells():
            self.begin_battle()
            return
        for cell in self.playground.cells:
            self.disable_units(cell)
        if self.turn_num > 2 and \
                isinstance(self.player.hand[0].tile, Order) and \
                isinstance(self.player.hand[1].tile, Order) and \
                isinstance(self.player.hand[2].tile, Order):
            # unlucky draw
            self.action_types[self.buttons['remove']] = []
        elif self.buttons['remove'] in self.action_types:
            del self.action_types[self.buttons['remove']]
        for action_type in self.action_types:
            if action_type in self.playground.cells:
                # actor is on the battlefield - mobility
                self.action_types[action_type] = action_type.tile.maneuver_rate(action_type)
            elif action_type in self.player.hand:
                # actor is in hand - it can be removed
                self.action_types[action_type] = [self.buttons['remove']]
                if isinstance(action_type.tile, Tile) and \
                            (len(self.playground.get_free_cells()) > 1 or self.player.remove_in_turn):
                    # this is tile - it can be placed on the battlefield
                    # placing new tile on the playground won't start the battle
                    self.action_types[action_type].extend(self.playground.get_free_cells())
                elif isinstance(action_type.tile, Order) and \
                            (action_type.tile.type != 'battle' or self.player.remove_in_turn):
                    # this is order - it can be applied
                    self.action_types[action_type].append(self.buttons['apply'])
        if self.turn_num > 2 and not self.player.remove_in_turn and self.player.tiles_in_hand() == 1:
            # 3rd tile in hand needs to be removed
            self.action_types[self.player.get_hand()[0]] = [self.buttons['remove']]
        self.pend_click(self.action_types, self.callback_dispatcher)

    def begin_battle(self, period=3000):
        """
        Computes units interaction during battle.
        :return: nothing is returned.
        """
        # prepare to battle
        # find max initiative
        # battle
        battle = Battle(self.playground,
                        self.pend_click,
                        self.buttons,
                        self.release_disable_units,
                        self.event,
                        self.set_timer,
                        period,
                        self.renderer,
                        self.new_turn)
        self.set_timer(period, battle.battle_phase)

    EVENT_TICKER = pygame.USEREVENT
    EVENT_USEREVENT = pygame.USEREVENT + 1
    EVENT_MAX = pygame.USEREVENT + 2


if __name__ == "__main__":
    game = GameMode(2)

    # moloch_medic1 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_medic2 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_medic3 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_medic4 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_medic5 = Medic(1, 1, [1, 1, 0, 0, 0, 1])
    # moloch_fat = Unit(1, 5, None, None, None, None, None, mobility=True)
    # moloch_greaver1 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # moloch_greaver2 = Unit(1, 1, (1, 0, 0, 0, 0, 0), None, None, None, [[2, True]], mobility=True)
    # borgo_fighter1 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # borgo_fighter2 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # borgo_fighter3 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # borgo_fighter4 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # borgo_fighter5 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # borgo_fighter6 = Unit(2, 1, 'fighter', (1, 1, 0, 0, 0, 0), None, None, None, [[1, True]])
    # moloch_netfighter = Unit(1, 1, None, None, None, [1,1,0,0,0,0], [[0, True]])
    # moloch_hq = Base(1, 5, [1,1,1,1,1,1], [[0, True]], {}, {})
    #
    # game.playground.cells[1].tile = borgo_fighter1
    # game.playground.cells[1].turn = 1
    # game.playground.cells[2].tile = borgo_fighter2
    # game.playground.cells[2].turn = 1
    # game.playground.cells[3].tile = borgo_fighter3
    # game.playground.cells[3].turn = 1
    # game.playground.cells[4].tile = borgo_fighter4
    # game.playground.cells[4].turn = 1
    # game.playground.cells[5].tile = borgo_fighter5
    # game.playground.cells[5].turn = 1
    # game.playground.cells[6].tile = borgo_fighter6
    # game.playground.cells[6].turn = 1

    game.start_game()

