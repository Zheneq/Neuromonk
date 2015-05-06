__author__ = 'Zheneq'
import pygame

from src.game.common.tile import *


class TileRenderer:
    def __init__(self):
        self.tilepic = pygame.image.load("../res/tile.png")
        self.tile = None
        self.rotation = 0.0

    def generate_tile(self, tile, rotation = 0.0):
        self.tilepic = pygame.image.load("../res/tile" + str(tile.army_id) + ".png")
        self.tile = tile
        self.rotation = -60.0 * rotation
        if isinstance(self.tile, Base):
            self.generate_tile_base()
        elif isinstance(self.tile, Unit):
            self.generate_tile_unit()
            self.generate_tile_hp()
        elif isinstance(self.tile, Module):
            self.generate_tile_module()
            self.generate_tile_hp()
        elif isinstance(self.tile, Order):
            self.generate_tile_order()
        elif isinstance(self.tile, Medic):
            self.generate_tile_medic()
            self.generate_tile_hp()
        return self.tilepic

    def generate_tile_hp(self):
        # hp
        if self.tile.hp > 1:
            self.blit("../res/hp" + str(self.tile.hp) + ".png")

    def generate_tile_damage(self):
        # damage
        if self.tile.injuries > 0:
            self.blit("../res/hp" + str(self.tile.hp) + "_dmg" + str(self.tile.injuries) + ".png")

    def generate_tile_base(self):
        self.generate_tile_module()
        self.generate_tile_unit()

    def generate_tile_order(self):
        self.blit("../res/order_" + self.tile.type + ".png")

    def generate_tile_unit(self):
        # nets
        if self.tile.nets is not None:
            for i in xrange(len(self.tile.nets)):
                if self.tile.nets[i]:
                    self.blit("../res/net_attack.png", i)
        # armor
        if self.tile.armor is not None:
            for i in xrange(len(self.tile.armor)):
                if self.tile.armor[i]:
                    self.blit("../res/armor.png", i)
        # range
        if self.tile.range is not None:
            modifier = ""
            if self.tile.row_attack: modifier = "_penetrating"
            for i in xrange(len(self.tile.range)):
                if self.tile.range[i]:
                    self.blit("../res/range" + str(self.tile.range[i]) + modifier + ".png", i)
        # melee
        if self.tile.melee is not None:
            for i in xrange(len(self.tile.melee)):
                if self.tile.melee[i]:
                    self.blit("../res/melee" + str(self.tile.melee[i]) + ".png", i)
        # rotation
        self.tilepic = pygame.transform.rotozoom(self.tilepic, self.rotation, 1.0)
        # initiative
        if self.tile.initiative is not None:
            for init in self.tile.initiative:
                self.blit("../res/init" + str(init[0]) + ".png")
        # mobility
        if self.tile.default_mobility:
            self.blit("../res/mobility.png")
        # unique attack
        if self.tile.unique_attack:
            self.blit("../res/spec_attack.png")

    def generate_tile_module(self):
        # links
        bufftypes = { "buff": [], "debuff": []}
        for buff in self.tile.buff.keys():
            bufftypes["buff"].append(buff)
            self.generate_tile_module_links(self.tile.buff[buff])
        for debuff in self.tile.debuff.keys():
            bufftypes["debuff"].append(debuff)
            self.generate_tile_module_links(self.tile.debuff[debuff])
        # rotation
        self.tilepic = pygame.transform.rotozoom(self.tilepic, self.rotation, 1.0)
        # module icons
        self.blit("../res/module.png")
        # buff icon
        line = ""
        if bufftypes["buff"]:
            for buff in bufftypes["buff"]: line += "_" + buff
            self.blit("../res/module_buff" + line + ".png")
        elif bufftypes["debuff"]:
            for debuff in bufftypes["debuff"]: line += debuff
            self.blit("../res/module_debuff" + line + ".png")

    def generate_tile_medic(self):
        # links
        self.generate_tile_module_links(self.tile.direction)
        # rotation
        self.tilepic = pygame.transform.rotozoom(self.tilepic, self.rotation, 1.0)
        # medic icons
        self.blit("../res/module.png")
        self.blit("../res/unique_medic.png")

    def generate_tile_module_links(self, links):
        for i in xrange(len(links)):
            if links[i] == 0: continue
            self.blit("../res/module_link.png", i)

    def generate_tile_net(self):
        self.blit("../res/net.png")

    def blit(self, filename, rotation = 0):
        pic = pygame.image.load(filename)
        pic.convert_alpha(self.tilepic)
        if rotation: pic = pygame.transform.rotozoom(pic, -60.0 * rotation, 1.0)
        picrect = pic.get_rect()
        picrect.center = self.tilepic.get_rect().center
        self.tilepic.blit(pic, picrect)

    def generate_tile_fx(self, tile, turn):
        self.tile = tile
        self.rotation = 0
        # TODO: Size of the surface shouldn't be a numerical constant
        self.tilepic = pygame.Surface((500, 500), pygame.SRCALPHA)
        picrect = self.tile.gfx[turn].get_rect()
        picrect.center = self.tilepic.get_rect().center
        self.tilepic.blit(self.tile.gfx[turn], picrect)
        if not isinstance(self.tile, Tile):
            return self.tilepic
        if not isinstance(self.tile, Base):
            self.generate_tile_damage()
        if not self.tile.active:
            self.generate_tile_net()
        return self.tilepic

    def generate_cell_fx(self, highlighted = False, selected = False, army_id = 0):
        # TODO: Size of the surface shouldn't be a numerical constant
        self.tilepic = pygame.Surface((500, 500), pygame.SRCALPHA)
        if highlighted:
            self.blit("../res/tile" + str(army_id) + "_selection.png")
        if selected:
            self.blit("../res/tile" + str(army_id) + "_selected.png")
        return self.tilepic


