from django.shortcuts import render
from django.http import HttpResponse
import django
import uuid as UUID
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
    user_id = manage_active_players(request, game)
    context = {
              "game": game,
              "board": game.board,
    }
    response = render(request, 'django_pysolation/index.html', context=context)
    response.set_cookie('user_id', user_id)
    return response


def manage_active_players(request, game):
    """ manage new and current players. New players are assigned an open user (if one exists). Links
    are only generated for the current active user """
    player_in_game = False
    user_id = request.COOKIES.get('user_id')  
    if not user_id:
        user_id = str(UUID.uuid4())
    print("uuid" + user_id, file=sys.stderr)
    current_users = [player.assigned_user for player in game.board.players]
    if user_id in current_users:
        player_in_game = True
        print("player already in game", file=sys.stderr)
    else:
        for player in game.board.players:
            if not player.assigned_user:
                player_in_game = True
                player.assigned_user = user_id
                player.save()
                print("player added", file=sys.stderr)
                break
    user_is_active = False  # set to True if we should make links visible (since it's his turn)
    if player_in_game:
        if game.get_active_player().assigned_user == user_id:
            user_is_active = True
    if user_is_active:
        game.set_link_prepend(game.uuid)
        game.prep_links()  # pre-fetches tiles so they can have urls rewritten
        game.prep_links()  # actually sets tiles with correct urls
        print("player ACTIVE", file=sys.stderr)
    else:
        print("player not active", file=sys.stderr)
    return user_id


def game_landing(request, uuid):
    """ game is loaded by uuid """
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    user_id = manage_active_players(request, game)
    if not game:
        return HttpResponse("Game not found")
    game.get_active_player()  # workaround to load and show players on html page
    context = {
              "game": game,
              "board": game.board,
    }
    response = render(request, 'django_pysolation/index.html', context=context)
    response.set_cookie('user_id', user_id)
    return response


def move_player_to(request, uuid, x, y):
    x, y = int(x), int(y)
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    game.player_moves_player(x, y)
    user_id = manage_active_players(request, game)
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    game.save()
    response = render(request, 'django_pysolation/index.html', context=context)
    response.set_cookie('user_id', user_id)
    return response


def remove_tile_at(request, uuid, x, y):
    x, y = int(x), int(y)
    game = models.Game.objects.filter(uuid=uuid).first()
    game.board.preload_tiles()
    game.player_removes_tile(x, y)
    user_id = manage_active_players(request, game)
    print(game.turnSuccessful, file=sys.stderr)
    active = game.get_active_player()
    print(active.x, active.y, file=sys.stderr)
    context = {
              "game": game,
              "board": game.board,
    }
    game.save()
    response = render(request, 'django_pysolation/index.html', context=context)
    response.set_cookie('user_id', user_id)
    return response
