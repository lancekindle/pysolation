import board


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

    def reset_links(self):
        self.link = None

    def set_link(self, link):
        self.link = link
    

class HtmlPlayer(board.Player):

    def to_html(self):# build html representing player
        html = '<div class="player" style="background-color:' + self.color + '"></div>'
        return html


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

    def set_tile_links(self):
        self.reset_links()
        if self.turnType == self.MOVE_PLAYER:
            self.set_tile_links_for_player_move()
        elif self.turnType == self.REMOVE_TILE:
            self.set_tile_links_for_tile_remove()
        else:
            raise  # problem with our logic


class HtmlGame(board.Game):
    GameBoard = HtmlGameBoard
    Player = HtmlPlayer  # "magically" this now will spawn an HtmlPlayer, not just a normal player
    Tile = HtmlTile

    def to_html(self):
        # assume players turn to move
        self.prep_links()
        html = self.board.to_html()
##        h, w = self.board.board.shape
        width = '50px'
        height = '50px'
        style = '<style> div.player { width: ' + width + '; height: ' + height + '; border-radius: 50%; }'
        style += 'div.tile { position: relative; width: ' + width + '; height: ' + height + ';'
        style += 'float: left; margin: 2px; }'
        style += 'div.tile.visible { background-color: yellow }'
        style += 'div.tile.hidden { background-color: transparent; }'
        style += 'div.row { overflow: hidden; }'
        style += 'a.tile-link { display: block; width: ' + width + '; height: ' + height + '; }'
        style += '</style>'
        return style + html

    def prep_links(self):
        self.board.set_tile_links()
        
        


if __name__ == '__main__':
    game = HtmlGame()
    game.setup()
    board = game.board
    print(board)
    print(isinstance(game, HtmlGame))
    print(isinstance(game.board, HtmlGameBoard))
    print(isinstance(game.board[0,0], HtmlTile))
