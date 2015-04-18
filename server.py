import HtmlBoard as isolation
from flask import Flask

# http://flask.pocoo.org/docs/0.10/quickstart/#quickstart
app = Flask(__name__)

game = isolation.HtmlGame()
game.setup()  # can manipulate game within our functions

# tell flask what url should trigger this function
# "/" would mean our root url
@app.route("/")
def root_url():
    return game.to_html()

@app.route("/move_player_to/<int:x>,<int:y>")
def move_player_to(x, y):
    game.player_moves_player(x, y)
    return game.to_html()

@app.route("/remove_tile_at/<int:x>,<int:y>")
def remove_tile_at(x, y):
    game.player_removes_tile(x, y)
    return game.to_html()

if __name__ == "__main__":
    app.run(debug=True)  # run with debug=True to allow interaction & feedback when
                    # error / exception occurs.
                    # however, debug mode is super unsecure, so don't use it when allowing any ip connection
