import numpy as np
import random
import scipy
from scipy import signal


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
        grid = grid.copy()
        for x, col in enumerate(self.originalGrid):
            for y, val in enumerate(col):
                if val == self.GAP:
                    grid[x, y] = self.GAP
        return grid

    def get_tile_neighbors_around_point(self, grid, x, y, includeValue=False):
        """ return list of neighbor tile value and coordinates that are available. GAPS and NaN valued points not
        included i.e. if x=5, y=7, and value = 2 is a tile, the tuple (2, 5, 7) would be added to the list of neighbors
        """
        directions = [-1, 0, 1]
        neighbors = set()
        for h in directions:
            for v in directions:
                if h == v == 0:
                    continue  # skip searching x, y point
                x2, y2 = x + h, y + v
                if not self.is_in_bounds(grid, x2, y2):
                    continue
                if self.originalGrid[x2, y2] == self.GAP:  # skip gap
                    continue
                if np.isnan(grid[x2, y2]):  # skip NaN valued items
                    continue
                value = grid[x2, y2]
                if includeValue:
                    neighbors.add((value, x2, y2))
                else:
                    neighbors.add((x2, y2))
        return neighbors
    

class MoveGrid(BaseGrid):

    def _prep_grid_for_point_expansion(self, grid):
        grid = grid.copy()  # make copy so we don't alter original
        for x, col in enumerate(grid):
            for y, value in enumerate(col):
                if not value == self.GAP:  # any non-gaps set to NaN, indicating it's unreachable
                    grid[x, y] = np.Inf
        return grid

    def _set_gaps_to_infinite(self, grid):
        for x, col in enumerate(grid):
            for y, value in enumerate(col):
                if value == self.GAP:  # any gaps set to NaN, indicating it's unreachable
                    grid[x, y] = np.Inf
        return grid
            

    def expand_from_points(self, grid, points):
        """ points should be a list of tuples, which indicate the starting points from which to expand.
        expand across board from starting points. Each expansion "wave" increments the value of the found points
        such that points further from starting points are greater in value. After expanding, any unreachable points
        and gaps will contain the np.Inf vlaue, indicating they are invalid moves
        """
        grid = grid.copy()  # make a copy, since we will be altering the grid
        grid = self._prep_grid_for_point_expansion(grid)
        frontier = set(points)
        explored = set()
        nextwave = set()
        wave = 1
        while frontier or nextwave:
            if not frontier:  # next wave!
                frontier = nextwave
                nextwave = set()
                wave += 1
            p = frontier.pop()
            x, y = p
            explored.add(p)
            grid[x, y] = wave
            neighborSet = self.get_tile_neighbors_around_point(self.originalGrid, x, y)
            nextwave = nextwave.union(neighborSet)  # add neighbors to nextwave
            nextwave = nextwave.difference(explored)  # remove any previously explored points
        # now set all gaps to infinite
        expanded = self._set_gaps_to_infinite(grid)
        return expanded


class AccessibleGrid(MoveGrid):

    def get_grid_accessible_from_point(self, grid, x, y):
        expanded = self.expand_from_points(grid, [(x, y)])
        accessible = expanded > 1  # wave starts at 1, so > 1 will indicate any spot accessible from x, y, but not x, y itself
##        print('accessible')
##        print(accessible)
        return grid * accessible


class SweetSpotGrid(AccessibleGrid):

    def neighbor_convolve(self, grid):
        neighborSumming = np.ones((3,3), dtype=np.int32)
        neighborSummed = scipy.signal.convolve(grid, neighborSumming, mode='same')
        return neighborSummed

    def get_sweet_spots_from_point(self, grid, x, y):
        accessible = self.get_grid_accessible_from_point(grid, x, y)
        firstPass = self.neighbor_convolve(accessible)
        passOneWithGaps = self.set_gaps(firstPass)
##        print(passOneWithGaps)
        secondPass = self.neighbor_convolve(passOneWithGaps)
        passTwoWithGaps = self.set_gaps(secondPass)
        passTwoWithGaps[x, y] = 0  # set to zero so that the best spot does NOT equal starting point (x, y).
##        print(passTwoWithGaps)
        bestSpots = (passTwoWithGaps == passTwoWithGaps.max())
        arrayCoords = np.transpose(bestSpots.nonzero())
        sweetSpots = [(x, y) for x, y in arrayCoords]  # convert to usable list of tuple coordinates
        return sweetSpots

    def get_next_move_toward_sweet_spot(self, grid, x, y):
        """ find neighboring tile to x, y that moves in direction towards sweet spot """
        sweetSpots = self.get_sweet_spots_from_point(grid, x, y)
##        print(sweetSpots)
        moveGrid = self.expand_from_points(grid, sweetSpots)
        print(moveGrid)
        neighbors = self.get_tile_neighbors_around_point(moveGrid, x, y, True)
##        print(neighbors)
        vMin, x, y = min(neighbors)
##        print(vMin)
##        print('vMin', vMin)
##        print(neighbors)
        bestMoves = [(x, y) for v, x, y in neighbors if v == vMin]
        print(bestMoves)
        x, y = random.choice(bestMoves)
        return x, y


if __name__ == '__main__':
    g = np.ones((5,5))
    g[1,2] = 0
    g[1, 1] = 0
    g[3, 3] = 0
    g[2,3:5] =0
    g[3, 1] = 0
    x1, y1 = 6, 3  # where player is
    g = np.ones((7,6)) 
    g[x1, y1] = 0
    g[1, 0] = 0
    g[1, 5] = 0
    print(g)
    ssg = SweetSpotGrid(g)
    x, y = ssg.get_next_move_toward_sweet_spot(g, x1, y1)
    print(x, y)
    