class Renderer:
    def __init__(self, game):
        self.game = game
        # self.screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((1300, 750))
        self.screenrect = self.screen.get_rect()
        self.scale = 0.3
        self.boardbackbuffer = None
        #
        self.idle = False
        self.fps = 0
        self.deltatime = 0
        #
        self.objects = []
        #
        self.pics = {}
        self.pics["button"] = pygame.image.load("../res/button.png")
        self.tile_gen = TileRenderer()
        self.pics["cell"] = pygame.image.load("../res/cell.png")
        self.pics["cellmask"] = pygame.mask.from_surface(self.pics["cell"])
        self.pics["cellmaskrect"] = self.pics["cell"].get_rect()
        self.pics["button_high"] = self.pics["cell_high"] = self.tile_gen.generate_cell_fx(highlighted = True)
        self.pics["button_sel"]  = self.pics["cell_sel"] = self.tile_gen.generate_cell_fx(selected = True)

    def tick(self, deltatime):
        """
        Subroutine executed every tick
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        self.render(deltatime)

    def render(self, deltatime):
        """
        Rendering subroutine
        :param deltatime: Time since last tick (in milliseconds)
        :return: nothing is returned.
        """
        self.deltatime += deltatime
        self.fps += 1
        if self.deltatime >= 1000:
            self.deltatime = 0
            pygame.display.set_caption("FPS: %d" % self.fps)
            # print "FPS: %d" % self.fps
            self.fps = 0
        if not self.idle:
            self.screen.fill((240, 240, 240))
            self.render_board(self.game.playground)
            self.render_players(self.game.players)
            self.render_objects()
            pygame.display.flip()
            # self.idle = True

    def render_players(self, players):
        indent = 0
        tile_gen = TileRenderer()
        for player in players:
            # TODO: Initialize in proper place
            player.gfx = pygame.image.load("../res/player.png")
            player.gfx_indent = gfx_indent = player.gfx.get_rect().center
            player.gfx_multiplier = self.game.playground.gfx_multiplier
            #
            pic = self.clone_pic(player.gfx)
            for cell in player.hand:
                #
                cell.mask = self.game.playground.cellmask
                cell.maskrect = self.game.playground.cellrect.copy()
                cell.maskrect.center = ((gfx_indent[0] + cell.x * self.game.playground.gfx_multiplier[0]) * self.scale,
                                        (gfx_indent[1] + cell.y * self.game.playground.gfx_multiplier[1]) * self.scale + indent)
                # rendering cell fx
                self.render_cell_fx(pic, player, cell)
                # rendering tiles
                if cell.tile is None:
                    continue
                pic.blit(*self.render_tile(player, cell))
            pic = pygame.transform.rotozoom(pic, 0.0, self.scale)
            rect = pic.get_rect()
            rect.left = 0
            rect.top = indent
            self.screen.blit(pic, rect)
            indent += rect.height

    def render_cell_fx(self, target, container, cell):
        if self.game.clicker.click_pending:
            if self.game.clicker.click_selected is not None:
                if cell in self.game.clicker.click_pending[self.game.clicker.click_selected]:
                    self.render_cell_fx_sub(target, container, cell, "highlighted")
                if cell is self.game.clicker.click_selected:
                    self.render_cell_fx_sub(target, container, cell, "selected")
            else:
                if cell in self.game.clicker.click_pending:
                    self.render_cell_fx_sub(target, container, cell, "highlighted")

    def render_cell_fx_sub(self, target, container, cell, type):
        rect = cell.gfx[type].get_rect()
        rect.center = (container.gfx_indent[0] + cell.x * container.gfx_multiplier[0],
                       container.gfx_indent[1] + cell.y * container.gfx_multiplier[1])
        target.blit(cell.gfx[type], rect)

    def render_board(self, grid):
        self.boardbackbuffer = self.clone_pic(grid.gfx)
        rect = grid.gfx.get_rect()
        # rendering cell fx
        for cell in grid.cells:
            self.render_cell_fx(self.boardbackbuffer, grid, cell)
        # rendering tiles
        for cell in grid.cells:
            if cell.tile is None:
                continue
            self.boardbackbuffer.blit(*self.render_tile(grid, cell))
        # showing it on the screen
        self.boardbackbuffer = pygame.transform.rotozoom(self.boardbackbuffer, 0.0, self.scale)
        rect = self.boardbackbuffer.get_rect()
        # rect.center = (self.screenrect.center[0] * 1.33, self.screenrect.center[1])
        rect.center = self.screenrect.center
        self.screen.blit(self.boardbackbuffer, rect)

    def render_tile(self, container, cell):
        if not cell.tile.gfx:
            for turn in xrange(6):
                cell.tile.gfx[turn] = self.tile_gen.generate_tile(cell.tile, turn)
        pic = self.tile_gen.generate_tile_fx(cell.tile, cell.turn)
        rect = pic.get_rect()
        rect.center = (container.gfx_indent[0] + cell.x * container.gfx_multiplier[0],
                       container.gfx_indent[1] + cell.y * container.gfx_multiplier[1])
        return pic, rect

    def make_button(self, button):
        print "make button"
        button.gfx = {}
        button.gfx["default"] = self.clone_pic(self.pics["button"])
        button.gfx["highlighted"] = self.clone_pic(self.pics["button_high"])
        button.gfx["selected"] = self.clone_pic(self.pics["button_sel"])
        for pic in button.gfx:
            button.gfx[pic] = pygame.transform.rotozoom(button.gfx[pic], 0.0, button.scale)
        button.mask = pygame.mask.from_surface(button.gfx["default"])
        button.maskrect = button.gfx["default"].get_rect()
        button.maskrect.left, button.maskrect.top = button.x, button.y
        self.objects.append(button)

    def make_board(self, grid):
        cellpic = pygame.image.load("../res/cell.png")
        cellpicrect = cellpic.get_rect()
        grid.gfx = pygame.Surface(((grid.radius * 2 + 1) * cellpicrect.width,
                                   (grid.radius * 2 + 1) * cellpicrect.height))
        grid.gfx_multiplier = (cellpicrect.width, cellpicrect.height)
        grid.gfx_indent = grid.gfx.get_rect().center
        # cell mask
        temppic = pygame.transform.rotozoom(cellpic, 0.0, self.scale)
        grid.cellmask = pygame.mask.from_surface(temppic)
        grid.cellrect = temppic.get_rect()
        for clickable in grid.cells:
            cellpicrect = cellpic.get_rect()
            cellpicrect.center = (grid.gfx_indent[0] + clickable.x * grid.gfx_multiplier[0],
                                  grid.gfx_indent[1] + clickable.y * grid.gfx_multiplier[1])
            grid.gfx.blit(cellpic, cellpicrect)
            # cell mask
            clickable.mask = grid.cellmask
            clickable.maskrect = temppic.get_rect()
            clickable.maskrect.center = ((grid.gfx_indent[0] + clickable.x * grid.gfx_multiplier[0]) * self.scale +
                                    (self.screenrect.width - grid.gfx.get_rect().width * self.scale) / 2,
                                    (grid.gfx_indent[1] + clickable.y * grid.gfx_multiplier[1]) * self.scale +
                                    (self.screenrect.height - grid.gfx.get_rect().height * self.scale) / 2)

    def render_objects(self):
        for obj in self.objects:
            self.screen.blit(obj.gfx["default"], obj.maskrect)
            if self.game.clicker.click_pending:
                if self.game.clicker.click_selected is not None:
                    if obj in self.game.clicker.click_pending[self.game.clicker.click_selected]:
                        self.screen.blit(obj.gfx["highlighted"], obj.maskrect)
                    if obj is self.game.clicker.click_selected:
                        self.screen.blit(self.game.clicker.click_selected.gfx["selected"], obj.maskrect)
                else:
                    if obj in self.game.clicker.click_pending:
                        self.screen.blit(obj.gfx["highlighted"], obj.maskrect)

    def make_cell(self, cell):
        cell.gfx = {}
        cell.gfx["default"] = self.pics["cell"]
        cell.gfx["highlighted"] = self.pics["cell_high"]
        cell.gfx["selected"] = self.pics["cell_sel"]
        cell.mask = self.pics["cellmask"]
        cell.maskrect = self.pics["cellmaskrect"]

    def clone_pic(self, surface):
        res = pygame.Surface((surface.get_rect().width, surface.get_rect().height), 0, surface)
        res.blit(surface, surface.get_rect())
        return res