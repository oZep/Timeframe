import sys
import os
import math
import random
import pygame, os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.tilemap import Tilemap


class Game:
    def __init__(self):
        '''
        initializes Game
        '''
        pygame.init()

        # change the window caption
        pygame.display.set_caption("Time Dilemma")

        # create window
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.screen_size = pygame.display.get_surface().get_size()
        self.display = pygame.Surface((1920, 1080))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False, False, False]  # left, right, up, down
        self.slowdown = 0 # slow down the game
        self.game_speed = 1

        self.assets = {
            'ground': load_images('tiles/ground'),
            'obstacles': load_images('tiles/obstacles'),
            'player': load_image('entities/player.png'),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'target': load_image('entities/target_round_a.png'),
            'playerbullet/idle': load_image('entities/PlayerBullet.png'),
        }


        # initalizing player
        self.player = Player(self, (self.display.get_width()/2, self.display.get_height()/2), (42, 42))

        # initalizing tilemap
        self.tilemap = Tilemap(self, tile_size=64)
        self.tilemap.load('map.json')
        self.ground = Tilemap(self, tile_size=64)
        self.ground.load('ground.json')

        # screen shake
        self.screenshake = 0

        self.dead = 0

        self.scroll = [0, 0]

        pygame.mouse.set_visible(False)

    def main_menu(self):
        while True:
            self.display.fill((255, 255, 255))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # have to code the window closing
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_RETURN:
                        self.run()
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen_size))
            pygame.display.update()
            self.deltatime = self.clock.tick(60) # run at 60 fps, like a sleep

    def run(self):
        '''
        runs the Game
        '''
        self.screenshake = 0

        self.dead = 0

        self.player.pos = [self.display.get_width()/2, self.display.get_height()/2]

        self.movement = [False, False, False, False]  # left, right, up, down
        self.slowdown = 0 # slow down the game
        self.game_speed = 1

        #Enemy spawn wait (milliseconds)
        self.enemy_timer = 2000

        self.enemies = []

        self.deltatime = 0

        # creating an infinite game loop
        while True:
            self.display.fill((255, 255, 255))
            # clear the screen for new image generation in loop

            self.screenshake = max(0, self.screenshake-1) # resets screenshake value

            if self.dead: # get hit once
                self.dead += 1
            
            #Count down, if time elapse spawn enemy
            self.enemy_timer -= self.deltatime
            if self.enemy_timer < 0:
                enemy_pos = (100, 100)
                new_enemy = Enemy(self, enemy_pos, (42, 42))
                self.enemies.append(new_enemy)
                #next wait (milliseconds)
                self.enemy_timer = 2000

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
                self.game_speed = 0.2
            else:
                self.game_speed = 1
            
            #update enemies
            for enemy in self.enemies:
                enemy.update(self.tilemap, (self.player.pos[0] - enemy.pos[0], self.player.pos[1] - enemy.pos[1]))
                enemy.render(self.display)

            if not self.dead:
                # update player movement
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], self.movement[3] - self.movement[2]))
                self.player.render(self.display, offset=render_scroll)

            # player cursor display bulleye
            mpos = pygame.mouse.get_pos() # gets mouse positon
            mpos = (mpos[0] / (self.screen_size[0]/self.display.get_width()), mpos[1] / (self.screen_size[1]/self.display.get_height())) # since screen sometimes scales
            self.display.blit(pygame.transform.scale(self.assets['target'], (32, 32)), (mpos[0], mpos[1]))


            for event in pygame.event.get():
                if event.type == pygame.QUIT: # have to code the window closing
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.main_menu()
                    if event.key == pygame.K_a: # referencing right and left arrow keys
                        self.movement[0] = True
                    elif event.key == pygame.K_d: 
                        self.movement[1] = True
                    elif event.key == pygame.K_w:
                        self.movement[2] = True
                    elif event.key == pygame.K_s:
                        self.movement[3] = True
                if event.type == pygame.KEYUP: # when key is released
                    if event.key == pygame.K_a: 
                        self.movement[0] = False
                    elif event.key == pygame.K_d: 
                        self.movement[1] = False
                    elif event.key == pygame.K_w:
                        self.movement[2] = False
                    elif event.key == pygame.K_s:
                        self.movement[3] = False
                
                if not self.movement[0] and not self.movement[1] and not self.movement[2] and not self.movement[3]:
                    self.slowdown = True
                else:
                    self.slowdown = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.screenshake = 10
                    self.player.shoot(pygame.mouse.get_pos())

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen_size), screenshake_offset)
            pygame.display.update()
            self.deltatime = self.clock.tick(60) # run at 60 fps, like a sleep

# returns the game then runs it
Game().main_menu()