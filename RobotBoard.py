import board


class RobotPlayer(board.Player):
    # all player needs to do is trigger a POST request after ~ 1 second to request url: /robot_takes_turn/
    # ... on the html page.

    def __init__(self, *args, **kwargs):
        super(RobotPlayer, self).__init__(*args, **kwargs)
        self.humanControlled = True  # determine if player is a robot or not
        if 'robot' in kwargs and kwargs['robot'] == True:
            self.humanControlled = False  # mark this as a Robot

    def take_remove_tile_turn(self, remove_tile_fxn):
        pass

    def take_move_player_turn(self, move_player_fxn):
        pass


class RobotGameBoard(board.GameBoard):
    Player = RobotPlayer

    def add_players(self, humanQty, robotsQty=0):
        """ add players to the board in quantity specified, spacing them equally apart. Robot players are added after
        human players.
        """
        totalQty = humanQty + robotsQty
        startingPositions = self.get_starting_positions_for_players(totalQty)
        self.players = [None]*totalQty
        for i in range(humanQty):
            p = self.Player(*startingPositions[i])
            self.players[i] = p
            self.move_player(p, p.x, p.y)
        for i in range(humanQty, totalQty):
            p = self.Player(*startingPositions[i], robot=True)
            self.players[i] = p
            self.move_player(p, p.x, p.y)


class RobotGame(board.Game):
    Player = RobotPlayer

    def setup(self, numPlayers=2, shape=(9,9), numRobots=0):
        self.board = self.GameBoard()
        self.board.Player = self.Player  # set up proper inheritance
        self.board.Tile = self.Tile
        self.board.setup(shape)
        self.board.add_players(numPlayers, numRobots)
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
