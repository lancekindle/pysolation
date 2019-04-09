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
    gb.fill_board(django_board.w, django_board.h)
    # replace tiles with tiles from django
    for (x, y, _), t in zip(gb, tiles):
        #print("tile", file=sys.stderr)
        tile = HtmlTile.create(x,y)
        tile.ID = t.ID
        tile.visible = t.visible
        tile.solid = t.solid
        gb[x, y] = tile
    gb.players.clear()
    for p in players:
        player = HtmlPlayer.create(p.x, p.y)
        player.active = p.active
        player.disabled = p.disabled
        player.ID = p.ID
        player.color = p.color
        gb.players.append(player)
        holding_tile = gb[player.x, player.y]
        holding_tile.player = player
    game.turnType = django_board.turnType
    return game

def save_game_to_django(game):
    # create database entries for board, tiles, and players
    board = game.board
    django_board = models.Board(h=board.h, w=board.w, turnType=game.turnType)
    django_board.save()
    for x, y, tile in board:
        t = models.Tile(board=django_board, x=x, y=y,
             ID=tile.ID, visible=tile.visible, solid=tile.solid)
        t.save()
    for player in board.players:
        p = models.Player(board=django_board, ID=player.ID, x=player.x,
               y=player.y, disabled=player.disabled, active=player.active, color=player.color)
        p.save()

def get_or_create_game():
    board = models.Board.objects.all().first()
    if board:
        game = load_game_from_django(board)
    else:
        game = HtmlGame()
        game.setup()  # sets up common 9x9 board with 2 players
        save_game_to_django(game)
    return game

# Create your views here.
def index(request):
    """ create or use first board game """
        # now we display the main board to the user.... 
    game = get_or_create_game()
    context = {
              "game": game,
              "board": game.board,
    }
    return render(request, 'django_pysolation/index.html', context=context)

def move_player_to(request, x, y):
    x, y = int(x), int(y)
    game = get_or_create_game()
    game.player_moves_player(x, y)
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    save_game_to_django(game)
    return render(request, 'django_pysolation/index.html', context=context)

def remove_tile_at(request, x, y):
    x, y = int(x), int(y)
    game = get_or_create_game()
    game.player_removes_tile(x, y)
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    save_game_to_django(game)
    return render(request, 'django_pysolation/index.html', context=context)
