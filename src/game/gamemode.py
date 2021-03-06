__author__ = 'zheneq & dandelion'

import pygame
from copy import copy
import os
import sys
import gettext

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
    Main class of abstract board game. Controls game process.
    """

    EVENT_TICKER = pygame.USEREVENT
    EVENT_USEREVENT = pygame.USEREVENT + 1
    EVENT_MAX = pygame.USEREVENT + 2

    def __init__(self, renderer):
        self.active = False
        self.timers = {}

        bindir = os.path.dirname(os.path.realpath(sys.argv[0]))
        for localedir in os.path.join(bindir, 'loc'), None:
            localefile = gettext.find('game', localedir)
            if localefile:
                break
        gettext.install('game', localedir, names=("ngettext",))

        self.clicker = Clicker(self)
        self.renderer = renderer(self)

    def start_game(self, start, args, kwargs, interaction=True):
        """Starts board game main loop.
        Initializes PyGame structures, then initializes game values (:py:meth:`begin_play()`) and enters the game loop.

        :param function start: Function that begins game after initialization in :py:meth:`begin_play()`
        :param list args: Arguments for function *start()* given as first parameter
        :param dict kwargs: Key word arguments for function *start()* given as first parameter
        :param bool interaction: Whether game is interactive or not. Needs for test reasons.

        In main loop different game events are caught and handled (such as :py:attr:`PyGame.MOUSEBUTTONUP` or
        :py:attr:`PyGame.USEREVENT`). Mouse events are used for players' actions handling while others are used for
        drawing gameboard and performing game logic. Game ends when either game logic finishes or event
        :py:attr:`PyGame.QUIT` happens.
        """
        pygame.init()
        self.active = True
        self.begin_play(start, args, kwargs)
        pygame.time.set_timer(self.EVENT_TICKER, 50)
        time = pygame.time.get_ticks()
        while self.active:
            prevtime = time
            time = pygame.time.get_ticks()
            pygame.event.pump()
            events = [pygame.event.wait()]
            events.extend(pygame.event.get())
            # processing events
            for event in events:
                if event.type == pygame.QUIT:
                    self.active = False
                if interaction:
                    # All user actions embodying game process
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.clicker.parse(event.pos)
                    if event.type == pygame.MOUSEMOTION:
                        # uses in rotation
                        self.clicker.parse_rot(event.pos)
                # common event type. Used for game logic and drawing gameboard
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
        pygame.quit()

    def end_game(self):
        """Immediately stops the game."""
        self.active = False

    def begin_play(self, start, args, kwargs):
        """Initializes abstract game values.
        Sets game values (such as players' info), then starts the game. Must be overridden in particular game.

        :param function start: Function that begins game after initialization
        :param list args: Arguments for function *start()* given as first parameter
        :param dict kwargs: Key word arguments for function *start()* given as first parameter
        """
        pass

    def tick(self, deltatime):
        """Game tick.
        Subroutine executed every tick.

        :param deltatime: Time since last tick (in milliseconds)
        """
        pass

    def event(self, callback, parameters=()):
        """Creates game event.
        Created events will be handeled in main loop of :py:meth:`start_game()`

        :param function callback: Callback for event
        :param tuple parameters: Tuple of parameters for *callback()* given as first parameter
        """
        pygame.event.post(pygame.event.Event(self.EVENT_USEREVENT, {"callback": callback, "parameters": parameters}))

    def set_timer(self, time, callback, repeat=False):
        """Sets a timer.

        :param int time: Time in milliseconds. If 0, timer is unset
        :param function callback: Function to call when the timer is fired
        :param bool repeat: Bool flag set when timer should be fired repeatedly

        Game rises `callback()` event every `time` milliseconds. If `repeat` is ``False``, the event is risen only once.
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
    Main Neuroshima Hex game class. Controls game process.
    """

    def __init__(self, grid_radius):
        GameMode.__init__(self, Renderer)
        self.players = []
        self.player = None
        self.last_player = None
        self.playground = Grid(self, grid_radius)
        self.turn_num = 0
        self.over = False
        self.battle = None

        self.playground_save = []
        self.player_hand_save = []

        self.action_types = {}
        self.orderhandler = OrderHandler(self)
        # DEBUG
        self.buttons = {'remove': Button(self, self.remove_tile_from_hand, 75, 450, .3, 'remove'),
                        'apply': Button(self, self.orderhandler.resolve_order, 275, 450, .3, 'apply'),
                        'revoke': Button(self, self.load, 75, 615, .3, 'revoke'),
                        'confirm': Button(self, self.new_turn, 275, 615, .3, 'confirm')}

    def start_game(self, start, args, kwargs, test_actions=None):
        """Starts Neuroshima Hex main loop.
        Overridden base method :py:meth:`GameMode.start_game()`. Added test mode.

        :param function start: Function that begins game after initialization in :py:meth
        :param list args: Arguments for function *start()* given as first parameter
        :param dict kwargs: Key word arguments for function *start()* given as first parameter
        :param list test_actions: List of emulated players actions during the whole game. Used for testing

        Optional `test_actions` is a list of distinct players' actions. Each player's action is a list of actors that
        player has selected to perform one action in game logic. For example, placing tile from hand to board needs
        pressing on 2 actors: cell with tile on hand and free cell in the board. So, player actions will look like
        `[hand_cell, free_board_cell]`

        If `test_actions` is not ``None``, interaction with players is disabled because there are emulated actions.
        """
        if test_actions:
            self.clicker.test(test_actions)
            GameMode.start_game(self, start, args, kwargs, interaction=False)
        else:
            GameMode.start_game(self, start, args, kwargs)

    def begin_play(self, start, args, kwargs):
        """Initializes Neuroshima Hex main info.
        Overridden base method :py:meth:`GameMode.begin_play()`.
        Initializes players names and armies, order of turns. After that starts game.

        :param function start: Function that begins game after initialization in :py:meth
        :param list args: Arguments for function *start()* given as first parameter
        :param dict kwargs: Key word arguments for function *start()* given as first parameter

        Function `start()` is the first action in game. It can either be some test function or unique beginning of the
        game process that is described in game rules.

        Standard action starting the game is placing players' HQs on the board (:py:meth:`place_all_hq()`)
        """
        GameMode.begin_play(self, start, args, kwargs)
        self.players = [Player('Moloch', 1, 0, self), Player('Hegemony', 3, 1, self)]
        for p in self.players:
            p.army_shuffle()
        self.players[0].next = self.players[1]
        self.players[1].next = self.players[0]
        self.player = self.players[0]

        start(*args, **kwargs)

    def swap(self, (a, b)):
        """Swaps tiles between cells.

        :param Cell a: one cell
        :param Cell b: another cell
        """
        if b:
            self.release_disable_units(a)
            # move tile from a to b - uses in placing tile on board and/or resolving moving orders
            a.tile, b.tile = b.tile, a.tile
        else:
            print "b is none"

    def march(self, (who, where)):
        """Performs placing tile on board or March order.

        :param Cell who: Old place for tile
        :param Cell where: New place for tile. Must be the same cell as `who` or some free cell.

        Updates action dictionary if `who` is actor and then :py:meth:`swap()` tiles in cells.
        """
        if who in self.action_types and who is not where:
            # move mobile unit - actor in action dict is changed
            # actor cell in dictionary must be updated for further handling actions
            values = self.action_types[who]
            del self.action_types[who]
            self.action_types[where] = values
        if who in self.player.hand:
            # placing tile on board
            print _("\t %(player)s places %(hex)s to cell %(index)d") %\
                  { "player": _(self.player.name),
                    "hex": _(who.tile.hex.name),
                    "index": self.playground.cells.index(where) }
        else:
            # moving mobile units
            print _("\t %(player)s moves %(hex)s to cell %(index)d") %\
                  { "player": _(self.player.name),
                    "hex": _(who.tile.hex.name),
                    "index": self.playground.cells.index(where) }
        self.swap((who, where))
        # link rotation events with rotation callback
        self.clicker.pend_rotation(where, self.tactic)

    def begin_battle(self, continuer='default', period=3000):
        """Computes units interaction during battle.
        Creates instance `Battle()` for battle and launches first battle phase.

        :param function continuer: Function that runs after the end of the battle
        :param int period: Periods between battle phases (in milliseconds)

        Standard`continuer()` is :py:meth:`new_turn()`
        """
        if continuer is 'default':
            continuer = self.new_turn
        self.battle = Battle(self.playground,
                             self.clicker.pend_click,
                             self.buttons,
                             self.release_disable_units,
                             self.event,
                             self.set_timer,
                             period,
                             continuer)
        self.set_timer(period, self.battle.battle_phase)

    def release_disable_units(self, cell):
        """Releases all enemy tiles disabled by the tile in `cell`.

        :param Cell cell: cell with Unit that can use nets

        It's used when the net-unit goes away from `cell` or dies.
        """
        if isinstance(cell.tile.hex, Unit) and cell.tile.hex.nets:
            for ind in xrange(len(cell.neighbours)):
                if cell.tile.hex.nets[(ind + 6 - cell.tile.turn) % 6] and \
                        cell.neighbours[ind] is not None and \
                        cell.neighbours[ind].tile is not None and \
                        cell.neighbours[ind].tile.hex.army_id != cell.tile.hex.army_id:
                    # release unit if there is no other net fighters catching unit
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
        """Disables all enemy units catched by the tile in `cell`.

        :param Cell cell: cell with Unit that can use nets

        It's used when net-unit goes or is plased to the `cell`. Also enemy unit can go under the net-unit's nets.
        """
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
        """Removes tile from player's hand.
        Marks player as returned tile and allows him to finish his turn (nexessary after first and second game turns).

        :param Tile tile: Tile that needs to be removed
        """
        name = ''
        if isinstance(tile, Order):
            name = tile.type
        else:
            name = tile.name
        print _("\t %(player)s removes %(hex)s from his hand") %\
              { 'player': self.player.name,
                'hex': _(name) }
        self.player.remove_in_turn = True
        self.action_types[self.buttons['confirm']] = []
        self.event(self.tactic)

    def new_turn(self):
        """Starts new turn.
        Switches player to the next, resets support info in DisposableModules on the board and starts new turn.
        """
        for cell in self.playground.cells:
            # reset disposable modules
            if cell.tile is not None and isinstance(cell.tile.hex, DisposableModule):
                cell.tile.used = []
        self.player = self.player.next
        self.event(self.turn)

    def callback_dispatcher(self, (s, cell)):
        """Handles common players' choices.
        Specifies callback for every player's choice.

        :param Cell s: Actor
        :param Cell/Button cell: Action
        """
        if isinstance(s, Button):
            if s is self.buttons['confirm'] or s is self.buttons['revoke']:
                s.action()
            else:
                # unlucky draw
                print _("\t %(player)s refreshes his hand.") % { 'player': self.player.name }
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
                        # mobility resolve - decrease tile's mobility - unit made one move action
                        s.tile.mobility -= 1
                    self.march((s, cell))

    def place_hq(self, (who, where)):
        """Places player's HQ to the board.

        :param Cell who: cell on player's hand with HQ
        :param Cell where: Free cell on the board
        """
        self.march((who, where))
        self.next_hq()

    def next_hq(self):
        """Switches to the next player for placing his HQ.
        If all HQ are placed on the board, starts first :py:meth:`turn()`
        """
        self.player = self.player.next
        if self.player is self.players[0]:
            self.turn()
        else:
            self.place_all_hq()

    def place_all_hq(self):
        """Prepares for placing HQ to the board.
        Fills action dictionary with HQs and list of free cells on the board to place them. Then links action dictionary
        with :py:meth:`place_hq()` as callback.
        """
        print _("\t %(player)s , please, place your HQ.") % { 'player': self.player.name }
        self.player.hand[0].tile = self.player.hq
        self.action_types = {self.player.hand[0]: self.playground.get_free_cells()}
        self.clicker.pend_click(self.action_types, self.place_hq)

    def save(self):
        """Saves the board and player;s hand.
        It's used for revoking player's actions in turn.
        """
        self.playground_save = [copy(cell.tile) for cell in self.playground.cells]
        self.player_hand_save = [copy(cell.tile) for cell in self.player.hand]

    def load(self):
        """Loads the board and players's hand.
        It's used in revokes of player's actions during his turn. Also restores pointers to players' HQs.
        After loading begins turn again.
        """
        print _("\t %(player)s revokes his actions.") % { 'player': self.player.name }
        for cell, cell_save in zip(self.playground.cells, self.playground_save):
            cell.tile = copy(cell_save)
            if cell.tile and isinstance(cell.tile.hex, Base) and cell.tile.hex.army_id == self.player.army:
                self.player.hq = cell.tile
            if cell.tile and isinstance(cell.tile.hex, DisposableModule) and cell.tile.hex.army_id == self.player.army:
                # reset disposable module usages
                cell.tile.used = []
        for cell, cell_save in zip(self.player.hand, self.player_hand_save):
            cell.tile = copy(cell_save)
        self.turn_init()

    def turn(self):
        """Starts new turn.
        Check winning conditions, then gives necessary amount of tiles to current player's hand,
        player:py:meth:`save()` game state and initializes player's turn info (:py:meth:`turn_init()`).
        """
        for player in self.players:
            if player.hq.hex.hp <= player.hq.injuries:
                print _("\t %(player)s's HQ is destroyed.") % { 'player': player.name }
                print _("\t Congratulations, %(player)s!") % { 'player':  player.next.name }
                self.set_timer(3000, self.end_game)
                return
        if self.over:
            print _("\t %(player)s's HQ: %(hp)d hp.") %\
                  { 'player': self.player.name,
                    'hp': self.player.hq.hex.hp - self.player.hq.injuries }
            print _("\t %(player)s's HQ: %(hp)d hp.") %\
                  {'player': self.player.next.name,
                   'hp': self.player.next.hq.hex.hp - self.player.next.hq.injuries }
            if self.player.hq.hex.hp - self.player.hq.injuries < self.player.next.hq.hex.hp - self.player.next.hq.injuries:
                print _("\t %(player)s's HQ is more damaged.") % { 'player': self.player.name }
                print _("\t Congratulations, %(player)s!") % { 'player':  self.player.next.name }
                self.set_timer(3000, self.end_game)
                return
            elif self.player.hq.hex.hp - self.player.hq.injuries > self.player.next.hq.hex.hp - self.player.next.hq.injuries:
                print _("\t %(player)s's HQ is more damaged.") % { 'player': self.player.next.name }
                print  _("\t Congratulations, %(player)s!") % { 'player':  self.player.name }
                self.set_timer(3000, self.end_game)
                return
            else:
                # TODO implement additional turn
                print _(" HQs are equally damaged.")
                print _("That\'s a draw(")
                self.set_timer(3000, self.end_game)
                return
        if self.last_player and self.last_player is self.player:
            print _("The Final Battle begins!")
            self.over = True
            self.begin_battle()
            return
        print _("%s's turn!") % self.player.name
        self.turn_num += 1
        self.player.get_tiles(self.turn_num)
        self.save()
        self.turn_init()

    def turn_init(self):
        """Initializes turn info.
        Initializes action dictionary for player and resets tiles' all temporary info to defaults. Then initializes
        values for action dictionary (:py:meth:`tactic()`)
        """
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
        """Initializes values for action dictionary.
        Constructs values for keys in dictionary of player's actions. Then links action dictionary with standard
        :py:meth:`callback_dispatcher()`.
        """
        # if all battlefield is full begin the battle
        if not self.playground.get_free_cells():
            for cell in self.playground.cells:
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