import numpy as np
import math


#=================================================================
class _GamePieceAccess:

    def iter(self):
        for x in range(self.w):
            for y in range(self.h):
                yield x, y, self.dict_board[x, y]

    def get(self, x, y):
        return self.dict_board.__getitem__((x, y))

    def set(self, x, y):
        self.dict_board.__setitem__((x, y))

    def get_player_at(self, x, y):
        """ return player attribute of tile at specified x, y coordinates """
        return self.get(x, y).player

    def remove_at(self, x, y):
        """ "Remove" Tile at specified coordinate. This will set the visible attribute to False """
        self.dict_board[x, y].visible = False
        return self.dict_board[x, y]

    def move_player(self, player, x, y):
        """ move player from occupied tile to tile @ x, y coordinates. """
        tile = self.get(player.x, player.y)
        tile.player = None
        player.move_to(x, y)
        target = self.get(x, y)
        target.player = player


#=================================================================
class _BoardSetup(_GamePieceAccess):
    Player = None
    Tile = None
    board = None
    shape = (0, 0)

    def setup(self, size=(9,9)):
        """ populate board with Tiles, according to the size argument

        :param size: size of board to construct in (x, y) format.
        """
        w, h = size
        self.shape = (h, w)
        self.w = w
        self.h = h
        self.fill_board(w, h)
        self.players = []

    def fill_board(self, w, h):
        rows = []
        for x in range(w):
            col = [self.Tile.create(x,y) for y in range(h)]
            rows.append(col)
        self.dict_board = np.array(rows)

    def add_players(self, qty):
        """ add players to the board in quantity specified, spacing them equally apart """
        startingPositions = self.get_starting_positions_for_players(qty)
        self.players = [None]*qty
        for i in range(qty):
            p = self.Player.create(*startingPositions[i])
            self.players[i] = p
            self.move_player(p, p.x, p.y)

    def _get_next_tile_coordinate_from(self, x, y, radians):
        """ calculate next available integer coordinates given x, y float coordinates, and an angle to follow """
        floor = math.floor
        xf =floor(x)
        yf = floor(y)
        while floor(x) == xf and floor(y) == yf:
            x += 0.1 * math.cos(radians)
            y += 0.1 * math.sin(radians)
        return (x, y)

    def _get_last_valid_coordinate_along_vector(self, x, y, radians):
        """ calculate coordinates along vector (given x, y and angle to follow) and return last valid coordinates """
        while not self.out_of_bounds(x, y):
            validX, validY = x, y
            x, y = self._get_next_tile_coordinate_from(x, y, radians)
        return (validX, validY)
    
    def get_starting_positions_for_players(self, qty):
        """ calculate (x, y) coordinates for qty of players, equally distributing them around the edges of the board """
        positions = []
        midx, midy = float(self.w / 2.0), float(self.h / 2.0)
        for i in range(qty):
            fraction = 1.0 * i / qty
            radians = 2.0 * math.pi * fraction
            x, y = self._get_last_valid_coordinate_along_vector(midx, midy, radians)
            pos = (math.floor(x), math.floor(y))
            positions.append(pos)
        return positions


