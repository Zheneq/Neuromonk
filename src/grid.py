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

    def action(self, damage_modificator):
        for ind in xrange(len(self.neighbours)):
            damage = self.tile.damage(ind - self.turn)
            if self.tile.can_melee_buffed:
                damage['melee'] += damage_modificator['melee']
            if self.tile.can_range_buffed:
                damage['range'] += damage_modificator['range']
            if damage['melee'] > 0:
                if self.neighbours[ind] is not None and self.neighbours[ind].tile is not None:
                    if self.neighbours[ind].tile.army_id != self.tile.army_id:
                        damage_to_unit = {'value': damage['melee'], 'type': 'melee', 'instigator': self.tile}
                        self.neighbours[ind].tile.taken_damage.append(damage_to_unit)
            if damage['range'] > 0:
                neighbour = self.neighbours[ind]
                while neighbour is not None:
                    if neighbour.tile is not None and neighbour.tile.army_id != self.tile.army_id:
                        range_damage = damage['range'] - neighbour.tile.get_armor(ind - neighbour.turn)
                        if range_damage > 0:
                            damage_to_unit = {'value': range_damage,
                                              'type': 'range',
                                              'instigator': self.tile}
                            neighbour.tile.taken_damage.append(damage_to_unit)
                        if not self.tile.row_attack:
                            break
                    neighbour = neighbour.neighbours[ind]

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

