import board
# for css icons
# https://css-tricks.com/examples/ShapesOfCSS/

class HtmlTile(board.Tile):

    def to_html(self):
        html = ''  # build html representing tile
        if self.player:
            html += self.player.to_html()
        return html
    

class HtmlPlayer(board.Player):

    def to_html(self):
        html = ''  # build html representing player
        return html


class HtmlGameBoard(board.GameBoard):
    Player = HtmlPlayer
    Tile = HtmlTile

    def to_html(self):
        html = ''
        for row in self.board:
            for tile in row:
                html += tile.to_html()
            html += '\n'  # or some other visual break between rows
        html += 'GameBoard tail\n'  # add extras
        return html


class HtmlGame(board.Game):
    GameBoard = HtmlGameBoard  # "magically" this now will spawn an HtmlPlayer, not just a normal player
    Player = HtmlPlayer
    Tile = HtmlTile

    def to_html(self):
        html = self.board.to_html()
        html += 'Game tail\n'
        return html


if __name__ == '__main__':
    game = HtmlGame()
    game.setup()
    board = game.board.board
    print(board)
    print(isinstance(game, HtmlGame))
    print(isinstance(game.board, HtmlGameBoard))
    print(isinstance(game.board[0,0], HtmlTile))
