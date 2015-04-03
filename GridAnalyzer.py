from __future__ import print_function
from Grid import Grid
from Astar import PathPoint as Point


class BaseMap(object):

    def __init__(self, grid):
        self._grid = grid

    def generate(self, mapp, frontier, includePlayerPt=False):
        grid = self._grid  # Grid(self._grid)
        explored = set()
        nextwave = set()
        wave = 1
        while frontier or nextwave:
            if not frontier:  # next wave!
                frontier = nextwave
                nextwave = set()
                wave += 1
            pt = frontier.pop()
            explored.add(pt)
            mapp[pt] = wave
            neighborSet = grid.get_visible_tile_points_around_point(pt, includePlayerPt)  # get pt neighbors
            nextwave = nextwave.union(neighborSet)  # add pt neighbors to nextwave
            nextwave = nextwave.difference(explored)  # remove any previously explored points
        return mapp

class MovementMap(BaseMap):

    def __init__(self, grid, pt):
        # pt should be location of player
        self._grid = grid
        self._pt = pt

    def generate(self):
        frontier = set()
        frontier.add(self._pt)
        w, h = self._grid.get_shape()
        mapp = Grid(w, h, Point) + (99 - Grid.TILE)  # grid with values 99
        return super(MovementMap, self).generate(mapp, frontier)

class SafeTileMap(BaseMap):
    ''' generates a map with values representing distance from removed tiles and sides.
    '''

    def generate(self):
        grid = self._grid  #Grid(self._grid)
        sides = grid.get_visible_edge_tile_points()
        gapNeighbors = grid.get_points_neighboring_gaps()
        playerPts = grid.get_player_points()
        withPlayers = gapNeighbors.union(sides)
        frontier = withPlayers.difference(playerPts)
        w, h = grid.get_shape()
        mapp = Grid(w, h, Point) - Grid.TILE  # grid with values 0
        return super(SafeTileMap, self).generate(mapp, frontier)

class SummedSafeTileMap(SafeTileMap):
    ''' grid points indicate how many neighbors are safe. Values range from 0 - 8
    '''

    def generate(self):
        grid = self._grid  # Grid(self._grid)
        tilemap = super(SummedSafeTileMap, self).generate()
        return self.create_summed_version(tilemap)

    def create_summed_version(self, tilemap):
        w, h = tilemap.get_shape()
        summed = Grid(w, h, Point) - Grid.TILE
##        summed = np.zeros(tilemap.shape)
        w, h = tilemap.shape
        for x in range(w):
            for y in range(h):
                pt = Point(x, y)
                if tilemap[pt] > 0:  # if it's an open spot  # pt.x, pt.y
                    pts = grid.get_all_tile_points_around_point(pt)
                    for valuePt in pts:
                        summed[pt] += tilemap[valuePt]
        return summed

        
class GridAnalyzer:
    grid = None
    def __init__(self, grid, startPoint):
        self.grid = grid
        self.startPoint = startPoint

    def get_analyzed_grid(self):
        sstm = SummedSafeTileMap(self.grid)
        sumtilemap = sstm.generate()
        mm = MovementMap(self.grid, self.startPoint)
        movemap = mm.generate()
        return sumtilemap - movemap

    def get_target_point(self):
        ''' analyzes the grid and returns a point representing the best location
            in the grid, reachable from the startPoint
        '''
        computedGrid = self.get_analyzed_grid()

        
if __name__ == '__main__':
    gapPts = [Point(2, 3), Point(1, 1), Point(0, 0)]
    playerPt = Point(1,2)  # put player there
    w, h = 4, 4
    grid = Grid(w, h, Point)
    grid.set_player_points([playerPt])
    grid.set_gap_points(gapPts)
    ga = GridAnalyzer(grid, playerPt)
    bestGrid = ga.get_analyzed_grid()
    print(bestGrid)
##    sstm = SummedSafeTileMap(grid)
##    sumtilemap = sstm.generate()
##    stm = SafeTileMap(grid)
##    tilemap = stm.generate()
##    mm = MovementMap(grid, playerPt)
##    movemap = mm.generate()
##    print(movemap, '\n')
##    print(tilemap, '\n')
##    print(sumtilemap, '\n')
##    print(sumtilemap - movemap, '\n')
    
