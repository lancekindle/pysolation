from django.shortcuts import render
from django.http import HttpResponse
from HtmlBoard import HtmlGameBoard, HtmlGame, HtmlPlayer, HtmlTile
from . import models

def load_game_from_django(django_game):
    django_board = django_game.board
    # order by 'id' NOT 'ID' aka order by creation order
    tiles = models.Tile.objects.filter(board__eq=django_board).order_by('id')
    players = models.Player.objects.filter(board__eq=django_board).order_by('id')
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
    for (x, y, _), tile in zip(gb, tiles):
        gb[x, y] = tile
    return game

def save_game_to_django(game):
    # create database entries for board, tiles, and players
    board = game.board
    django_board = models.Board(h=board.h, w=board.w)
    for x, y, tile in board:
        models.Tile(board=django_board, x=x, y=y,
             ID=tile.ID, visible=tile.visible, solid=tile.solid)
    for player in board.players:
        models.Player(board=django_board, ID=player.ID, x=player.x,
               y=player.y, disabled=player.disabled, active=player.active)

# Create your views here.
def index(request):
    game = HtmlGame()
    game.setup()  # sets up common 9x9 board with 2 players
    save_game_to_django(game)
    game.prep_links()
    # now we display the main board to the user.... 
    context = {
              "game": game,
              "board": game.board,
    }
    return render(request, 'django_pysolation/index.html', context=context)

def move_player(request):
    request.args
