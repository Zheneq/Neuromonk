__author__ = 'Zheneq'
import pygame
from tile import *


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

    def generate_tile(self, tile):
        tilepic = pygame.image.load("../res/tile" + str(tile.army_id) + ".png")
        if isinstance(tile, Unit):
            print "unit"
            tilepic = self.generate_tile_unit(tile, tilepic)
            tilepic = self.generate_tile_hp(tile, tilepic)
        if isinstance(tile, Module):
            print "module"
            tilepic = self.generate_tile_module(tile, tilepic)
            tilepic = self.generate_tile_hp(tile, tilepic)
        return tilepic

    def generate_tile_hp(self, tile, tilepic):
        # hp
        if tile.hp > 1:
            hppic = pygame.image.load("../res/hp" + str(tile.hp) + ".png")
            hppic.convert_alpha(tilepic)
            tilepic.blit(hppic, hppic.get_rect())
        return tilepic

    def generate_tile_unit(self, tile, tilepic):
        for i in xrange(len(tile.melee)):
            # armor
            if tile.armor[i]:
                armorpic = pygame.image.load("../res/armor.png")
                armorpic.convert_alpha(tilepic)
                armorpic = pygame.transform.rotozoom(armorpic, -60.0 * i, 1.0)
                self.generate_tile_blit(tilepic, armorpic)
            # range
            if tile.range[i]:
                attackpic = pygame.image.load("../res/range" + str(tile.range[i]) + ".png")
                attackpic.convert_alpha(tilepic)
                attackpic = pygame.transform.rotozoom(attackpic, -60.0 * i, 1.0)
                self.generate_tile_blit(tilepic, attackpic)
            # melee
            if tile.melee[i]:
                attackpic = pygame.image.load("../res/melee" + str(tile.melee[i]) + ".png")
                attackpic.convert_alpha(tilepic)
                attackpic = pygame.transform.rotozoom(attackpic, -60.0 * i, 1.0)
                self.generate_tile_blit(tilepic, attackpic)
        # initiative
        for init in tile.initiative:
            initpic = pygame.image.load("../res/init" + str(init[0]) + ".png")
            initpic.convert_alpha(tilepic)
            tilepic.blit(initpic, initpic.get_rect())
        return tilepic

    def generate_tile_module(self, tile, tilepic):
        bufftype = None
        for buff in tile.buff.keys():
            bufftype = "buff_" + buff
            self.generate_tile_module_links(tilepic, tile.buff[buff])
        for debuff in tile.debuff.keys():
            bufftype = "debuff_" + debuff
            self.generate_tile_module_links(tilepic, tile.debuff[debuff])
        modulepic = pygame.image.load("../res/module.png")
        modulepic.convert_alpha(tilepic)
        tilepic.blit(modulepic, modulepic.get_rect())
        if bufftype is not None:
            buffpic = pygame.image.load("../res/module_" + bufftype + ".png")
            buffpic.convert_alpha(tilepic)
            tilepic.blit(buffpic, buffpic.get_rect())
        return tilepic

    def generate_tile_module_links(self, tilepic, links):
        for i in xrange(len(links)):
            if links[i] == 0: continue
            linkpic = pygame.image.load("../res/module_link.png")
            linkpic.convert_alpha(tilepic)
            linkpic = pygame.transform.rotozoom(linkpic, -60.0 * i, 1.0)
            self.generate_tile_blit(tilepic, linkpic)

    def generate_tile_blit(self, tilepic, pic):
        picrect = pic.get_rect()
        picrect.center = tilepic.get_rect().center
        tilepic.blit(pic, picrect)

    def render_tiles(self, grid):
        for cell in grid.cells:
            if cell.tile is None:
                continue
            cellpic = self.generate_tile(cell.tile)
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