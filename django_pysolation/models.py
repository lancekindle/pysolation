from __future__ import print_function
from django.db import models
import sys
import uuid as UUID
from HtmlBoard import HtmlGame, HtmlTile, HtmlGameBoard, HtmlPlayer

class Board(models.Model, HtmlGameBoard):
    creation = models.AutoField(primary_key=True)
    w = models.IntegerField()
    h = models.IntegerField()

    _players = []

    @property
    def players(self):
        """ get players list, from DB if necessary"""
        if not self._players:
            self._players = list(Player.objects.filter(board=self).order_by('active'))
            self._players.reverse()
        return self._players
    
    @players.setter
    def players(self, player_list):
        """ set players list """
        self._players = player_list

    def get(self, x, y):
        """ get tile from cache (board) or retrieve from database """
        try:
            return super(Board, self).get(x,y)
        except (KeyError, AttributeError) as err:
            if isinstance(err, AttributeError):
                self.fill_board(0,0)  # create board but don't fill
            tile = Tile.objects.filter(board=self, x=x, y=y)[0]
            self.set(x, y, tile)
            return tile
    
    def save(self, *args, **kwargs):
        """ save all players and tiles in database. Will only save currently loaded tiles """
        super(Board, self).save(*args, **kwargs)
        for tile in self.get_all_tiles():
            tile.board = self
            tile.save()
        for player in self.players:
            player.board = self
            player.save()
    
    def preload_tiles(self):
        """ preload all tiles back into dictionary. Currently, each board refresh redoes the whole board
            with get_html() calls that force all tiles to load
        """
        self.fill_board(0,0)  # create board but don't fill
        for tile in Tile.objects.filter(board=self):
            self.set(tile.x, tile.y, tile)

class Player(models.Model, HtmlPlayer):
    creation = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    ID = models.CharField(max_length=15)  # player_1, player_2, etc.
    x = models.IntegerField()
    y = models.IntegerField()
    color = models.CharField(max_length=15)
    colorName = models.CharField(max_length=31)
    disabled = models.BooleanField(default=False)    # True if player is unable to move
    active = models.BooleanField(default=False)  # True if it's players turn
    # all players are robots until a player is assigned to it
    humanControlled = models.BooleanField(default=False)
    assigned_user = models.CharField(max_length=100, default='')

class Tile(models.Model, HtmlTile):
    creation = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()
    ID = models.CharField(max_length=15)
    visible = models.BooleanField(default=True)
    solid = models.BooleanField(default=False)

class Game(models.Model, HtmlGame):
    # define which objects to use in constructing / creating board in self.setup()
    # so these models (Board, Player, Tile) inheriting from HtmlBoard, HtmlPlayer, etc. objects will be used
    GameBoard = Board
    Player = Player
    Tile = Tile

    creation = models.AutoField(primary_key=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    turnType = models.IntegerField(default=HtmlGame.MOVE_PLAYER)
    robotsTurn = models.BooleanField(default=False)
    processingRobotsTurn = models.BooleanField(default=False)
    uuid = models.CharField(max_length=25, unique=True)
    timestamp = models.CharField(max_length=100)  # hold time of last move

    user_is_active = False  # will be changed when managing users
    turnSuccessful = False  # will be changed when turn is successful

    def make_uuid(self):
        if not self.uuid:
            sample = UUID.uuid4()
            self.uuid = hex(sample.time_low)[2::2].replace('L', '')   # e.g. fe45L  but strip the L
            self.uuid += hex(UUID.uuid4().time_low)[3:4]  # add one more hex letter
            self.uuid = self.uuid.upper()  # uppercase everything
    
    def set_link_prepend(self, uuid=None):
        if not uuid:
            uuid = self.uuid
        self.board.link_prepend = "/game/" + uuid
    
    def prep_links(self):
        if not self.user_is_active:
            print("NOT prepping links", file=sys.stderr)
            return
        print("prep links", file=sys.stderr)
        self.set_link_prepend()
        return super(Game, self).prep_links()

    def save(self, *args, **kwargs):
        """ save board & all tiles, players. Every save includes a new timestamp """
        self.make_uuid()  # 
        self.timestamp = UUID.uuid4().hex  # update timestamp to latest modification
        self.board.save()
        # FOR SOME REASON, the board_id is not updated when I save the board
        self.board_id = self.board.creation
        # self.board = self.board
        if not self.get_active_player().humanControlled:
            self.robotsTurn = True
        super(Game, self).save(*args, **kwargs)

    def get_active_player(self):
        """ necessary to call this before saving """
        # this ordering will not work for 3+ players
        for player in self.board.players:
            # place players on their respective tiles. Workaround for html players not showing up
            tile = self.board.get(player.x, player.y)
            tile.player = player
        return self.board.players[0]
    
# redefine Board's Player and Tile properties
# these will be used when Board.setup() is run
Board.Player = Player
Board.Tile = Tile