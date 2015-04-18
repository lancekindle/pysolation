import numpy as np
import math
import AI
from Grid import Grid
import Astar

class Coordinate:

    def __init__(self, xfloat, yfloat):
        self.x = math.floor(xfloat)
        self.y = math.floor(yfloat)
        self.xy = (self.x, self.y)
        self.xfloat = xfloat
        self.yfloat = yfloat

class Tile:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = True
        self.solid = False
        self.player = None

    def __repr__(self):
        pos = str(self.x) + ',' + str(self.y)
        player = '' if self.player is None else self.player.color + '@'
        return player + pos

    def __eq__(self, obj):
        # match both the tile and player
        # so that we can match if a player is IN board[x,y]
        if obj is None:
            return False
        if obj == self.player:
            return True
        if obj is self:
            return True
        return False

    def set_visible(self, tf):
        self.visible = tf


class Player:
    colors = ["#FF0000", "#0000FF", "#00FF00", "#FF00FF", "#00FFFF", "#FFFF00"]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = self.colors.pop(0)
        self.colors.append(self.color)  # put first color at end of list
        self.gameOver = False

    def move_to(self, x, y):
        """ should only be called by board's move_to() function
        """
        self.x = x
        self.y = y


class GameBoard:
    Player = Player
    Tile = Tile
    board = None
    shape = (0, 0)

    def to_numpy_grid(self):
        ''' returns a numpy array representing the state of the tiles. 
        0 = invisible / removed, 1 = present, -1 = player occupying location
        '''
        h, w = self.shape
        grid = np.zeros((h, w))
        for x in range(w):
            for y in range(h):
                if self.board[x, y].visible:
                    grid[y, x] += 1
                if self.board[x, y].player:
                    grid[y, x] -= 2
        return grid

    def __iter__(self):
        for x in range(self.w):
            for y in range(self.h):
                yield x, y, self.board[x, y]
    
    def setup(self, size=(8,8)):
        w, h = size
        self.shape = (h, w)
        self.w = w
        self.h = h
        rows = []
        for x in range(w):
            col = [self.Tile(x,y) for y in range(h)]
            rows.append(col)
        self.board = np.array(rows)
        self.players = [] # first player in list ALWAYS has turn

    def __getitem__(self, *args):
        return self.board.__getitem__(*args)

    def __setitem__(self, *args):
        self.board.__setitem__(*args)

    def __str__(self):
        return str(self.board.transpose())  # transpose because numpy's representation will show x/y reversed

    def add_players(self, qty):
        startingPositions = self.get_starting_positions_for_players(qty)
        self.players = [None]*qty
        for i in range(qty):
            p = self.Player(*startingPositions[i])
            self.players[i] = p
            self.move_player(p, p.x, p.y)

    def out_of_bounds(self, x, y):
        w, h = self.w, self.h
        if x >= w or y >= h:
            return True
        if x < 0 or y < 0:
            return True
        return False

    def get_next_tile_coordinate_from(self, x, y, radians):
        floor = math.floor
        xf =floor(x)
        yf = floor(y)
        while floor(x) == xf and floor(y) == yf:
            x += 0.1 * math.cos(radians)
            y += 0.1 * math.sin(radians)
        return (x, y)

    def get_target_position_from(self, x, y, radians):
        while not self.out_of_bounds(x, y):
            validX, validY = x, y
            x, y = self.get_next_tile_coordinate_from(x, y, radians)
        return (validX, validY)
    
    def get_starting_positions_for_players(self, qty):
        positions = []
        midx, midy = float(self.w / 2.0), float(self.h / 2.0)
        for i in range(qty):
            fraction = 1.0 * i / qty
            radians = 2.0 * math.pi * fraction
            x, y = self.get_target_position_from(midx, midy, radians)
            pos = (math.floor(x), math.floor(y))
            positions.append(pos)
        return positions

    def get_player_at(self, x, y):
        return self[x, y].player

    def remove_at(self, x, y):
        self.board[x, y].visible = False

    def get_tiles_around(self, x, y):
        # returns tiles around AND including x, y
        # return tiles is in a mini 2D numpy array
        xsmall = max(0, x - 1)
        xbig = min(self.w, x + 2)
        ysmall = max(0, y - 1)
        ybig = min(self.h, y + 2)
        return self.board[xsmall:xbig, ysmall:ybig]

    def is_valid_player_move(self, player, x, y):
        if not self[x, y].visible:
            return False
        if not self[x, y] in self.get_tiles_around(player.x, player.y):
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def is_valid_tile_remove(self, x, y):
        if not self[x, y].visible:
            return False
        if self[x, y].solid:
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def move_player(self, player, x, y):
        tile = self[player.x, player.y]
        tile.player = None
        player.move_to(x, y)
        target = self[x, y]
        target.player = player

    def remove_tile(self, tile):
        tile.set_visible(False)

    def is_player_trapped(self, player):
        for row in self.get_tiles_around(player.x, player.y):
            for tile in row:
                if self.is_valid_player_move(player, tile.x, tile.y):
                    return False
        return True

    def convert_to_grid(self):
        grid = Grid(self.w, self.h, Astar.PathPoint)
        gaps = []
        players = []
        for x, y, tile in self:
            if not tile.visible:
                gaps.append(Astar.PathPoint(x, y))
            if tile.player:
                players.append(Astar.PathPoint(x, y))
        grid.set_gap_points(gaps)
        grid.set_player_points(players)
        return grid


class Game:
    REMOVE_TILE = 5
    MOVE_PLAYER = 6
    GameBoard = GameBoard
    Player = Player
    Tile = Tile

    def setup(self):
        self.board = self.GameBoard()
        self.board.Player = self.Player  # set up proper inheritance
        self.board.Tile = self.Tile
        self.board.setup()
        self.board.add_players(2)
        self.turnType = self.MOVE_PLAYER  # first player's turn is to move
    
    def get_active_player(self):
        return self.board.players[0]
    
    def setup_next_turn(self):
        # check for game over
        if self.is_game_over():
            self.end_game()
            return
        if self.turnType == self.MOVE_PLAYER:
            self.turnType = self.REMOVE_TILE
            return
        elif self.turnType == self.REMOVE_TILE:
            self.turnType = self.MOVE_PLAYER
            player = self.board.players.pop(0)
            self.board.players.append(player)

    def end_game(self):
        pass

    def is_game_over(self):
        for player in self.board.players[1:]:
            if not self.board.is_player_trapped(player):
                return False
        return True

    def player_removes_tile(self, x, y):
        if self.turnType == self.REMOVE_TILE and self.board.is_valid_tile_remove(x, y):
            self.board.remove_at(x, y)
            self.setup_next_turn()

    def player_moves_player(self, x, y):
        player = self.get_active_player()
        if self.turnType == self.MOVE_PLAYER and self.board.is_valid_player_move(player, x, y):
            self.board.move_player(player, x, y)
            self.setup_next_turn()


# only run this code if run directly, NOT imported
if __name__ == '__main__':
    game = Game()
    game.setup()
    board = game.board
    print(board)
