from __future__ import print_function
from django.shortcuts import render
try:
    from django.core.urlresolvers import reverse  # correct path 1.8.14
except:
    from django.urls import reverse  # this is the correct path for 1.11, and 2.0+
from django.db import IntegrityError
from django.http import HttpResponse, Http404, HttpResponseRedirect
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
    game = models.Game.objects.filter(uuid=uuid).first() or \
           models.Game.objects.filter(uuid=uuid.upper()).first()
    if not game:
        raise Http404
    if timestamp == game.timestamp:
        print('refresh game: robot_turn {} & processing {}'.format(game.robotsTurn, game.processingRobotsTurn), file=sys.stderr)
        if game.robotsTurn and not game.processingRobotsTurn:
            # it appears that almost every time a human has a turn, we reach here
            # so check as well that active player is actually a robot
            if not game.get_active_player().humanControlled:
                return take_robot_turn(game)
        return HttpResponse(status=304)  # NOT MODIFIED status code
    return HttpResponse(status=303)  # SEE OTHER status code -- aka refresh from another URL

def take_robot_turn(game):
    # well we need to make a move for robot
    print('processing robot turn', file=sys.stderr)
    game.board.preload_tiles()
    game.get_active_player()  # workaround to pre-load players
    game.processingRobotsTurn = True
    game.save() # prevent future refresh requests from triggering the same function
    game.robot_takes_turn()
    if game.turnSuccessful:
        print('SUCCESS robot turn', file=sys.stderr)
        game.processingRobotsTurn = False
        game.save()
    else:
        print('FAIL robot turn', file=sys.stderr)
        raise Http404  # problem with our robot, it should never fail
    return HttpResponse(status=303)  # refresh from game URL


def join(request, uuid=None):
    """ joins game, triggering a redirect to that game's url. If such a game does not exist, will
        display home page with an error message
    """
    if not uuid:
        uuid = request.GET.get('code', None)
    if not uuid:
        return HttpResponseRedirect('/game')  # redirect to index, since no join code was given
                                                     # (basically just start a game)
    # retrieve game, checking uppercase uuid if not found at first
    game = models.Game.objects.filter(uuid=uuid).first() or \
           models.Game.objects.filter(uuid=uuid.upper()).first()
    if not game:
        context = {'error': 'no game found by ID "{}"'.format(uuid)}
        return render(request, 'django_pysolation/start.html', context=context)
    return HttpResponseRedirect('/game/{}'.format(uuid))

def index(request, uuid=None):
    """ create or join a board game. If uuid is not specified, create game and
        redirect to /game/<uuid> so that "refreshing" the browser won't trigger
        another new game
    """
    # now we display the main board to the user.... 
    game = None #models.Game.objects.all().first()
    if not uuid:
        # get uuid from url parameters aka game/?uuid=c234 
        print(request.GET, file=sys.stderr)
        uuid = request.GET.get('code', None)
    print("uuid???", uuid, file=sys.stderr)
    if uuid:
        # retrieve game, checking uppercase uuid if not found at first
        game = models.Game.objects.filter(uuid=uuid).first() or \
               models.Game.objects.filter(uuid=uuid.upper()).first()
        if game:
            game.board.preload_tiles()
    if not game:
        return create_and_redirect_to_game(request)
    else:
        print("game found", file=sys.stderr)
    user_id, is_active_player = manage_active_players(request, game)
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


def create_and_redirect_to_game(request):
    try:
        print("game created", file=sys.stderr)
        w, h = 5, 6
        board = models.Board(w=w, h=h)
        game = models.Game(board=board)
        players = 2  # number of players
        game.setup(0, (w,h), players)  # all players are robots by default
        # when a player visits the board she'll be assigned a player, removing it's status as a robot
        # active player on fresh board will be assigned to first user
        game.save()
        return HttpResponseRedirect('/game/{}'.format(game.uuid))
    except IntegrityError:
        print("clashing game uuid found", file=sys.stderr)
        models.Game.objects.all().delete()
        raise Http404("DATABASE OUT OF MEMORY. WIPING ALL PREVIOUS GAMES.....")


def manage_active_players(request, game):
    """ manage new and current players. New players are assigned an open user
        (if one exists). returns (user_id, is_active_player) where
        is_active_player is boolean if it's player's turn
    """
    player_in_game = False
    user_id = request.COOKIES.get('user_id')
    if not user_id:
        user_id = str(UUID.uuid4())
    print("uuid" + user_id, file=sys.stderr)
    game.get_active_player()  # workaround to preload players
    current_users = [player.assigned_user for player in game.board.players]
    if user_id in current_users:
        player_in_game = True
        print("player already in game", file=sys.stderr)
    else:
        # assign user to an unassigned player token
        for player in game.board.players:
            if not player.assigned_user:
                player_in_game = True
                player.assigned_user = user_id
                player.humanControlled = True
                player.save()
                print("player added", file=sys.stderr)
                break
    if player_in_game:
        if game.get_active_player().assigned_user == user_id:
            game.user_is_active = True
    if game.user_is_active:
        print("player ACTIVE", file=sys.stderr)
    else:
        print("player not active", file=sys.stderr)
    return user_id, game.user_is_active


def game_landing(request, uuid):
    """ game is loaded by uuid """
    game = models.Game.objects.filter(uuid=uuid).first() or \
           models.Game.objects.filter(uuid=uuid.upper()).first()
    user_id, is_active = manage_active_players(request, game)
    if not game:
        return HttpResponse("Game not found")
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
    game = models.Game.objects.filter(uuid=uuid).first() or \
           models.Game.objects.filter(uuid=uuid.upper()).first()
    game.board.preload_tiles()
    user_id, is_active_player = manage_active_players(request, game)
    if is_active_player:
        game.player_moves_player(x, y)
    print("move turn success?", game.turnSuccessful, file=sys.stderr)
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
    game = models.Game.objects.filter(uuid=uuid).first() or \
           models.Game.objects.filter(uuid=uuid.upper()).first()
    user_id, is_active_player = manage_active_players(request, game)
    if is_active_player:
        game.player_removes_tile(x, y)
    print("remove turn success?", game.turnSuccessful, file=sys.stderr)
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
