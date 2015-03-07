import numpy as np


class Tile:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visible = True
        self.solid = False
        self.player = None

    def __repr__(self):
        return 'tile@' + str(self.x) + ',' + str(self.y)

    def __eq__(self, obj):
        # match both the tile and player
        # so that we can match if a player is IN board[x,y]
        if obj == self.player:
            return True
        if obj == self:
            return True
        return False


class Player:

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.gameOver = False

    def move_to(self, x, y):
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

    def is_valid_platform_remove(self, x, y):
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
        
        
        
        
    
        
        

    

    

    
        


# only run this code if run directly, NOT imported
if __name__ == '__main__':
    b = GameBoard()
    board = b.board
