__author__ = 'Dandelion'
from renderer import Renderer

class Cell(object):
    def __init__(self):
        self.tile = None
        self.turn = 0
        self.neighbours = [None for ind in xrange(6)]
        # gfx values
        self.x = 0.0
        self.y = 0.0

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


class Grid(object):
    def __init__(self, radius=2):
        # relative offsets between adjacent cells
        offset = [(0.0, -1.0), (0.75, -0.5), (0.75, 0.5), (0, 1), (-0.75, 0.5), (-0.75, -0.5)]
        self.cells = [Cell()]
        for rad in xrange(radius):
            buffer = []
            for cell in self.cells:
                for ind in xrange(len(cell.neighbours)):
                    if cell.neighbours[ind] is None:
                        buffer.append(Cell())
                        last_cell = buffer[len(buffer) - 1]
                        if cell.next(ind) is not None:
                            self.link(cell.next(ind), last_cell, cell.rightind(ind))
                        if cell.prev(ind) is not None:
                            self.link(cell.prev(ind), last_cell, cell.leftind(ind))
                        self.link(cell, last_cell, ind)
                        last_cell.x = cell.x + offset[ind][0]
                        last_cell.y = cell.y + offset[ind][1]
            self.cells.extend(buffer)

    def link(self, cell1, cell2, direction):
        cell1.neighbours[direction] = cell2
        cell2.neighbours[cell1.oppose(direction)] = cell1


if __name__ == "__main__":
    grid = Grid(2)
    renderer = Renderer(None)
    renderer.render_board(grid)
    print "Yay!"

