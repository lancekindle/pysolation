#!/usr/bin/env python
from JSBoard import JSGame
from HtmlBoard import HtmlGame
# run this module to play the browsers-supported game

if __name__ == '__main__':
    from flask import Flask, jsonify
    app = Flask(__name__)  # http://flask.pocoo.org/docs/0.10/quickstart/#quickstart

    game = HtmlGame()
    number_of_bots = 1
    number_of_humans = 1
    board_dimensions = (7, 6)
    
    game.setup(number_of_humans, board_dimensions, number_of_bots)

    @app.route("/")
    def root_url():
        return game.get_html()

    @app.route("/game/move_player_to/<int:x>,<int:y>")
    def move_player_to(x, y):
        game.player_moves_player(x, y)
        return game.get_html()

    @app.route("/game/remove_tile_at/<int:x>,<int:y>")
    def remove_tile_at(x, y):
        game.player_removes_tile(x, y)
        return game.get_html()

    @app.route("/robot_takes_turn/")
    def robot_takes_turn():
        game.robot_takes_turn()
        return game.get_html()

    # for handling javascript animated game, no urls ever change
    @app.route("/js/move_to/<int:x>,<int:y>", methods=['POST'])
    def player_moved(x, y):
        # no game logic happens we just need to watch player move. DEBUG
        game.player_moves_player(x, y)
        if not game.turnSuccessful:
            return jsonify({})
        game.prep_links()  # get new links
        method, (player, x, y) = game.lastTurn
        return jsonify({
                "move_player":["%s" % player.id, "%s,%s" % (x,y)],
                "change_turn": [],
                "link_tiles": game.linked_tiles, # change over to new linked tiles
            })

    # for handling javascript animated game, no urls ever change
    @app.route("/js/remove_at/<int:x>,<int:y>", methods=['POST'])
    def tile_removed(x, y):
        game.player_removes_tile(x, y)
        if not game.turnSuccessful:
            return jsonify({})
        game.prep_links()  # get new links
        method, (tile, x, y) = game.lastTurn
        return jsonify({
                "remove_tile": [tile.ID,],
                "change_turn": [],
                "link_tiles": game.linked_tiles, # changeover to new linked tiles
            })


    app.run(debug=True)  # run with debug=True to allow interaction & feedback when
                    # error / exception occurs.
                    # however, debug mode is super unsecure, so don't use it when allowing any ip connection

