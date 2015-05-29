__author__ = 'zheneq & dandelion'

import pygame
from copy import copy

from src.game.common.clicker import Clicker
from src.game.common.grid import Grid, Cell, Button
from src.game.common.tile import *
from src.game.common.renderer import Renderer
from src.game.common.player import Player
from src.game.common.buffs import compute_mobility

from src.game.battle.battle import Battle

from src.game.tactic.orderhandler import OrderHandler


class GameMode(object):
    """
    Main game class. Controls game process.
    """
    EVENT_TICKER = pygame.USEREVENT
    EVENT_USEREVENT = pygame.USEREVENT + 1
    EVENT_MAX = pygame.USEREVENT + 2

    def __init__(self, renderer):
        self.active = False
        self.timers = {}
        self.clicker = Clicker(self)
        self.renderer = renderer(self)

    def start_game(self, start, args, kwargs, interaction=True):
        """
        Launches the main cycle.
        :return: nothing is returned.
        """
        pygame.init()
        self.active = True
        self.begin_play(start, args, kwargs)
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
                if interaction:
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.clicker.parse(event.pos)
                    if event.type == pygame.MOUSEMOTION:
                        self.clicker.parse_rot(event.pos)
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
            if interaction:
                self.renderer.tick(deltatime)
        # unintialization
        pygame.quit()

    def end_game(self):
        """
        Immediately stops the game.
        :return: nothing is returned.
        """
        self.active = False

    def begin_play(self, start, args, kwargs):
        pass

    def tick(self, deltatime):
        """
        Subroutine executed every tick.
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        pass

    def event(self, callback, parameters=()):
        pygame.event.post(pygame.event.Event(self.EVENT_USEREVENT, {"callback": callback, "parameters": parameters}))

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


class Neuroshima(GameMode):
    """
    Main game class. Controls game process.
    """

    def __init__(self, grid_radius):
        """
        Initializes necessary data.
        :param grid_radius: radius of battlefield.
        :return: nothing is returned.
        """
        GameMode.__init__(self, Renderer)
        self.players = []
        self.player = None
        self.last_player = None
        self.playground = Grid(self, grid_radius)
        self.turn_num = 0
        self.over = False

        self.playground_save = []
        self.player_hand_save = []

        self.action_types = {}
        self.orderhandler = OrderHandler(self)
        # DEBUG
        self.buttons = {'remove': Button(self, self.remove_tile_from_hand, 0, 515, .25, 'remove'),
                        'apply': Button(self, self.orderhandler.resolve_order, 120, 515, .25, 'apply'),
                        'revoke': Button(self, self.load, 240, 515, .25, 'revoke'),
                        'confirm': Button(self, self.new_turn, 360, 515, .25, 'confirm')}

    def start_game(self, start, args, kwargs, test_actions=None):
        if test_actions:
            self.clicker.test(test_actions)
            GameMode.start_game(self, start, args, kwargs, interaction=False)
        else:
            GameMode.start_game(self, start, args, kwargs)

    def begin_play(self, start, args, kwargs):
        GameMode.begin_play(self, start, args, kwargs)
        # DEBUG
        Zq = Player('Player1', 1, 0, self)
        Zq.army_shuffle()
        Dand = Player('Player2', 3, 1, self)
        Dand.army_shuffle()
        self.players = [Zq, Dand]
        self.players[0].next = self.players[1]
        self.players[1].next = self.players[0]
        self.player = self.players[0]

        start(*args, **kwargs)
        # self.turn()

    def swap(self, (a, b)):
        if b:
            # release units disabled by nets of a.tile (if there are)
            self.release_disable_units(a)
            # move tile from a to b
            a.tile, b.tile = b.tile, a.tile
        else:
            print "b is none"

    def march(self, (who, where)):
        if who in self.action_types and who is not where:
            # move mobile unit - change cell in dictionary
            values = self.action_types[who]
            del self.action_types[who]
            self.action_types[where] = values
        if who in self.player.hand:
            # placing tile on board
            print '\t' + self.player.name, 'places', who.tile.hex.name, \
                'to the', str(self.playground.cells.index(where)), 'cell'
        else:
            # moving mobile units
            print '\t' + self.player.name, 'moves', who.tile.hex.name, \
                'to the', str(self.playground.cells.index(where)), 'cell'
        self.swap((who, where))
        self.clicker.pend_rotation(where, self.tactic)

    def begin_battle(self, continuer='default', period=3000):
        """
        Computes units interaction during battle.
        :return: nothing is returned.
        """
        # prepare to battle
        # find max initiative
        # battle
        if continuer is 'default':
            continuer = self.new_turn
        battle = Battle(self.playground,
                        self.clicker.pend_click,
                        self.buttons,
                        self.release_disable_units,
                        self.event,
                        self.set_timer,
                        period,
                        continuer)
        self.set_timer(period, battle.battle_phase)

    def release_disable_units(self, cell):
        if isinstance(cell.tile.hex, Unit) and cell.tile.hex.nets:
            for ind in xrange(len(cell.neighbours)):
                if cell.tile.hex.nets[(ind + 6 - cell.tile.turn) % 6] and \
                        cell.neighbours[ind] is not None and \
                        cell.neighbours[ind].tile is not None and \
                        cell.neighbours[ind].tile.hex.army_id != cell.tile.hex.army_id:
                    # release unit if there is no other net fighters
                    neighbour = cell.neighbours[ind]
                    for ind in xrange(len(neighbour.neighbours)):
                        if cell.neighbours[ind] is not None and \
                                    cell.neighbours[ind].tile is not None and \
                                    cell.neighbours[ind].tile.hex.army_id != cell.tile.hex.army_id and \
                                isinstance(cell.neighbours[ind].tile.hex, Unit) and \
                                cell.neighbours[ind].tile.hex.nets and \
                                cell.neighbours[ind].tile.hex.nets[(ind + 9 - cell.tile.turn) % 6]:
                            break
                    else:
                        neighbour.tile.active = True

    def disable_units(self, cell):
        if cell.tile and isinstance(cell.tile.hex, Unit) and cell.tile.active and cell.tile.hex.nets:
            for ind in xrange(len(cell.neighbours)):
                if cell.tile.hex.nets[(ind + 6 - cell.tile.turn) % 6] and \
                        cell.neighbours[ind] is not None and \
                        cell.neighbours[ind].tile is not None and \
                        cell.neighbours[ind].tile.hex.army_id != cell.tile.hex.army_id and \
                        not (isinstance(cell.neighbours[ind].tile.hex, Unit) and
                             cell.neighbours[ind].tile.hex.nets and
                             cell.neighbours[ind].tile.hex.nets[(ind + 9 - cell.neighbours[ind].tile.turn) % 6]):
                    # disable unit
                    cell.neighbours[ind].tile.active = False

    def remove_tile_from_hand(self, tile):
        name = ''
        if isinstance(tile, Order):
            name = tile.type
        else:
            name = tile.name
        print '\t' + self.player.name, 'removed', name, 'from his hand'
        self.player.remove_in_turn = True
        self.action_types[self.buttons['confirm']] = []
        self.event(self.tactic)

    def new_turn(self):
        for cell in self.playground.cells:
            # reset disposable modules
            if cell.tile is not None and isinstance(cell.tile.hex, DisposableModule):
                cell.tile.used = []
        self.player = self.player.next
        self.event(self.turn)

    def callback_dispatcher(self, (s, cell)):
        if isinstance(s, Button):
            if s is self.buttons['confirm'] or s is self.buttons['revoke']:
                s.action()
            else:
                # unlucky draw
                print '\t' + self.player.name, 'refreshed hand.'
                self.player.refresh_hand()
                self.save()
                self.event(self.tactic)
        elif isinstance(s, Cell):
            # remove action from possible ones - it is done
            if not (isinstance(s.tile.hex, Order) and s.tile.hex.type is 'battle' and \
                    cell is self.buttons['apply'] and not self.player.remove_in_turn):
                del self.action_types[s]
                tile = s.tile
                if isinstance(cell, Button):
                    # remove or apply (order)
                    self.player.remove_from_hand(tile)
                    cell.action(tile.hex)
                    return
                else:
                    # marsh/mobility resolve
                    if s in self.playground.cells:
                        # mobility resolve - decrease tile's mobility
                        s.tile.mobility -= 1
                    self.march((s, cell))

    def place_hq(self, (who, where)):
        self.march((who, where))
        self.next_hq()

    def next_hq(self):
        self.player = self.player.next
        if self.player is self.players[0]:
            self.turn()
        else:
            self.place_all_hq()

    def place_all_hq(self):
        print self.player.name + ', please, place your HQ on the board.'
        self.player.hand[0].tile = self.player.hq
        self.action_types = {self.player.hand[0]: self.playground.get_free_cells()}
        self.clicker.pend_click(self.action_types, self.place_hq)

    def save(self):
        self.playground_save = [copy(cell.tile) for cell in self.playground.cells]
        self.player_hand_save = [copy(cell.tile) for cell in self.player.hand]

    def load(self):
        print '\t' + self.player.name, 'revokes his actions.'
        for cell, cell_save in zip(self.playground.cells, self.playground_save):
            cell.tile = cell_save
            if cell.tile and isinstance(cell.tile.hex, Base) and cell.tile.hex.army_id == self.player.army:
                self.player.hq = cell.tile
        for cell, cell_save in zip(self.player.hand, self.player_hand_save):
            cell.tile = cell_save
        self.turn_init()

    def turn(self):
        """
        Initialize player's hand and actions he can make.
        :return: nothing is returned.
        """
        for player in self.players:
            if player.hq.hex.hp <= player.hq.injuries:
                print player.name + '\'s HQ is destroyed.'
                print 'Congratulations,', player.next.name + '!!!'
                self.set_timer(3000, self.end_game)
                return
        if self.over:
            print self.player.name + '\'s HQ:', self.player.hq.hex.hp - self.player.hq.injuries
            print self.player.next.name + '\'s HQ:', self.player.next.hq.hex.hp - self.player.next.hq.injuries
            if self.player.hq.hex.hp - self.player.hq.injuries < self.player.next.hq.hex.hp - self.player.next.hq.injuries:
                print self.player.name + '\'s HQ is more damaged'
                print 'Congratulations,', self.player.next.name + '!!!'
                self.set_timer(3000, self.end_game)
                return
            elif self.player.hq.hex.hp - self.player.hq.injuries > self.player.next.hq.hex.hp - self.player.next.hq.injuries:
                print self.player.next.name + '\'s HQ is more damaged'
                print 'Congratulations,', self.player.name + '!!!'
                self.set_timer(3000, self.end_game)
                return
            else:
                # TODO implement additional turn
                print 'Both HQs are equally damaged'
                print 'That\'s a draw('
                self.set_timer(3000, self.end_game)
                return
        if self.last_player and self.last_player is self.player:
            # Final Battle
            print 'The Final Battle begins!'
            self.over = True
            self.begin_battle()
            return
        print self.player.name + '\'s turn!'
        self.turn_num += 1
        self.player.get_tiles(self.turn_num)
        self.save()
        self.turn_init()

    def turn_init(self):
        # Input when revoking
        self.player.remove_in_turn = False
        if self.turn_num < 3 or self.player.tiles_in_hand() < 3:
            self.player.remove_in_turn = True

        #TODO DEBUG
        # self.player.hand[0].tile = TileOnBoard(Order(self.player.army, 'move'), 0)
        # self.player.hand[1].tile = TileOnBoard(Order(self.player.army, 'move'), 0)
        # self.player.hand[2].tile = TileOnBoard(Order(self.player.army, 'move'), 0)

        # reset units' support info
        for cell in self.playground.cells:
            # reset mobility
            if cell.tile is not None and cell.tile.hex.army_id == self.player.army:
                cell.tile.mobility = cell.tile.hex.default_mobility
        # create dictionary of actions
        self.action_types = {}
        for cell in self.player.hand:
            if cell.tile:
                self.action_types[cell] = []

        #TODO DEBUG
        self.action_types[self.buttons['revoke']] = []

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
            for cell in self.playground.cells:
                # if 'cell' is netfighter disable enemies 'cell'
                self.disable_units(cell)
            self.begin_battle()
            return
        for cell in self.playground.cells:
            # if 'cell' is netfighter disable enemies 'cell'
            self.disable_units(cell)
            if cell.tile is not None and cell.tile.hex.army_id == self.player.army:
                # if 'cell' is near transport increase 'cell' mobility
                cell.tile.mobility += compute_mobility(cell)
                # if unit is mobile add action
                if cell.tile.active and not cell.tile.hex.immovable and cell.tile.mobility > 0:
                    self.action_types[cell] = []
        if self.player.tiles_in_hand() == 3 and \
                isinstance(self.player.hand[0].tile.hex, Order) and \
                isinstance(self.player.hand[1].tile.hex, Order) and \
                isinstance(self.player.hand[2].tile.hex, Order):
            # unlucky draw
            self.action_types[self.buttons['remove']] = []
        elif self.buttons['remove'] in self.action_types:
            del self.action_types[self.buttons['remove']]
        if not self.last_player and not self.player.tiles:
            # deck is over - last actions before the Final Battle
            self.last_player = self.player
        for action_type in self.action_types:
            if action_type in self.playground.cells:
                # actor is on the battlefield - mobility
                self.action_types[action_type] = action_type.tile.maneuver_rate(action_type)
            elif action_type in self.player.hand:
                # actor is in hand - it can be removed
                self.action_types[action_type] = [self.buttons['remove']]
                if isinstance(action_type.tile.hex, Tile) and \
                        (len(self.playground.get_free_cells()) > 1 or self.player.remove_in_turn):
                    # this is tile - it can be placed on the battlefield
                    # placing new tile on the playground won't start the battle
                    self.action_types[action_type].extend(self.playground.get_free_cells())
                elif isinstance(action_type.tile.hex, Order) and \
                        (action_type.tile.hex.type != 'battle' or self.player.remove_in_turn and not self.last_player):
                    # this is order - it can be applied
                    self.action_types[action_type].append(self.buttons['apply'])
        if self.turn_num > 2 and not self.player.remove_in_turn and self.player.tiles_in_hand() == 1:
            # 3rd tile in hand needs to be removed
            self.action_types[self.player.get_hand()[0]] = [self.buttons['remove']]
        self.clicker.pend_click(self.action_types, self.callback_dispatcher)


if __name__ == "__main__":
    pass