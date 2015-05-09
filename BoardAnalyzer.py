import numpy as np
import random


class BaseGrid(object):
    GAP = 0
    TILE = 1

    def __init__(self, grid):
        self.originalGrid = grid

    def is_in_bounds(self, grid, x, y):
        xborder, yborder = grid.shape[:2]
        if x >= xborder or y >= yborder:
            return False
        if x < 0 or y < 0:
            return False
        return True

    def set_gaps(self, grid):
        """ set passed grid to zero @ coordinates where original grid was zero """
        for c, col in enumerate(self.originalGrid):
            for r, val in enumerate(col):
                if val == self.GAP:
                    self.grid[r, c] = self.GAP
        return grid

    def get_tile_neighbors_around_point(self, grid, x, y):
        """ return list of neighbor tile value and coordinates that are available. GAPS not included
        i.e. if x=5, y=7, and value = 2 is a tile, the tuple (2, 5, 7) would be added to the list of neighbors
        """
        directions = [-1, 0, 1]
        neighbors = set()
        for h in directions:
            for v in directions:
                if h == v == 0:
                    continue  # skip searching x, y point
                if grid[x, y] == self.GAP:
                    continue
                if self.is_in_bounds(grid, x + h, y + v):
                    value = grid[x, y]
                neighbors.add((value, x + h, y + v))
        return neighbors
    

class MoveGrid(BaseGrid):

    def expand_from_points(self, grid, points):
        """ points should be a list of tuples, which indicate the starting points from which to expand """
        frontier = set(points)
        explored = set()
        nextwave = set()
        wave = 1
        while frontier or nextwave:
            if not frontier:  # next wave!
                frontier = nextwave
                nextwave = set()
                wave += 1
            v, x, y = frontier.pop()
            explored.add((v, x, y))
            grid[x, y] = wave
            neighborSet = self.get_tile_neighbors_around_point(self.originalGrid, x, y)
            nextwave = nextwave.union(neighborSet)  # add neighbors to nextwave
            nextwave = nextwave.difference(explored)  # remove any previously explored points
        return grid


class AccessibleGrid(MoveGrid):

    def get_grid_accessible_from_point(self, grid, x, y):
        expanded = self.expand_from_point(grid, [(x, y)])
        accessible = expanded > self.GAP  # we make the assumption that gaps / obstacles / unreachables are 0 or lower
        return grid * accessible
    

class SweetSpotGrid(AccessibleGrid):

    def get_sweet_spots_from_point(self, grid, x, y):
        accessible = self.get_grid_accessible_from_point(grid, x, y)
        firstPass = self.neighbor_convolve(accessible)
        passOneWithGaps = self.set_gaps(firstPass)
        secondPass = self.neighbor_convolve(passOneWithGaps)
        passTwoWithGaps = self.set_gaps(secondPass)
        bestSpots = (passTwoWithGaps == passTwoWithGaps.max())
        arrayCoords = np.transpose(bestSpots.nonzero())
        sweetSpots = [(x, y) for x, y in arrayCoords]  # convert to usable list of tuple coordinates
        return sweetSpots

    def get_next_move_toward_sweet_spot(self, grid, x, y):
        """ find neighboring tile to x, y that moves in direction towards sweet spot """
        sweetSpots = self.get_sweet_spots_from_point(grid, x, y)
        moveGrid = self.expand_from_points(grid, sweetSpots)
        neighbors = self.get_tile_neighbors_around_point(moveGrid, x, y)
        vMax, x, y = max(neighbors)
        bestMoves = [(x, y) for v, x, y in neighbors if v == vMax]
        x, y = random.choice(bestMoves)
        return x, y


if __name__ == '__main__':
    pass
