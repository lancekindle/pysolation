import board


class Robot(object):
    """ controller for any non-humanControlled playing tokens. Using a board-representation, it can decide where
    to move, and what tiles to remove. Calls to the Robot must be made for each turn: moving or removing.
    """


class RobotGameBoard(board.GameBoard):

    def set_num_robot_players(self, num):
        for i, player in enumerate(self.players[:num]):
            player.humanControlled = False  # set robots as first NUM players


class RobotGame(board.Game):
    # all game needs to do is trigger a POST request after ~ 1 second to request url: /robot_takes_turn/
    # ... on the html page. if the active player is a robot

    def setup(self, numPlayers=2, shape=(9,9), numRobots=0):
        self.board = self.GameBoard()
        self.board.Player = self.Player  # set up proper inheritance
        self.board.Tile = self.Tile
        self.board.setup(shape)
        self.board.add_players(numPlayers + numRobots)
        self.board.set_num_robot_players(numRobots)
        self.turnType = self.MOVE_PLAYER  # first player's turn is to move
        self.get_active_player().active = True

    def robot_takes_turn(self):
        """ if active player is robot (AI), will guide robot into taking part of its turn (remove-tile or move-player) """
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            return
        if self.turnType == self.REMOVE_TILE:
            remove_tile_fxn = super(RobotGame, self).player_removes_tile
            activePlayer.take_remove_tile_turn(remove_tile_fxn)
        elif self.turnType == self.MOVE_PLAYER:
            move_player_fxn = super(RobotGame, self).player_moves_player
            activePlayer.take_move_player_turn(move_player_fxn)
        elif self.turnType == self.GAME_OVER:
            pass  # game over, we do nothing
        else:
            raise  # problem with our logic
    
    def player_removes_tile(self, x, y):
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_removes_tile(x, y)

    def player_moves_player(self, x, y):
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_moves_player(x, y)
