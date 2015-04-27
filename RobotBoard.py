import board
import random

class Robot(object):
    """ controller for any non-humanControlled playing tokens. Using a board-representation, it can decide where
    to move, and what tiles to remove. Calls to the Robot must be made for each turn: moving or removing.
    """

    def __init__(self, game, board, player):
        self.game = game  # keep reference of game for tracking success of move
        self.board = board  # keep reference to the board and player for calculations
        self.player = player
    
    def take_move_player_turn(self, move_player_fxn):
        # if this move fails, you should call super(self) to ask the previous robot to try its move.
        # if all moves fail, eventually it'll reach this base Robot class, which moves to a random available tile
        x, y = self.player.x, self.player.y
        tiles = self.board.get_open_tiles_around(x, y)
        target = random.choice(tiles)
        move_player_fxn(target.x, target.y)

    def take_remove_tile_turn(self, remove_tile_fxn):
        """ remove a random available tile. """
        tiles = self.board.get_all_open_removable_tiles()
        target = random.choice(tiles)
        remove_tile_fxn(target.x, target.y)


class RobotGameBoard(board.GameBoard):

    def set_num_robot_players(self, numRobots):
        if numRobots < 1:
            return
        numPlayers = len(self.players)
        n = numPlayers / numRobots  # n is a ratio
        for player in self.players[::n]:  # every nth  player is a robot, so we sample every nth player
            if numRobots:  # stop once numRobots has been reached
                player.humanControlled = False
                numRobots -= 1


class RobotGame(board.Game):
    # all game needs to do is trigger a POST request after ~ 1 second to request url: /robot_takes_turn/
    # ... on the html page. if the active player is a robot

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
        self.board.set_num_robot_players(numRobots)
        for player in self.board.players:
            if not player.humanControlled:
                robot = Robot(self, self.board, player)
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
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_removes_tile(x, y)

    def player_moves_player(self, x, y):
        activePlayer = self.get_active_player()
        if activePlayer.humanControlled:
            super(RobotGame, self).player_moves_player(x, y)
