from django.shortcuts import render
from django.http import HttpResponse
import django
import sys
from . import models

def index(request, uuid=None):
    """ create or use first board game """
    # now we display the main board to the user.... 
    game = None #models.Game.objects.all().first()
    if uuid:
        game = models.Game.objects.filter(uuid=uuid).first()
        game.board.preload_tiles()
    if not game:
        print("game created", file=sys.stderr)
        w, h = 5, 6
        if uuid:
            board = models.Board(w=w, h=h, uuid=uuid)
        else:
            board = models.Board(w=w, h=h)
        game = models.Game(board=board)
        game.make_uuid()
        game.setup(2, (w,h), 0)
        game.save()
    else:
        print("game found", file=sys.stderr)
        game.get_active_player()  # workaround to load and show players on html page
    game.set_link_prepend(game.uuid)
    game.prep_links()  # pre-fetches tiles so they can have urls rewritten
    context = {
              "game": game,
              "board": game.board,
    }
    return render(request, 'django_pysolation/index.html', context=context)

def game_landing(request, uuid):
    """ game is loaded by uuid """
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    game.set_link_prepend(game.uuid)
    game.prep_links()  # pre-fetches tiles so they can have urls rewritten
    if not game:
        return HttpResponse("Game not found")
    game.get_active_player()  # workaround to load and show players on html page
    context = {
              "game": game,
              "board": game.board,
    }
    return render(request, 'django_pysolation/index.html', context=context)

def move_player_to(request, uuid, x, y):
    x, y = int(x), int(y)
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    game.set_link_prepend(game.uuid)
    game.player_moves_player(x, y)
    game.prep_links()  # pre-fetches tiles so they can have urls rewritten
    game.prep_links()  # actually sets tiles with correct urls
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    game.save()
    return render(request, 'django_pysolation/index.html', context=context)

def remove_tile_at(request, uuid, x, y):
    x, y = int(x), int(y)
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    game.set_link_prepend(game.uuid)
    game.player_removes_tile(x, y)
    game.prep_links()  # pre-fetches tiles so they can have urls rewritten
    game.prep_links()  # actually sets tiles with correct urls
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    game.save()
    return render(request, 'django_pysolation/index.html', context=context)
