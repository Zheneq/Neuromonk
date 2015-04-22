__author__ = 'Zheneq'
import pygame
from tile import *


class TileRenderer:
    def __init__(self):
        self.tilepic = pygame.image.load("../res/tile.png")
        self.tile = None

    def generate_tile(self, tile):
        self.tilepic = pygame.image.load("../res/tile" + str(tile.army_id) + ".png")
        self.tile = tile
        if isinstance(self.tile, Unit):
            print "unit"
            self.generate_tile_unit()
            self.generate_tile_hp()
        if isinstance(tile, Module):
            print "module"
            self.generate_tile_module()
            self.generate_tile_hp()
        return self.tilepic

    def generate_tile_hp(self):
        # hp
        if self.tile.hp > 1:
            hppic = pygame.image.load("../res/hp" + str(self.tile.hp) + ".png")
            hppic.convert_alpha(self.tilepic)
            self.tilepic.blit(hppic, hppic.get_rect())

    def generate_tile_unit(self):
        for i in xrange(len(self.tile.melee)):
            # armor
            if self.tile.armor[i]:
                armorpic = pygame.image.load("../res/armor.png")
                armorpic.convert_alpha(self.tilepic)
                armorpic = pygame.transform.rotozoom(armorpic, -60.0 * i, 1.0)
                self.generate_tile_blit(armorpic)
            # range
            if self.tile.range[i]:
                attackpic = pygame.image.load("../res/range" + str(self.tile.range[i]) + ".png")
                attackpic.convert_alpha(self.tilepic)
                attackpic = pygame.transform.rotozoom(attackpic, -60.0 * i, 1.0)
                self.generate_tile_blit(attackpic)
            # melee
            if self.tile.melee[i]:
                attackpic = pygame.image.load("../res/melee" + str(self.tile.melee[i]) + ".png")
                attackpic.convert_alpha(self.tilepic)
                attackpic = pygame.transform.rotozoom(attackpic, -60.0 * i, 1.0)
                self.generate_tile_blit(attackpic)
        # initiative
        for init in self.tile.initiative:
            initpic = pygame.image.load("../res/init" + str(init[0]) + ".png")
            initpic.convert_alpha(self.tilepic)
            self.tilepic.blit(initpic, initpic.get_rect())

    def generate_tile_module(self):
        bufftype = None
        for buff in self.tile.buff.keys():
            bufftype = "buff_" + buff
            self.generate_tile_module_links(self.tile.buff[buff])
        for debuff in self.tile.debuff.keys():
            bufftype = "debuff_" + debuff
            self.generate_tile_module_links(self.tile.debuff[debuff])
        modulepic = pygame.image.load("../res/module.png")
        modulepic.convert_alpha(self.tilepic)
        self.tilepic.blit(modulepic, modulepic.get_rect())
        if bufftype is not None:
            buffpic = pygame.image.load("../res/module_" + bufftype + ".png")
            buffpic.convert_alpha(self.tilepic)
            self.tilepic.blit(buffpic, buffpic.get_rect())

    def generate_tile_module_links(self, links):
        for i in xrange(len(links)):
            if links[i] == 0: continue
            linkpic = pygame.image.load("../res/module_link.png")
            linkpic.convert_alpha(self.tilepic)
            linkpic = pygame.transform.rotozoom(linkpic, -60.0 * i, 1.0)
            self.generate_tile_blit(linkpic)

    def generate_tile_blit(self, pic):
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
            cellpic = tile_gen.generate_tile(cell.tile)
            cellpic = pygame.transform.rotozoom(cellpic, -60.0 * cell.turn, self.scale)
            cellpicrect = cellpic.get_rect()
            cellpicrect.center = (self.indent[0] + cell.x * self.multiplier[0],
                                  self.indent[1] + cell.y * self.multiplier[1])
            self.screen.blit(cellpic, cellpicrect)
            print "Yaaa..."
        # for test purpose
        pygame.display.flip()
        again = True
        while again:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                again = False