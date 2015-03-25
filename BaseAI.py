from __future__ import print_function
import numpy as np

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xy = (x, y)

    def __getitem__(self, i):
        return self.xy[i]

    def __set__(self, i, i2):
        raise UserWarning('cannot modify Point!')

    def __eq__(self, other):
        return self.xy == other.xy

    def __hash__(self):
        return self.x * 1000 + self.y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return str(self.x) + ',' + str(self.y)

    def __repr__(self):
        return str(self)

    @classmethod
    def get_lruds(self):
        ''' return points for left, right, up, down, and stay
        '''
        left = Point(-1, 0)
        right = Point(1, 0)
        up = Point(0, -1)
        down = Point(0, 1)
        stay = Point(0, 0)
        return left, right, up, down, stay

class Grid:
    PLAYER = -1
    GAP = 0
    TILE = 1

    def __init__(self, grid):
        ''' grid expects to recieve a numpy matrix of simple value: 1s or 0s
        '''
        self.grid = grid

    def __getitem__(self, pt):
        if pt.x < 0 or pt.y < 0:
            raise IndexError
        return self.grid[pt.x, pt.y]

    def get_all_tile_points_around_point(self, pt):
        left, right, up, down, stay = Point.get_lruds()
        verticals = [up, down, stay]
        horizontals = [left, right, stay]
        tiles = set()
        for vertical in verticals:
            for horizontal in horizontals:
                if vertical == horizontal == stay:
                    continue  # skip returning the point itself
                direction = vertical + horizontal
                newpoint = pt + direction
                try:
                    tile = self[newpoint]
                except IndexError:
                    continue  # must be at bounds of grid
                tiles.add(newpoint)
        return tiles

    def get_visible_tile_points_around_point(self, pt, includePlayerPt=False):  # do NOT include points where players are.
        tilePts = self.get_all_tile_points_around_point(pt)
        tiles = set()
        for pt in tilePts:
            if self[pt] == self.TILE or (includePlayerPt and self[pt] == self.PLAYER):
                tiles.add(pt)
        return tiles

    def get_visible_edge_tile_points(self):
        edges = set()
        w, h = self.grid.shape
        y = 0
        top = [Point(x, y) for x in range(w) if self[Point(x, y)] == self.TILE]
        y = h - 1
        bottom = [Point(x, y) for x in range(w) if self[Point(x, y)] == self.TILE]
        x = 0
        left = [Point(x, y) for y in range(h) if self[Point(x, y)] == self.TILE]
        x = w - 1
        right = [Point(x, y) for y in range(h) if self[Point(x, y)] == self.TILE]
        for pt in left + right + top + bottom:
            edges.add(pt)
        return edges

    def get_points_neighboring_gaps(self):
        allNeighbors = set()
        w, h = self.grid.shape
        for x in range(w):
            for y in range(h):
                pt = Point(x, y)
                if self[pt] == self.GAP:  # we found a gap
                    nearbyToGap = self.get_visible_tile_points_around_point(pt)
                    allNeighbors = allNeighbors.union(nearbyToGap)
        return allNeighbors

    def get_player_points(self):
        playerPts = set()
        w, h = self.grid.shape
        for x in range(w):
            for y in range(h):
                pt = Point(x, y)
                if self[pt] == self.PLAYER:
                    playerPts.add(pt)
        return playerPts
        

class BaseMap(object):

    def __init__(self, grid):
        self._grid = grid

    def generate(self, mapp, frontier, includePlayerPt=False):
        grid = Grid(self._grid)
        #playerAt = Point(*self._pt.xy)
        explored = set()
        #frontier = set()
        #frontier.add(playerAt)
        nextwave = set()
        wave = 1
        while frontier or nextwave:
            if not frontier:  # next wave!
                frontier = nextwave
                nextwave = set()
                wave += 1
            pt = frontier.pop()
            explored.add(pt)
            mapp[pt.x, pt.y] = wave
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
        mapp = np.zeros(self._grid.shape) + 99  # movement map all to +9... to start (aka hard to reach)
        return super(MovementMap, self).generate(mapp, frontier)

class SafeTileMap(BaseMap):
    ''' generates a map with values representing distance from removed tiles and sides.
    '''

    def generate(self):
        grid = Grid(self._grid)
        sides = grid.get_visible_edge_tile_points()
        gapNeighbors = grid.get_points_neighboring_gaps()
        playerPts = grid.get_player_points()
        withPlayers = gapNeighbors.union(sides)
        frontier = withPlayers.difference(playerPts)
        mapp = np.zeros(self._grid.shape)  # gaps are valued at 0.
        return super(SafeTileMap, self).generate(mapp, frontier)

class SummedSafeTileMap(SafeTileMap):

    def generate(self):
        grid = Grid(self._grid)
        tilemap = super(SummedSafeTileMap, self).generate()
        return self.create_summed_version(tilemap)

    def create_summed_version(self, tilemap):
        summed = np.zeros(tilemap.shape)
        w, h = tilemap.shape
        for x in range(w):
            for y in range(h):
                pt = Point(x, y)
                if tilemap[pt.x, pt.y] > 0:  # if it's an open spot
                    pts = grid.get_all_tile_points_around_point(pt)
                    for valuePt in pts:
                        summed[pt.x, pt.y] += tilemap[valuePt.x, valuePt.y]
        return summed
        
        
if __name__ == '__main__':
    array = np.ones((4,4))
    array[2, 3] = 0
    array[1,1] = 0
    array[0,0] = 0
    pt = Point(1,2)
    array[1,2] = -1  # put player there
    grid = Grid(array)
    sstm = SummedSafeTileMap(array)
    sumtilemap = sstm.generate()
    stm = SafeTileMap(array)
    tilemap = stm.generate()
    mm = MovementMap(array, pt)
    movemap = mm.generate()
    print(movemap, '\n')
    print(tilemap, '\n')
    print(sumtilemap, '\n')
