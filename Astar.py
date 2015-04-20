import numpy as np
import math
import weakref
from Grid import Grid


class PathPoint(object):
    ''' cost and location of a point. When comparing, only location matters
    '''
    _goal = None
    __instances__ = set()
    
    def __init__(self, x, y, cost=0):
        self.cost = float(cost)
        self.pathCost = cost
        self.x = x
        self.y = y
        self.xy = (x, y)
        if self._goal:
            self._recalculate_total_cost()
        self.__instances__.add(weakref.ref(self))

    def __getitem__(self, i):
        return self.xy[i]

    def __eq__(self, other):
        return self.xy == other.xy

    def __cmp__(self, other):
        ''' for sorting points. compare pathCost first, then (if tied), distance to goal.
        '''
        if not self.pathCost == other.pathCost:
            if self.pathCost > other.pathCost:
                return 1
            return -1
        if not self.distanceToGoal == other.distanceToGoal:
            if self.distanceToGoal > other.distanceToGoal:
                return 1
            return -1
        return 0

    def __hash__(self):
        ''' for set(). a set requires a hash in order to work
        '''
        return int(self.x * 10000000 + self.y * 10000 + self.cost)

    def __add__(self, other):
        pt = self.__class__(self.x + other.x, self.y + other.y,
                   self.cost + other.cost)
        return pt
        
    def __sub__(self, other):
        pt = self.__class__(self.x - other.x, self.y - other.y,
                   self.cost - other.cost)
        return pt
        
    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            num = other
            return self.__class__(self.x * num + self.y * num, self.cost * num)
        x, y = self.x * other.x, self.y * other.y
        return self.__class__(x, y, self.cost * other.cost)

    def __str__(self):
        return str(self.x) + ',' + str(self.y) + ': ' + str(self.pathCost)

    def __repr__(self):
        return str(self)

    def _recalculate_total_cost(self):
        self.distanceToGoal = self.exaggerated_distance_to(self._goal)
        self.pathCost = self.cost + self.distanceToGoal

    @classmethod
    def set_goal(cls, goal):
        ''' set endpoint goal. This is the ending goal that A* should finish on.
            In this case, we set a class-wide Point as the goal, so that each point
            can immediately calculate the distance from the goal
            ONLY change this AFTER you've already calculated the full path to traverse
        '''
        cls._goal = goal
        dead = set()
        for ref in cls.__instances__:
            point = ref()
            if point is not None:
                point._recalculate_total_cost()
            else:
                dead.add(ref)
        cls.__instances__ -= dead

    def distance_to(self, point):
        x2 = float((point.x - self.x))**2
        y2 = float((point.y - self.y))**2
        return math.sqrt(x2 + y2)

    def exaggerated_distance_to(self, point):
        ''' calculates distance to point with worst-case scenario: have to jump only orthoganally
        + the actual calculated distance to the passed point
        '''
        xdif, ydif = abs(point.x - self.x), abs(point.y - self.y)
        return xdif + ydif + self.distance_to(point)


class PathStep(PathPoint):

    def __init__(self, dx, dy, cost=1):
        super(PathStep, self).__init__(dx, dy, cost)

    @classmethod
    def get_orthogonal_steps(cls, cost=1):
        ''' return points for left, right, up, down, and stay
        '''
        left = PathStep(-1, 0, cost)
        right = PathStep(1, 0, cost)
        up = PathStep(0, -1, cost)
        down = PathStep(0, 1, cost)
        return left, right, up, down

    @classmethod
    def get_diagonal_steps(cls, cost=1):
        upperLeft = PathStep(-1, -1, cost)
        upperRight = PathStep(1, -1, cost)
        lowerLeft = PathStep(-1, 1, cost)
        lowerRight = PathStep(1, 1, cost)
        return upperLeft, upperRight, lowerLeft, lowerRight

    @classmethod
    def get_all_8_directions(cls, orthogonalCost=1, diagonalCost=1):
        l, r, u, d = cls.get_orthogonal_steps(orthogonalCost)
        ul, ur, ll, lr = cls.get_diagonal_steps(diagonalCost)
        return l, r, u, d, ul, ur, ll, lr


