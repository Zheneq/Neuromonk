__author__ = 'Zheneq'
import pygame


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((640, 480))
        self.screenrect = self.screen.get_rect()
        self.scale = 0.33
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
        for cell in grid.cells:
            if cell.tile is None:
                continue
            cellpic = pygame.image.load("../res/tile.png")
            cellpic = pygame.transform.rotozoom(cellpic, 60.0 * cell.turn, self.scale)
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