from __future__ import print_function
import numpy as np


class Grid:
    PLAYER = -1
    GAP = 0
    TILE = 1
    Point = None

    def __init__(self, w, h, Point):
        self.shape = (h, w)  # for numpy stuff
        self.w, self.h = w, h
        self.grid = np.zeros(self.shape) + self.TILE
        self.Point = Point  # store instance of Point class

    def __getitem__(self, pt):
        if pt.x < 0 or pt.y < 0:  #only allow single point indexing
            raise IndexError
        return self.grid[pt.x, pt.y]

    def __setitem__(self, pt, val):
        if pt.x < 0 or pt.y < 0:
            raise IndexError
        self.grid[pt.x, pt.y] = val

    def __sub__(self, other):
        if isinstance(other, Grid):
            newgrid = Grid(self.w, self.h, self.Point)
            newgrid.grid = self.grid - other.grid
            return newgrid
        else:  # commit subtraction operation to numpy array
            self.grid.__sub__(other)
            return self

    def __add__(self, other):
        if isinstance(other, Grid):
            newgrid = Grid(self.w, self.h, self.Point)
            newgrid.grid = self.grid + other.grid
            return newgrid
        else:  # assume it targetting the actual numpy array
            self.grid.__add__(other)
            return self

    def __repr__(self):
        return str(self.grid.transpose())

    def get_shape(self):
        return (self.w, self.h)

    def out_of_bounds(self, pt):
        if pt.x < 0 or pt.y < 0:
            return True
        if pt.x >= self.w or pt.y >= self.h:
            return True
        return False

    def get_highest_value_point(self):
        ''' search all grid and return Point(x, y) of highest-value location in grid
        '''

    def get_all_tile_points_around_point(self, pt):
        verticals = [-1, 0 , 1]
        horizontals = [-1, 0, 1]
        tiles = set()
        for vertical in verticals:
            for horizontal in horizontals:
                if vertical == horizontal == 0:
                    continue  # skip returning the center point itself
                move = self.Point(horizontal, vertical)
                newpoint = pt + move
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
        w, h = self.shape
        y = 0
        top = [self.Point(x, y) for x in range(w) if self[self.Point(x, y)] == self.TILE]
        y = h - 1
        bottom = [self.Point(x, y) for x in range(w) if self[self.Point(x, y)] == self.TILE]
        x = 0
        left = [self.Point(x, y) for y in range(h) if self[self.Point(x, y)] == self.TILE]
        x = w - 1
        right = [self.Point(x, y) for y in range(h) if self[self.Point(x, y)] == self.TILE]
        for pt in left + right + top + bottom:
            edges.add(pt)
        return edges

    def get_points_neighboring_gaps(self):
        allNeighbors = set()
        w, h = self.shape
        for x in range(w):
            for y in range(h):
                pt = self.Point(x, y)
                if self[pt] == self.GAP:  # we found a gap
                    nearbyToGap = self.get_visible_tile_points_around_point(pt)
                    allNeighbors = allNeighbors.union(nearbyToGap)
        return allNeighbors

    def set_player_points(self, points):
        for pt in points:
            self[pt] = self.PLAYER

    def set_gap_points(self, points):
        for pt in points:
            self[pt] = self.GAP

    def get_points_of_type(self, ptype):
        pts = set()
        w, h = self.shape
        for x in range(w):
            for y in range(h):
                pt = self.Point(x, y)
                if self[pt] == ptype:
                    pts.add(pt)
        return pts

    def get_player_points(self):
        return self.get_points_of_type(self.PLAYER)

    def get_tile_points(self):
        return self.get_points_of_type(self.TILE)

    def get_gap_points(self):
        return self.get_points_of_type(self.GAP)

    def point_contains_type(self, pt, ptype):
        if self.out_of_bounds(pt):
            return False
        return self[pt] == ptype
    
    def contains_player(self, pt):
        return self.point_contains_type(pt, self.PLAYER)

    def contains_tile(self, pt):
        return self.point_contains_type(pt, self.TILE)

    def contains_gap(self, pt):
        return self.point_contains_type(pt, self.GAP)

        
if __name__ == '__main__':
    class Point:
        def __init__(self, x, y):
            self.x, self.y = x, y
            self.xy = (x, y)
        def __repr__(self):
            return str(self.xy)
            
    gapPts = [Point(2, 3), Point(1, 1), Point(0, 0)]
    playerPt = Point(1,2)  # put player there
    grid = Grid(4,4, Point)
    grid.set_player_points([playerPt])
    grid.set_gap_points(gapPts)
    print(grid)
    print(grid.get_gap_points())
    print(grid.get_player_points())
    print(grid.get_tile_points())
    for pt in grid.get_gap_points():
        print(grid.contains_gap(pt))  # True
        print(grid.contains_tile(pt))  # False
