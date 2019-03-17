from HtmlBoard import HtmlTile, HtmlGame, HtmlPlayer, HtmlTile, HtmlGameBoard

class JSGame(HtmlGame):
    """ provide html&js-export options to Game class """

    def get_scripts(self):
        """ return javascript for manipulating html gameboard """
        script = "<script>"
        with open("JSBoard.js", 'r') as f:
            script += '\n'.join(f.readlines())
        script += "</script>"
        return script
        

