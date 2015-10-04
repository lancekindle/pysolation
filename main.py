from HtmlBoard import HtmlGame
# run this module to play the browsers-supported game

if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)  # http://flask.pocoo.org/docs/0.10/quickstart/#quickstart

    game = HtmlGame()
    number_of_bots = 1
    number_of_humans = 2
    board_dimensions = (7, 6)
    
    game.setup(number_of_humans, board_dimensions, number_of_bots)

    @app.route("/")
    def root_url():
        return game.get_html()

    @app.route("/move_player_to/<int:x>,<int:y>")
    def move_player_to(x, y):
        game.player_moves_player(x, y)
        return game.get_html()

    @app.route("/remove_tile_at/<int:x>,<int:y>")
    def remove_tile_at(x, y):
        game.player_removes_tile(x, y)
        return game.get_html()

    @app.route("/robot_takes_turn/")
    def robot_takes_turn():
        game.robot_takes_turn()
        return game.get_html()

    app.run(debug=True)  # run with debug=True to allow interaction & feedback when
                    # error / exception occurs.
                    # however, debug mode is super unsecure, so don't use it when allowing any ip connection

