from scripts.UI import Image, Text

class GameOver():
    def __init__(self, game, score):
        ''' create the gameover UI'''

        self.game = game
        self.score = score

        self.text = Text('Game Over', [860, 100])
        self.text2 = Text('Score: '+str(score),  [860, 335])
        self.text4 = Text('You Suck :(', [860, 540])
        self.text3 = Text('Press Enter to Return to Menu.', [700, 720])



    def update(self):
        ''' update the menu'''

    def render(self):
        ''' render the menu'''
        self.text.render(self.game.display, 50, (0,0,0))
        self.text2.render(self.game.display, 50, (0,0,0))
        self.text3.render(self.game.display, 50, (0,0,0))

        if self.score[0] == "-":
            self.text4.render(self.game.display, 50, (0,0,0))



