import board
import random
import BoardAnalyzer

class Robot(object):
    """ controller for any non-humanControlled playing tokens. Using a board-representation, it can decide where
    to move, and what tiles to remove. Calls to the Robot must be made for each turn: moving or removing. Future
    inheriting classes, should they fail in taking a turn, should call super() on their take_move_player_turn and
    take_remove_tile_turn, since these base functions will take any possible turn.
    """

    def __init__(self, game, board, player):
        self.game = game  # keep reference of game for tracking success of move
        self.board = board  # keep reference to the board and player for calculations
        self.player = player
    
    def take_move_player_turn(self, move_player_fxn):
        """ move player token to a random nearby tile """
        x, y = self.player.x, self.player.y
        tiles = self.board.get_landable_tiles_around(x, y)
        target = random.choice(tiles)
        move_player_fxn(target.x, target.y)

    def take_remove_tile_turn(self, remove_tile_fxn):
        """ remove a random tile around a random player (that isn't MY player). If that isn't possible, remove
        a random tile that's not around my player. If that isn't possible, remove a random tile.
        """
        tilesAroundOpponents = []
        for player in self.board.players:
            if not player == self.player:
                x, y = player.x, player.y
                nearbyTiles = self.board.get_removable_tiles_around(x, y)
                tilesAroundOpponents.extend(nearbyTiles)
        tilesAroundOpponents = set(tilesAroundOpponents)
        x, y = self.player.x, self.player.y
        tilesAroundMe = set(self.board.get_removable_tiles_around(x, y))  # tiles around controlled player (me)
        safelyAroundOpponents = list(tilesAroundOpponents - tilesAroundMe)  # tiles around opponents but not around me
        removableTiles = set(self.board.get_all_open_removable_tiles())  # all removable tiles
        safelyRemovable = list(removableTiles - tilesAroundMe)  # all removable tiles except those around me
        target = random.choice(list(removableTiles))  # worst-case scenario. If other options fail, target tile will be, by logic,
                # those around the player token itself
        if safelyAroundOpponents:
            target = random.choice(safelyAroundOpponents)
        elif tilesAroundOpponents:  # likely that I'm next to other player. I'll have to remove a tile available for both of us
            target = random.choice(list(tilesAroundOpponents))
        elif safelyRemovable:  # no open spots to remove around players can only happen if solid unremovable tiles exist
            target = random.choice(safelyRemovable)
        remove_tile_fxn(target.x, target.y)

class RunnerBot(Robot):
    """ RunnerBot moves toward open, escapable tiles """
    
    def take_move_player_turn(self, move_player_fxn):
        x, y = self.player.x, self.player.y
        grid = self.board.to_number_grid(players=0, gaps=0, tiles=1)  # set all tiles to 1, and players and gaps to 0
        sweetspotter = BoardAnalyzer.SweetSpotGrid(grid)
        x, y = sweetspotter.get_next_move_toward_sweet_spot(grid, x, y)
        move_player_fxn(x, y)


class RobotGameBoard(board.GameBoard):
    """ allow defining robots in board """

    def set_num_robot_players(self, numRobots):
        if numRobots < 1:
            return
        numPlayers = len(self.players)
        n = int(numPlayers / numRobots)  # n is a ratio
        for player in self.players[::n]:  # every nth  player is a robot, so we sample every nth player
            if numRobots:  # stop once numRobots has been reached
                player.humanControlled = False
                numRobots -= 1


class RobotGame(board.Game):
    """ game handles adding robots to gameplay """

    def setup(self, numPlayers=2, shape=(9,9), numRobots=0):
        self.board = self.GameBoard()
        self.board.Player = self.Player  # set up proper inheritance
        self.board.Tile = self.Tile
        self.board.setup(shape)
        self.board.add_players(numPlayers + numRobots)
        self.robots = dict()
        self.setup_robots(numRobots)
        self.turnType = self.MOVE_PLAYER  # first player's turn is to move
        self.get_active_player().active = True

    def setup_robots(self, numRobots):
        """ set up robots to handle appropriate number player token """
        self.board.set_num_robot_players(numRobots)
        for player in self.board.players:
            if not player.humanControlled:
                robot = RunnerBot(self, self.board, player)
                self.robots[player] = robot

    def robot_takes_turn(self):
        """ if active player is robot (AI), will guide robot into taking part of its turn (remove-tile or move-player) """
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            return
        activeRobot = self.robots[activePlayer]
        if self.turnType == self.REMOVE_TILE:
            remove_tile_fxn = super(RobotGame, self).player_removes_tile
            activeRobot.take_remove_tile_turn(remove_tile_fxn)
        elif self.turnType == self.MOVE_PLAYER:
            move_player_fxn = super(RobotGame, self).player_moves_player
            activeRobot.take_move_player_turn(move_player_fxn)
        elif self.turnType == self.GAME_OVER:
            pass  # game over, we do nothing
        else:
            raise  # problem with our logic
    
    def player_removes_tile(self, x, y):
        """ if active player is human, carry out function. Otherwise exit """
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_removes_tile(x, y)

    def player_moves_player(self, x, y):
        """ if active player is human, carry out function. Otherwise exit """
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_moves_player(x, y)
