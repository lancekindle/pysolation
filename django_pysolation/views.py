from django.shortcuts import render
from django.http import HttpResponse
import django
import sys
from HtmlBoard import HtmlGameBoard, HtmlGame, HtmlPlayer, HtmlTile
from . import models

def load_game_from_django(django_board):
    # order by 'id' NOT 'ID' aka order by creation order
    tiles = models.Tile.objects.filter(board=django_board)
    players = models.Player.objects.filter(board=django_board)
    game = HtmlGame()
    gb = HtmlGameBoard()
    game.board = gb
    gb.setup()
    gb.players.clear()
    for p in players:
        player = HtmlPlayer.create(p.x, p.y)
        player.active = p.active
        player.disabled = p.disabled
        player.ID = p.ID
        gb.players.append(player)
    gb.fill_board(django_board.w, django_board.h)
    # replace tiles with tiles from django
    for (x, y, _), t in zip(gb, tiles):
        print("tile", file=sys.stderr)
        tile = HtmlTile.create(x,y)
        tile.ID = t.ID
        tile.visible = t.visible
        tile.solid = t.solid
        gb[x, y] = tile
    # turn-type hardcoded for now
    game.turnType = game.MOVE_PLAYER
    return game

def save_game_to_django(game):
    # create database entries for board, tiles, and players
    board = game.board
    django_board = models.Board(h=board.h, w=board.w)
    django_board.save()
    for x, y, tile in board:
        t = models.Tile(board=django_board, x=x, y=y,
             ID=tile.ID, visible=tile.visible, solid=tile.solid)
        t.save()
    for player in board.players:
        p = models.Player(board=django_board, ID=player.ID, x=player.x,
               y=player.y, disabled=player.disabled, active=player.active)
        p.save()

# Create your views here.
def index(request):
    board = models.Board.objects.all().first()
    if board:
        game = load_game_from_django(board)
    else:
        game = HtmlGame()
        game.setup()  # sets up common 9x9 board with 2 players
        save_game_to_django(game)
    # now we display the main board to the user.... 
    context = {
              "game": game,
              "board": game.board,
    }
    return render(request, 'django_pysolation/index.html', context=context)

def move_player(request):
    request.args
