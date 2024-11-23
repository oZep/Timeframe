from scripts.UI import Image, Text

class Menu():
    def __init__(self, game, tile):
        ''' create the menu UI'''
        self.game = game
        # WASD
        # (self, img, pos, speed)
        self.W = Image(self.game.assets['W'].copy(), [500,300], 10)
        self.W.scale(4) 
        self.A = Image(self.game.assets['A'].copy(), [445,360], 10)
        self.A.scale(4)
        self.S = Image(self.game.assets['S'].copy(), [500,360], 10)
        self.S.scale(4)
        self.D = Image(self.game.assets['D'].copy(), [555,360], 10)
        self.D.scale(4)

        self.ESC = Image(self.game.assets['ESC'].copy(), [1400,360], 10)

        self.click = Image(self.game.assets['click'].copy(), [1000, 330], 10)



    def update(self):
        ''' update the menu'''
        self.W.update()
        self.A.update()
        self.S.update()
        self.D.update()
        self.ESC.update()
        self.click.update()

    def render(self):
        ''' render the menu'''
        self.W.render(self.game.display)
        self.A.render(self.game.display)
        self.S.render(self.game.display)
        self.D.render(self.game.display)
        self.ESC.render(self.game.display)
        self.click.render(self.game.display)

