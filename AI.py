from __future__ import print_function
from GridAnalyzer import GridAnalyzer
from Astar import PathFinder

class SimpleAI:
    verbose = False

    def __init__(self, board, player):
        self.board = board
        self.player = player

    def get_move(self):
        grid = self.board.convert_to_grid()
        ga = GridAnalyzer(grid, self.player)
        ga.verbose = self.verbose
        #goal = ga.get_target_point()
        computedGrid = ga.get_analyzed_grid()
        goal = computedGrid.get_first_highest_value_point()
        pathfinder = PathFinder(grid, self.player, goal)
        path = pathfinder.get_best_path()
        if self.verbose:
            print('grid', grid)
            print('computedGrid', computedGrid)
            print('goal', goal)
            print('path', path)
        return path[0]

    def move_player(self):
        move = self.get_move()
        self.board.move_player(self.player, move.x, move.y)

if __name__ == '__main__':
    import board
    ggame = board.Game()
    ggame.setup()
    b = ggame.board
    pplayer = b.players[1]
    simpai = SimpleAI(b, pplayer)
    simpai.verbose = True
    simpai.move_player()
    print(b)
##    import server
##    player = server.game.board.players[1]
##    simpAI = SimpleAI(server.game.board, player)
##
##    @server.app.route("/move_player_to/<int:x>,<int:y>")
##    def move_player_to(x, y):
##        player = server.game.board.players[0]
##        server.game.board.move_player(player, x, y)
##        simpAI.move_player()
##        return server.game.to_html()
##
##    server.move_player_to = move_player_to
##    server.app.run(debug=True)