class _TileFinder(_BoardSetup):
    
    def get_tiles_around(self, x, y):
        """ :return: 1-D numpy array of tiles surrounding given coordinate, including tile @ coordinate itself """
        xsmall = max(0, x - 1)
        xbig = min(self.w, x + 2)
        ysmall = max(0, y - 1)
        ybig = min(self.h, y + 2)
        miniboard = []
        for x in range(xsmall, xbig):
            for y in range(ysmall, ybig):
                miniboard.append(self.dict_board[x, y])
        return miniboard

    def get_landable_tiles_around(self, x, y):
        """ return list of tiles around x, y that are open for movement. Do NOT use this for finding tiles to remove;
        this list includes solid tiles, which are not removable
        """
        tiles = self.get_tiles_around(x, y)
        openTiles = []
        for tile in tiles:
            if not tile.visible:
                continue
            if self.get_player_at(tile.x, tile.y):
                continue
            openTiles.append(tile)
        return openTiles

    def get_removable_tiles_around(self, x, y):
        """ return list of tiles neighboring the x, y coordinates that can be removed this turn """
        tiles = self.get_tiles_around(x, y)
        removable = []
        for tile in tiles:
            if not tile.visible:
                continue
            if tile.solid:
                continue
            x, y = tile.x, tile.y
            if self.get_player_at(x, y):
                continue
            removable.append(tile)
        return removable

    def get_all_open_removable_tiles(self):
        """ return list of all tiles available to remove on the board """
        removable = []
        for x, y, tile in self.iter():
            if not tile.visible:
                continue
            if self.get_player_at(x, y):
                continue
            if tile.solid:
                continue
            removable.append(tile)
        return removable


#=================================================================
class _RuleValidator(_TileFinder):
    
    def out_of_bounds(self, x, y):
        """ Return True if coordinates x, y are outside the boundaries of the GameBoard. Return False if a Tile is
        accessible at those coordinates
        """
        w, h = self.w, self.h
        if x >= w or y >= h:
            return True
        if x < 0 or y < 0:
            return True
        return False

    def is_valid_player_move(self, player, x, y):
        """ :return: True if x, y coordinate is an open tile, visible, and next to the specified player, False otherwise. """
        if not self.get(x, y).visible:
            return False
        if not self.get(x, y) in self.get_tiles_around(player.x, player.y):
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def is_valid_tile_remove(self, x, y):
        """ :return: True if Tile is visible on board, not solid, and unoccupied by a player, False otherwise. """
        if not self.get(x, y).visible:
            return False
        if self.get(x, y).solid:
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def is_player_trapped(self, player):
        """ determine if player token is unable to move from current position.
        :param player: player instance to check
        :return: False if any tiles surrounding player is a valid move, True otherwise
        """
        for tile in self.get_tiles_around(player.x, player.y):
            if self.is_valid_player_move(player, tile.x, tile.y):
                return False
        return True    


#=================================================================
class GameBoard(_RuleValidator):
    """ GameBoard that holds the tiles and players in one place. Allow manipulation of Players and Tiles, and provide
    functions for gathering data about specific states of the GameBoard. After initilization, requires setup() function
    call in order to populate the GameBoard, then a call to add_players(x) to add x players to game

    Attributes:
        Player: reference to Player class. You can change which player class to instantiate by overriding this attribute
                with your own Player class. Easiest way to do this is to through inheriting GameBoard with your own
                GameBoard class.
        Tile:   reference to Tile class to use when populating the GameBoard. Just Like Player, you can overwrite this
                reference to use your own Tile class if desired.
        board:  The actual board: a numpy array of Tiles. the GameBoard class itself provides native get and set methods
                so that you do not have to access board directly. Instead, just use gameboard[x, y].
        shape:  a numpy-style shape describing shape of gameboard.
    """
    
    def to_number_grid(self, **kwargs):
        ''' returns a numpy array representing the state of the tiles. 
        defaults: 0 = invisible / removed, 1 = present, -1 = player occupying location
        '''
        playerVal = float(kwargs.get('players', -1))  # allow overriding of default values
        tileVal = float(kwargs.get('tiles', 1))
        gapVal = float(kwargs.get('gaps', 0))
        grid = np.zeros((self.w, self.h)) + gapVal
        for x in range(self.w):
            for y in range(self.h):
                if self.dict_board[x, y].player:
                    grid[x, y] = playerVal
                elif self.dict_board[x, y].visible:
                    grid[x, y] = tileVal
        return grid

    def __str__(self):
        b = ""
        for x in range(self.w):
            b += "\n"
            for y in range(self.h):
                b += str(self.dict_board[x,y])
        return b
