from __future__ import print_function
from django.shortcuts import render
from django.db import IntegrityError
from django.http import HttpResponse, Http404
import django
import uuid as UUID
import sys
from . import models

def join_or_start(request):
    """ present user with simple option of starting a game, or joining an existing one """
    return render(request, 'django_pysolation/start.html', context={})

def refresh(request, uuid=None, timestamp=None):
    """ returns status code 200 only when game has updated from given timestamp """
    if uuid is None or timestamp is None:
        raise Http404
    game = models.Game.objects.filter(uuid=uuid).first()
    if not game:
        raise Http404
    if timestamp == game.timestamp:
        return HttpResponse(status=304)  # NOT MODIFIED status code
    return HttpResponse(status=303)  # SEE OTHER status code -- aka refresh from another URL

def index(request, uuid=None):
    """ create or use first board game """
    # now we display the main board to the user.... 
    game = None #models.Game.objects.all().first()
    if not uuid:
        # get uuid from url parameters aka game/?uuid=c234 
        print(request.GET, file=sys.stderr)
        uuid = request.GET.get('code', None)
    print("uuid???", uuid, file=sys.stderr)
    if uuid:
        game = models.Game.objects.filter(uuid=uuid).first()
        if game:
            game.board.preload_tiles()
    if not game:
        try:
            print("game created", file=sys.stderr)
            w, h = 5, 6
            board = models.Board(w=w, h=h)
            game = models.Game(board=board)
            if uuid:
                game.uuid = uuid
            else:
                uuid = game.make_uuid()
            game.setup(2, (w,h), 0)
            game.save()
        except IntegrityError:
            print("clashing game uuid found", file=sys.stderr)
            models.Game.objects.all().delete()
            raise Http404("DATABASE OUT OF MEMORY. WIPING ALL PREVIOUS GAMES.....")
    else:
        print("game found", file=sys.stderr)
        game.get_active_player()  # workaround to load and show players on html page
    user_id = manage_active_players(request, game)
    game_url = "/game/" + game.uuid
    context = {
            "game_url": game_url,
            "refresh_check_url": game_url + "/refresh/" + game.timestamp,
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
    game_url = "/game/" + game.uuid
    context = {
            "game_url": game_url,
            "refresh_check_url": game_url + "/refresh/" + game.timestamp,
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
    if game.turnSuccessful:
        game.save()
    game_url = "/game/" + game.uuid
    context = {
            "game_url": game_url,
            "refresh_check_url": game_url + "/refresh/" + game.timestamp,
            "game": game,
            "board": game.board,
    }
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
    if game.turnSuccessful:
        game.save()
    game_url = "/game/" + game.uuid
    context = {
            "game_url": game_url,
            "refresh_check_url": game_url + "/refresh/" + game.timestamp,
            "game": game,
            "board": game.board,
    }
    response = render(request, 'django_pysolation/index.html', context=context)
    response.set_cookie('user_id', user_id)
    return response
