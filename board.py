import numpy as np
import math

class Coordinate:

    def __init__(self, xfloat, yfloat):
        self.x = math.floor(xfloat)
        self.y = math.floor(yfloat)
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
        if obj == self:
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
    REMOVE_TILE = 5
    MOVE_PLAYER = 6

    def __init__(self, size=(8,8)):
        w, h = size
        self.w = w
        self.h = h
        rows = []
        for x in range(w):
            col = [Tile(x,y) for y in range(h)]
            rows.append(col)
        self.board = np.array(rows)
        self.players = [] # first player in list ALWAYS has turn
        self.turnType = self.MOVE_PLAYER  # first player's turn is to move

    def add_players(self, qty):
        startingPositions = self.get_starting_positions_for_players(qty)
        self.players = [None]*qty
        for i in range(qty):
            p = Player(*startingPositions[i])
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

    def get_at(self, x, y):
        return self.board[x, y]

    def get_player_at(self, x, y):
        return self.get_at(x, y).player

    def set_at(self, x, y, item):
        self.board[x, y] = item

    def remove_at(self, x, y):
        self.board[x, y].visible = False

    def get_tiles_around(self, x, y):
        # returns tiles around AND including x, y
        xsmall = max(0, x - 1)
        xbig = min(self.w, x + 2)
        ysmall = max(0, y - 1)
        ybig = min(self.h, y + 2)
        return self.board[xsmall:xbig, ysmall:ybig]

    def is_valid_player_move(self, player, x, y):
        if not self.get_at(x, y).visible:
            return False
        if not self.get_at(x, y) in self.get_platforms_around(player.x, player.y):
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def is_valid_tile_remove(self, x, y):
        if not self.get_at(x, y).visible:
            return False
        if self.get_at(x, y).solid:
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def move_player(self, player, x, y):
        tile = self.get_at(player.x, player.y)
        tile.player = None
        player.move_to(x, y)
        target = self.get_at(x, y)
        target.player = player

    def remove_tile(self, tile):
        tile.set_visible(False)

    def is_player_trapped(self, player):
        for tile in get_tiles_around(player.x, player.y):
            if is_valid_player_move(player, tile.x, tile.y):
                return False
        return True

    def is_game_over(self):
        for player in players[1:]:
            if not is_player_trapped(player):
                return False
        return True
        


class Game:

    def __init__(self):
        self.board = GameBoard()
        self.board.add_players(3)

    def start_game(self):
        pass
        

    

    

    
        


# only run this code if run directly, NOT imported
if __name__ == '__main__':
##    b = GameBoard()
##    board = b.board
    game = Game()
    board = game.board.board
    print(board)
