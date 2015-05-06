import numpy as np
import math


class Tile(object):
    """ A GameBoard is composed of rows and columns of Tiles. Each Tile has a specific x and y coordinate. It is up to
    the GameBoard setup to ensure a Tile has the correct x and y coordinates. When a Tile is NOT visible, it is
    considered removed from the Board, and can not be occupied by a Player.
    Tiles are considered "Landable" if a player can move onto it. "Removable" indicates the tile can be removed

    :Attributes
        visible: if the Tile has not been removed from the GameBoard. True=> NOT removed. False=> REMOVED FROM BOARD
        solid: specifies if Tile is removable. If True, Tile cannot be removed
        player: reference to player token. player = None if Tile is unoccupied. When checking if a player occupies a
            particular Tile, use player == tile, or player in board[i, j] also works
    """

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
        """ match both the tile and player
        so that we can match if a player is IN board[x,y]
        """
        if obj is None:
            return False
        if obj == self.player:
            return True
        if obj is self:
            return True
        return False

    def set_visible(self, tf):
        """
        :param tf: boolean True or False to set visible attribute.
        """
        self.visible = tf


class Player(object):
    """ Player is moved around the board, and is trapped once it cannot move on it's own turn.

    Attributes:
        x, y: x, y coordinate on the GameBoard
        color: the color of the player token.
        active: set to True when it is player's turn to move and remove tiles.
        disabled: permanently set to True when player has active turn and is unable to move. Usually this indicates
            player will remain inactive for the rest of the game.
        humanControlled: set to False if a robot is expected to control this Player Token's turn.
    """
    _colors = [("#FF0000", "Red"), ("#0000FF", "Blue"), ("#00FF00", "Green"),
               ("#FF00FF", "Purple"), ("#00FFFF", "Cyan"), ("#FFFF00", "Yellow")]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color, self.colorName = self._colors.pop(0)
        self._colors.append(self.color)  # put first color at end of class-wide list -> so next instance gets new color
        self.disabled = False
        self.active = False  # for determining style. Game will set Player's currentPlayer to True when it has turn
        self.humanControlled = True  # for determining which Players are robots / AI controlled

    def move_to(self, x, y):
        """ reassigns coordinates. Because it does not reassign player to Tile, this funciton should only be called by
        board's move_to() function
        """
        self.x = x
        self.y = y


class GameBoard(object):
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
    Player = Player
    Tile = Tile
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
        rows = []
        for x in range(w):
            col = [self.Tile(x,y) for y in range(h)]
            rows.append(col)
        self.board = np.array(rows)
        self.players = []

    def add_players(self, qty):
        """ add players to the board in quantity specified, spacing them equally apart """
        startingPositions = self.get_starting_positions_for_players(qty)
        self.players = [None]*qty
        for i in range(qty):
            p = self.Player(*startingPositions[i])
            self.players[i] = p
            self.move_player(p, p.x, p.y)

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

    def __getitem__(self, *args):
        return self.board.__getitem__(*args)

    def __setitem__(self, *args):
        self.board.__setitem__(*args)

    def __str__(self):
        return str(self.board.transpose())  # transpose because numpy's representation will show x/y reversed

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

    def get_player_at(self, x, y):
        """ return player attribute of tile at specified x, y coordinates """
        return self[x, y].player

    def remove_at(self, x, y):
        """ "Remove" Tile at specified coordinate. This will set the visible attribute to False """
        self.board[x, y].visible = False

    def get_tiles_around(self, x, y):
        """ :return: 1-D numpy array of tiles surrounding given coordinate, including tile @ coordinate itself """
        xsmall = max(0, x - 1)
        xbig = min(self.w, x + 2)
        ysmall = max(0, y - 1)
        ybig = min(self.h, y + 2)
        miniboard = self.board[xsmall:xbig, ysmall:ybig]
        return miniboard.flatten() # 1-D array of tiles

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
        for x, y, tile in self:
            if not tile.visible:
                continue
            if self.get_player_at(x, y):
                continue
            if tile.solid:
                continue
            removable.append(tile)
        return removable

    def is_valid_player_move(self, player, x, y):
        """ :return: True if x, y coordinate is an open tile, visible, and next to the specified player, False otherwise. """
        if not self[x, y].visible:
            return False
        if not self[x, y] in self.get_tiles_around(player.x, player.y):
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def is_valid_tile_remove(self, x, y):
        """ :return: True if Tile is visible on board, not solid, and unoccupied by a player, False otherwise. """
        if not self[x, y].visible:
            return False
        if self[x, y].solid:
            return False
        if self.get_player_at(x, y):
            return False
        return True

    def move_player(self, player, x, y):
        """ move player from occupied tile to tile @ x, y coordinates. """
        tile = self[player.x, player.y]
        tile.player = None
        player.move_to(x, y)
        target = self[x, y]
        target.player = player

    def is_player_trapped(self, player):
        """ determine if player token is unable to move from current position.
        :param player: player instance to check
        :return: False if any tiles surrounding player is a valid move, True otherwise
        """
        for tile in self.get_tiles_around(player.x, player.y):
            if self.is_valid_player_move(player, tile.x, tile.y):
                return False
        return True


