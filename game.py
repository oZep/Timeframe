import sys
import os
import math
import random
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player
from scripts.tilemap import Tilemap


class Game:
    def __init__(self):
        '''
        initializes Game
        '''
        pygame.init()

        # change the window caption
        pygame.display.set_caption("Pok N Wack")
        # create window
        self.screen = pygame.display.set_mode((1920,1080))

        self.display = pygame.Surface((1920,1080)) # render on different resolution then scale it up to screen

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False, False, False]  # left, right, up, down
        self.slowdown = 0 # slow down the game
        self.game_speed = 1

        self.assets = {
            'ground': load_images('tiles/ground'),
            'obstacles': load_images('tiles/obstacles'),
            'player': load_image('entities/player.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }


        # initalizing player
        self.player = Player(self, (1920/2, 1080/2), (8, 15))

        # initalizing tilemap
        self.tilemap = Tilemap(self, tile_size=64)
        self.tilemap.load('map.json')
        self.ground = Tilemap(self, tile_size=64)
        self.ground.load('ground.json')

        # screen shake
        self.screenshake = 0

        self.dead = 0

        self.scroll = [0, 0]


    def run(self):
        '''
        runs the Game
        '''

        # creating an infinite game loop
        while True:
            self.display.fill((255, 255, 255))
            # clear the screen for new image generation in loop

            self.screenshake = max(0, self.screenshake-1) # resets screenshake value

            if self.dead: # get hit once
                self.dead += 1

            # move 'camera' to focus on player, make him the center of the screen
            # scroll = current scroll + (where we want the camera to be - what we have/can see currently) 
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])  / 30  # x axis
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30

            # fix the jitter
            #render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            render_scroll = (0, 0)

            self.ground.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            # handle changes in game speed
            if self.slowdown:
                self.game_speed = 0.5

            if not self.dead:
                # update player movement
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]))
                self.player.render(self.display, offset=render_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # have to code the window closing
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a: # referencing right and left arrow keys
                        self.movement[0] = True
                        self.slowdown = False
                    elif event.key == pygame.K_d: 
                        self.movement[1] = True
                        self.slowdown = False
                    elif event.key == pygame.K_w:
                        self.movement[2] = True
                        self.slowdown = False
                    elif event.key == pygame.K_s:
                        self.movement[3] = True
                        self.slowdown = False
                    else:
                        self.slowdown = True
                if event.type == pygame.KEYUP: # when key is released
                    if event.key == pygame.K_a: 
                        self.movement[0] = False
                    if event.key == pygame.K_d: 
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_x:
                        self.slowdown = False

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60) # run at 60 fps, like a sleep

# returns the game then runs it
Game().run()