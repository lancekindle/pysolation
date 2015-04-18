import board
from flask import Flask


class HtmlTile(board.Tile):
    link = None

    def to_html(self):
        if self.visible:
            visibility = 'visible'
        else:
            visibility = 'hidden'
        html = '<div class="tile ' + visibility  + '">'  # build html representing tile
        if self.visible and not self.player:  # do not allow clicking on tile if it's removed or player occupied
            if self.link:
                html += '<a href="' + self.link + '" class="tile-link"></a>'
        if self.player:
            html += self.player.to_html()
        html += '</div>'
        return html

    @classmethod
    def get_style(cls, size='50px'):
        style = 'div.tile { position: relative; width: ' + size + '; height: ' + size + ';'
        style += 'float: left; margin: 2px; }'
        style += 'div.tile.visible { background-color: yellow }'
        style += 'div.tile.hidden { background-color: transparent; }'
        style += 'a.tile-link { display: block; width: ' + size + '; height: ' + size + '; }'
        return style

    def reset_links(self):
        self.link = None

    def set_link(self, link):
        self.link = link
    

class HtmlPlayer(board.Player):

    def to_html(self):# build html representing player
        html = '<div class="player" style="background-color:' + self.color + '"></div>'
        return html

    @classmethod
    def get_style(cls, size='50px'):
        return 'div.player { width: ' + size + '; height: ' + size + '; border-radius: 50%; }'


class HtmlGameBoard(board.GameBoard):
    Player = HtmlPlayer
    Tile = HtmlTile

    def to_html(self):
        html = ''
        for row in self.board:
            html += '<div class="row">'
            for tile in row:
                html += tile.to_html()
            html += '</div>'  # or some other visual break between rows
        html += 'GameBoard tail'  # add extras
        return html

    @classmethod
    def get_style(cls, size='50px'):
        return 'div.row { overflow: hidden; }'  # set each row on newline

    def reset_links(self):
        for row in self.board:
            for tile in row:
                tile.reset_links()

    def set_tile_links_for_player_move(self):
        player = self.players[0]
        x, y = player.x, player.y
        tileMatrix = self.get_tiles_around(x, y)
        for row in tileMatrix:
            for tile in row:
                x2, y2 = tile.x, tile.y
                if x == x2 and y == y2:  # skip tile under player
                    continue
                tile.set_link("/move_player_to/" + str(x2) + ',' + str(y2))

    def set_tile_links_for_tile_remove(self):
        for row in self.board:
            for tile in row:
                x, y = tile.x, tile.y
                tile.set_link("/remove_tile_at/" + str(x) + ',' + str(y))


class HtmlGame(board.Game):
    GameBoard = HtmlGameBoard
    Player = HtmlPlayer  # "magically" this now will spawn an HtmlPlayer, not just a normal player
    Tile = HtmlTile

    def to_html(self):
        self.prep_links()
        html = self.board.to_html()
        style = self.get_style('50px')  # even though it's a class method, we called using self, meaning
                            # that the function will use this instance and its variables instead of the class's
        return '<style>' + style  + '</style>' + html
    
    @classmethod
    def get_style(cls, size='50px'):
        style = cls.GameBoard.get_style(size)
        style += cls.Tile.get_style(size)
        style += cls.Player.get_style(size)
        return style

    def prep_links(self):
        self.board.reset_links()
        if self.turnType == self.MOVE_PLAYER:
            self.board.set_tile_links_for_player_move()
        elif self.turnType == self.REMOVE_TILE:
            self.board.set_tile_links_for_tile_remove()
        else:
            raise  # problem with our logic


if __name__ == '__main__':
    # http://flask.pocoo.org/docs/0.10/quickstart/#quickstart
    app = Flask(__name__)

    game = HtmlGame()
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

    app.run(debug=True)  # run with debug=True to allow interaction & feedback when
                    # error / exception occurs.
                    # however, debug mode is super unsecure, so don't use it when allowing any ip connection