class BoardExporter:
    """ allow exporting board to grid. Copies all relevant data from the board and then gives access to analyzing functions
    """
    def __init__(self, board):
        self._board = board

    def export_gap_points(self):
        """ return list of coordinates for removed tiles """
        gaps = []
        for x, y, tile in self._board:
            if not tile.visible:
                gaps.append((x, y))
        return gaps

    def export_player_points(self):
        """ return list of coordinates for players """
        players = []
        for x, y, tile in self._board:
            if tile.player:
                players.append(x, y)
        return players

    def export_board_size(self):
        """ return width and height of board """
        w, h = self._board.w, self._board.h
        return w, h


class Game(object):
    """ Game keeps track of the GameBoard and game-state. It is responsible for interfacing with the user/player,
    checking that any tile remove or player token move action is valid and then applying the action. It also keeps
    track of whose turn it is, and what type of turn it is (removing tile or moving player).

    Attributes:
        turnSuccessful: True or False if the last command (to move player or remove tile) was valid and executed
        turnType: type of turn, REMOVE_TILE or MOVE_PLAYER, or GAME_OVER
        board: reference to the gameboard.
    """
    REMOVE_TILE = 5
    MOVE_PLAYER = 6
    GAME_OVER = 4
    GameBoard = GameBoard
    Player = Player
    Tile = Tile
    turnSuccessful = False  # a status indicator only.
    turnType = None

    def setup(self, numPlayers=2, shape=(9,9)):
        """ set up board shape and populate players, set active player. After this, game will be ready to play """
        self.board = self.GameBoard()
        self.board.Player = self.Player  # set up proper inheritance
        self.board.Tile = self.Tile
        self.board.setup(shape)
        self.board.add_players(numPlayers)
        self.turnType = self.MOVE_PLAYER  # first player's turn is to move
        self.get_active_player().active = True
    
    def get_active_player(self):
        """ return player who has "control" of current turn """
        return self.board.players[0]

    def setup_next_active_player(self):
        """ Cycle through players, making next player active. Check that newly active player is not trapped. If trapped,
        mark player as inactive and cycle to next player. Inactive players will be skipped in future cycles.
        """
        trappedPlayerFound = True
        while trappedPlayerFound:  # stay in while loop until untrapped player found
            pastPlayer = self.board.players.pop(0)  # cycle to next player
            pastPlayer.active = False
            self.board.players.append(pastPlayer)
            activePlayer = self.get_active_player()
            activePlayer.active = True
            if self.board.is_player_trapped(activePlayer) or activePlayer.disabled:
                activePlayer.disabled = True  # set as if we just now discover active player is trapped
            else:
                trappedPlayerFound = False  # we found an untrapped player, and have set as active player.
    
    def setup_next_turn(self):
        """ Cycle game state from one turn to the next, cycling through active players as necessary. """
        if self.is_game_over():
            self.end_game()
            return
        if self.turnType == self.MOVE_PLAYER:
            self.turnType = self.REMOVE_TILE
            return
        elif self.turnType == self.REMOVE_TILE:
            self.turnType = self.MOVE_PLAYER
            self.setup_next_active_player()

    def end_game(self):
        """ perform end-game functions that ensure the game grinds to a halt """
        self.turnType = self.GAME_OVER

    def is_game_over(self):
        """ return True if all players--excluding active player--are either trapped or inactive (previously trapped) """
        for player in self.board.players[1:]:
            if not self.board.is_player_trapped(player) and not player.disabled:
                return False
        return True

    def player_removes_tile(self, x, y):
        """ take turn on game by removing tile. Checks that turn is valid, and afterwards rolls over to next turn """
        if self.turnType == self.REMOVE_TILE and self.board.is_valid_tile_remove(x, y):
            self.board.remove_at(x, y)
            self.setup_next_turn()
            self.turnSuccessful = True
        else:
            self.turnSuccessful = False

    def player_moves_player(self, x, y):
        """ take turn on game by moving player. Checks that turn is valid, and afterwards rolls over to next turn """
        player = self.get_active_player()
        if self.turnType == self.MOVE_PLAYER and self.board.is_valid_player_move(player, x, y):
            self.board.move_player(player, x, y)
            self.setup_next_turn()
            self.turnSuccessful = True
        else:
            self.turnSuccessful = False


# only run this code if run directly, NOT imported
if __name__ == '__main__':
    game = Game()
    game.setup()
    board = game.board
    print(board)