class PathFinder:
    frontier = None
    xy = None
    goal = None
    movesToUse = None
    explored = None
    grid = None

    def __init__(self, grid, startPoint, goalPoint, movesToUse=None):
        self.frontier = []
        self.grid = grid
        self.xy = []  # kinda like explored already nodes
        self.explored = []
        self.goal = PathPoint(goalPoint.x, goalPoint.y)
        PathPoint.set_goal(self.goal)
        if movesToUse is None:
            movesToUse = PathStep.get_all_8_directions()
        self.movesToUse = movesToUse
        self.startPoint = PathPoint(startPoint.x, startPoint.y)
        self.add_point_to_frontier(self.startPoint)

    def add_point_to_frontier_if_valid(self, point):
        ''' check that point is unique, unexplored, and not a gap or player point, then adds it if valid
        :param point: PathPoint for location to be added
        :return:None
        '''
        if point in self.frontier or point in self.explored: # we have explored this point previously
            return
        if not self.grid.contains_tile(point):
            return  # skip point that is not a tile. (maybe a gap or player or out of bounds instead)
        self.add_point_to_frontier(point)

    def add_point_to_frontier(self, point):
        ''' Add point to frontier, no checks made. Usually this is only called during initialization
        :param point: PathPoint
        :return:
        '''
        self.xy.append(point.xy)
        self.frontier.append(point)
        self.frontier.sort()

    def pop_from_frontier(self, index=0):
        ''' pop off best path-cost point, and add it to list of explored nodes
        '''
        pt = self.frontier.pop(index)
        self.explored.append(pt)
        return pt

    def goal_is_reached(self):
        ''' determines if one of the current point has reached the goalPoint
        '''
        if self.goal in self.frontier or self.goal in self.explored:
            return True
        return False

    def march_until_goal_reached(self):
        while not self.goal_is_reached():
            bestPoint = self.pop_from_frontier()
            for move in self.movesToUse:
                newSpot = bestPoint + move
                self.add_point_to_frontier_if_valid(newSpot)

    def get_best_path(self):
        self.march_until_goal_reached()
        traceback = self.get_traceback()
        if len(traceback) < 2:  # then we have a problem. The path
            # should always be at least start, finish.
            raise UserWarning('traceback returned <2 points! A* path is bad')
        path = [pt for pt in reversed(traceback)]  # 0th point is starting point
        return path[1:]  # discard starting point
        
    def get_traceback(self):
        ''' get a traceback of coordinates from the current best frontier point to the start.(inclusive)
        using previously explored nodes and useable moves.
        if march_until_goal_reached() was called prior, the returned traceback should return a path from goal to start.
        '''
        closestPt = self.pop_from_frontier()
        if not closestPt == self.goal:
            print('last frontier point coordinate not same as goal. A* will be truncated')
        tracebackPoints = [closestPt]  # we add pt instead of self.goal because pt has correct cost
        traceback = tracebackPoints[-1]
        while self.explored:  # until we've exausted the list
            point = self.explored.pop(-1)  # access last element is lowest cost
                # lowest cost point is closest to goal. So long as we prove that it was
                # within move range from the previous one
            for move in self.movesToUse:
                if point.pathCost < traceback.pathCost:  # point.pathCost should be >= the current
                    break                   # traceback Pt. if not, then we know that this is a bifurcation
                if (point - move) == traceback:  # then this is within moving distance from our previous point
                    tracebackPoints.append(point)
                    traceback = point  # new point to match
                    break
        return tracebackPoints


if __name__ == '__main__':
    grd = Grid(4, 4, PathPoint)
    go = PathPoint(3,3)
    st = PathPoint(0,1)
    moven = PathStep.get_all_8_directions()
    moven  = PathStep.get_orthogonal_steps()
    #movements = PathStep.get_diagonal_steps()
    pf = PathFinder(grd, st, go) #, mmovements)
    path = pf.get_best_path()  # goal should have lowest cost
    print(path)
    # backtrack through explored points, choosing lowest cost
    # lowest-cost points should be closest to goal. And yet, at some point if there was a bifurcation, then
    # lowest-cost does not always mean it follows the best path
    # so you'll need to choose the next lowest path, so long as the next lowest (will be => closer path)
    # path cost
    # as you trace backwards, cost should go up:
    # farther.cost >= closer_to_goal.cost
    # and it mostly needs to follow a nearby path.
    # in other words, the you need to find another point whose cost >= current backtrack cost
    # AND you can get to that points.xy from the current point using the supplied movements.
    # MAKE SURE to use farther + move and compare to closer_to_goal

    # taken from board object
    def convert_to_grid(self):
        """  """
        grid = Grid(self.w, self.h, PathPoint)
        gaps = []
        players = []
        for x, y, tile in self:
            if not tile.visible:
                gaps.append(PathPoint(x, y))
            if tile.player:
                players.append(PathPoint(x, y))
        grid.set_gap_points(gaps)
        grid.set_player_points(players)
        return grid

