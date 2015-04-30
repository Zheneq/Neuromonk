__author__ = 'Dandelion'
from renderer import Renderer


class Clickable(object):
    def __init__(self, game):
        self.game = game
        # gfx values
        self.x = 0.0
        self.y = 0.0
        self.mask = None
        self.maskrect = None
        #
        self.game.add_actor(self)
        self.invalidate()

    def invalidate(self):
        self.mask = None
        self.maskrect = None


class Button(Clickable):
    def __init__(self, game, action, x = 0, y = 0, scale = 1.0):
        self.scale = scale
        Clickable.__init__(self, game)
        self.x = x
        self.y = y
        self.action = action
        self.invalidate()

    def invalidate(self):
        Clickable.invalidate(self)
        self.game.renderer.make_button(self)


class Cell(Clickable):
    def __init__(self, game):
        Clickable.__init__(self, game)
        self.tile = None
        self.turn = 0
        self.neighbours = [None for ind in xrange(6)]

    def next(self, ind):
        return self.neighbours[(ind + 1) % 6]

    def prev(self, ind):
        return self.neighbours[(ind - 1) % 6]

    def rightind(self, ind):
        return (ind - 1) % 6

    def leftind(self, ind):
        return (ind + 1) % 6

    def oppose(self, ind):
        return (ind + 3) % 6

    def invalidate(self):
        Clickable.invalidate(self)
        self.game.renderer.make_cell(self)


class Grid(object):
    def __init__(self, game, radius=2):
        self.radius = radius
        self.game = game
        # relative offsets between adjacent cells
        offset = [(0.0, -1.0), (0.75, -0.5), (0.75, 0.5), (0, 1), (-0.75, 0.5), (-0.75, -0.5)]
        self.cells = [Cell(game)]
        for rad in xrange(radius):
            buffer = []
            for cell in self.cells:
                for ind in xrange(len(cell.neighbours)):
                    if cell.neighbours[ind] is None:
                        buffer.append(Cell(game))
                        last_cell = buffer[len(buffer) - 1]
                        if cell.next(ind) is not None:
                            self.link(cell.next(ind), last_cell, cell.rightind(ind))
                        if cell.prev(ind) is not None:
                            self.link(cell.prev(ind), last_cell, cell.leftind(ind))
                        self.link(cell, last_cell, ind)
                        last_cell.x = cell.x + offset[ind][0]
                        last_cell.y = cell.y + offset[ind][1]
            self.cells.extend(buffer)
        self.game.renderer.make_board(self)

    def link(self, cell1, cell2, direction):
        cell1.neighbours[direction] = cell2
        cell2.neighbours[cell1.oppose(direction)] = cell1

    def get_free_cells(self):
        result = []
        for cell in self.cells:
            if cell.tile is None:
                result.append(cell)
        return result


if __name__ == "__main__":
    grid = Grid(2)
    renderer = Renderer(None)
    renderer.render_board(grid)
    print "Yay!"

