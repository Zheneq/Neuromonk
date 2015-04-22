__author__ = 'Zheneq'
import pygame
from tile import *


class TileRenderer:
    def __init__(self):
        self.tilepic = pygame.image.load("../res/tile.png")
        self.tile = None
        self.rotation = 0.0

    def generate_tile(self, tile, rotation = 0.0):
        self.tilepic = pygame.image.load("../res/tile" + str(tile.army_id) + ".png")
        self.tile = tile
        self.rotation = -60.0 * rotation
        if isinstance(self.tile, Unit):
            self.generate_tile_unit()
            self.generate_tile_hp()
        if isinstance(self.tile, Module):
            self.generate_tile_module()
            self.generate_tile_hp()
        if isinstance(self.tile, Medic):
            self.generate_tile_medic()
            self.generate_tile_hp()
        if not self.tile.active:
            self.generate_tile_net()
        return self.tilepic

    def generate_tile_hp(self):
        # hp
        if self.tile.hp > 1:
            self.blit("../res/hp" + str(self.tile.hp) + ".png")
        # damage
        if self.tile.injuries > 0:
            self.blit("../res/hp" + str(self.tile.hp) + "_dmg" + str(self.tile.injuries) + ".png")

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
            for i in xrange(len(self.tile.range)):
                if self.tile.range[i]:
                    self.blit("../res/range" + str(self.tile.range[i]) + ".png", i)
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

    def generate_tile_module(self):
        # links
        bufftype = None
        for buff in self.tile.buff.keys():
            bufftype = "buff_" + buff
            self.generate_tile_module_links(self.tile.buff[buff])
        for debuff in self.tile.debuff.keys():
            bufftype = "debuff_" + debuff
            self.generate_tile_module_links(self.tile.debuff[debuff])
        # rotation
        self.tilepic = pygame.transform.rotozoom(self.tilepic, self.rotation, 1.0)
        # module icons
        self.blit("../res/module.png")
        if bufftype is not None:
            self.blit("../res/module_" + bufftype + ".png")

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


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((800, 600))
        self.screenrect = self.screen.get_rect()
        self.scale = 0.5
        self.multiplier = (1.0, 1.0)
        self.indent = self.screenrect.center

    def render_board(self, grid):
        cellpic = pygame.image.load("../res/cell.png")
        cellpic = pygame.transform.rotozoom(cellpic, 0.0, self.scale)
        cellpicrect = cellpic.get_rect()
        center = self.screenrect.center
        self.multiplier = (cellpicrect.width, cellpicrect.height)
        self.indent = self.screenrect.center
        for cell in grid.cells:
            cellpicrect = cellpic.get_rect()
            cellpicrect.center = (self.indent[0] + cell.x * self.multiplier[0],
                                  self.indent[1] + cell.y * self.multiplier[1])
            self.screen.blit(cellpic, cellpicrect)
        self.render_tiles(grid)

    def render_tiles(self, grid):
        tile_gen = TileRenderer()
        for cell in grid.cells:
            if cell.tile is None:
                continue
            cellpic = tile_gen.generate_tile(cell.tile, cell.turn)
            cellpic = pygame.transform.rotozoom(cellpic, 0.0, self.scale)
            cellpicrect = cellpic.get_rect()
            cellpicrect.center = (self.indent[0] + cell.x * self.multiplier[0],
                                  self.indent[1] + cell.y * self.multiplier[1])
            self.screen.blit(cellpic, cellpicrect)
        # for test purpose
        pygame.display.flip()
        again = True
        while again:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                again = False