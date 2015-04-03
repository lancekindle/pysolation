from __future__ import print_function
from Grid import Grid
from Astar import PathPoint as Point

# if you see an error like: ValueError: setting an array element with a sequence.
# then you are probably accidentally accessing a numpy array with a point
# array[pt] like that, when you should be accessing grid[pt].
class BaseMap(object):

    def __init__(self, grid):
        self._grid = grid

    def generate(self, mapp, frontier, includePlayerPt=False):
        grid = self._grid
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
    ''' generates a map with values representing distance from removed tiles, players, and sides.
        values of 0 represent where a player or gap exists. Points neighboring those will have value of 1,
        and all other locations will have increasingly larger positive values the farther from 0's they are.
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
        summed = Grid(w, h, Point) - Grid.TILE  # a grid of all 0's
        for x, y, pt in tilemap:
            if tilemap[pt] > 0:  # tilemap[pt] == 0 where there are players or gaps. All other values are positive.
                pts = tilemap.get_all_tile_points_around_point(pt)
                for valuePt in pts:
                    summed[pt] += tilemap[valuePt]
        return summed

        
class GridAnalyzer:
    grid = None
    verbose = False
    
    def __init__(self, grid, startPoint):
        self.grid = grid
        self.startPoint = Point(startPoint.x, startPoint.y)

    def get_analyzed_grid(self):
        ''' analyze self.grid without changing it
        '''
        stm = SafeTileMap(self.grid)
        safemap = stm.generate()
        sstm = SummedSafeTileMap(self.grid)
        sumtilemap = sstm.generate()  
        mm = MovementMap(self.grid, self.startPoint)
        movemap = mm.generate()
        if self.verbose:
            print('safemap;\n', safemap)
            print('sumtilemap;\n', sumtilemap)
            print('movemap;\n', movemap)
            print('final;\n', sumtilemap - movemap)
        return sumtilemap - movemap

    def get_target_point(self):
        ''' analyzes the grid and returns a point representing the best location
            in the grid, reachable from the startPoint
        '''
        computedGrid = self.get_analyzed_grid()
        return computedGrid.get_first_highest_value_point()

        
if __name__ == '__main__':
    gapPts = [Point(2, 3), Point(1, 1), Point(0, 0)]
    playerPt = Point(1,2)  # put player there
    w, h = 4, 4
    grid = Grid(w, h, Point)
    grid.set_player_points([playerPt])
    grid.set_gap_points(gapPts)
    ga = GridAnalyzer(grid, playerPt)
    bestGrid = ga.get_analyzed_grid()
    bestPoint1 = bestGrid.get_first_highest_value_point()
    print(bestGrid)
    print(bestPoint1)
    
