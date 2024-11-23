from scripts.UI import Image, Text

class GameOver():
    def __init__(self, score):
        ''' create the menu UI'''


        self.text = Text('Game Over', [860, 100])
        self.text2 = Text(str(score), [860, 100])
        self.text3 = Text('Press Enter to Return to Menu.', [780, 720])



    def update(self):
        ''' update the menu'''

    def render(self):
        ''' render the menu'''
        self.text.render(self.game.display, 50, (0,0,0))
        self.text2.render(self.game.display, 50, (0,0,0))
        self.text3.render(self.game.display, 50, (0,0,0))



