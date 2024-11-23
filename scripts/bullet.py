import math
import pygame

class Bullet():
    def __init__(self, game, pos, velocity, angle, size=(18, 18), type='player'):
        self.game = game
        self.pos = list(pos)
        self.velocity = velocity
        self.angle = angle
        self.size = size
        self.type = type

        self.game.screenshake = 7
    
    def render(self, surf, offset=(0, 0)):
        surf.blit(self.game.assets[self.type + 'bullet'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def update(self, tilemap):
        self.pos[0] += math.cos(self.angle) * self.velocity * self.game.game_speed
        self.pos[1] += math.sin(self.angle) * self.velocity * self.game.game_speed
        if tilemap.solid_check(self.pos):
            return True
        else:
            if self.type == 'player':
                for enemy in self.game.enemies.copy():
                    rect = enemy.rect()
                    if rect.collidepoint(self.pos):
                        self.game.enemies.remove(enemy)
                        if not self.game.dead:
                            self.game.game_timer += 5000
                        return True
            elif self.type == 'enemy':
                rect = self.game.player.rect()
                if rect.collidepoint(self.pos):
                    self.game.dead += 1
                    return True