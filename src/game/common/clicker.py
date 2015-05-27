__author__ = 'dandelion'

import math


class Clicker(object):
    """
    Mouse input parser
    """

    def __init__(self, game):
        self.game = game
        self.actors = []
        self.rot_pending = None
        self.click_pending = {}
        self.click_callback = None
        self.click_selected = None

    def test(self, test_actions):
        self.test_actions = test_actions

    def parse(self, pos):
        # print "Click!"
        clicked = self.locate(pos)
        # for c in clicked:
        #     if isinstance(c, Cell) and isinstance(c.tile, Tile):
        #         print "\t" + str(type(c.tile)) + " " + str(c.tile.hp)
        #     else:
        #         print "\t" + "None"
        if clicked:
            self.select(clicked)

    def parse_rot(self, pos):
        if self.rot_pending:
            self.rotate_tile(pos)

    def add_actor(self, actor):
        self.actors.append(actor)

    def pend_click(self, cells, callback):
        self.rot_pending = None
        self.click_pending = cells
        self.click_callback = callback
        if hasattr(self, 'test_actions'):
            # testmode = emulate user actions
            if not self.test_actions:
                raise ValueError('Trouble: test actions are unknown')
            action = self.test_actions[0]
            self.test_actions.remove(action)
            for actor in action:
                self.select([actor])

    def pend_rotation(self, cell, callback):
        self.click_pending = None
        self.rot_pending = cell
        self.click_callback = callback

    def rotate_tile(self, mousepos):
        x = self.rot_pending.maskrect.center[0] - mousepos[0]
        y = self.rot_pending.maskrect.center[1] - mousepos[1]
        self.rot_pending.tile.turn = int(math.floor(11 + math.atan2(y, x) * 3 / math.pi)) % 6

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
        if self.rot_pending:
            print '\twith turn', self.rot_pending.tile.turn
            self.rot_pending = None
            self.game.event(self.click_callback)
        else:
            for cell in cells:
                if self.click_selected is not None:
                    # there is tile from dictionary selected by previous click
                    if cell in self.click_pending[self.click_selected]:
                        # there is pair (source, dist) of action
                        self.game.event(self.click_callback, (self.click_selected, cell))
                        # reset selection dictionary
                        self.click_selected = None
                        self.click_pending = {}
                        break
                if self.click_pending and cell in self.click_pending:
                    # if player doesn't need to select second actor
                    if not self.click_pending[cell]:
                        self.game.event(self.click_callback, (cell, None))
                        self.click_selected = None
                        self.click_pending = {}
                    else:
                        self.click_selected = cell
                    break
