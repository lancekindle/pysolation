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
    return '<a href="move_player_to/6,4"> click here to move player to (6,4) </a><p>' + str(game.board).replace('\n', '<p>')

@app.route("/two.html")
def nhello():
    return "next time!"

@app.route("/move_player_to/<int:x>,<int:y>")
def move_player_to(x, y):
    player = game.board.players[0] # hard coded player  -- can change that using index of players in url
    game.board.move_player(player, x, y)
    return str(game.board)

if __name__ == "__main__":
    app.run(debug=True)  # run with debug=True to allow interaction & feedback when page doesn't load
                    # however, debug mode is super unsecure, so don't use it when allowing any ip
