import sys
import os
import math
import random
import pygame, os

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy
from scripts.bullet import Bullet
from scripts.tilemap import Tilemap
from scripts.UI import Text
from scripts.menu import Menu


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
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'target': load_image('entities/target_round_a.png'),
            'playerbullet': load_image('entities/PlayerBullet.png'),
            'enemybullet': load_image('entities/enemy_bullet.png'),
            'W': load_image('UI/W.png'),
            'A': load_image('UI/A.png'),
            'S': load_image('UI/S.png'),
            'D': load_image('UI/D.png'),
            'ESC': load_image('UI/ESC.png'),
            'click': load_image('UI/click.png'),
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

        self.bullets = []

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

            # render the main menu
            menu = Menu(self)
            menu.update()
            menu.render()

            
            self.screen.blit(pygame.transform.scale(self.display, self.screen_size), [0,0])
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
        self.enemy_timer_reset = 2000
        self.enemy_timer = self.enemy_timer_reset

        self.enemies = []
        self.bullets = []

        self.deltatime = 0

        self.game_timer = 30000

        self.slowdown_timer_change = 10

        self.has_moved = False

        level_bar = Text("Time Left: " + str(self.game_timer), pos=(self.display.get_width() // 2 -30, 13))

        # creating an infinite game loop
        while True:
            self.display.fill((255, 255, 255))
            # clear the screen for new image generation in loop

            self.screenshake = max(0, self.screenshake-1) # resets screenshake value

            #Count game timer down if has moved
            if self.has_moved and not self.dead:
                self.game_timer -= self.deltatime * (1 + self.slowdown * (self.slowdown_timer_change -1))

            if self.dead: # get hit once
                self.dead += 1
            
            #Count down if has moved, if time elapsed spawn enemy
            if self.has_moved:
                self.enemy_timer -= self.deltatime * (1 - (self.slowdown * (self.slowdown_timer_change-1)/self.slowdown_timer_change))
            if self.enemy_timer < 0:
                enemy_pos = [100, 100]
                if random.randint(0, 1) == 0:
                    enemy_pos[0] = 0 + ((self.display.get_width() + 42) * random.randint(0, 1)) - 42
                    enemy_pos[1] = random.randint(0, self.display.get_height() + 42) - 42
                else:
                    enemy_pos[1] = 0 + ((self.display.get_height() + 42) * random.randint(0, 1)) - 42
                    enemy_pos[0] = random.randint(0, self.display.get_width() + 42) - 42
                new_enemy = Enemy(self, enemy_pos, (42, 42))
                self.enemies.append(new_enemy)
                #next wait (milliseconds)
                self.enemy_timer_reset -= 100
                if self.enemy_timer_reset < 100:
                    self.enemy_timer_reset = 100
                self.enemy_timer = self.enemy_timer_reset

            render_scroll = (0, 0)

            self.ground.render(self.display, offset=render_scroll)
            self.tilemap.render(self.display, offset=render_scroll)

            for bullet in self.bullets.copy():
                collided = bullet.update(self.tilemap)
                if collided:
                    self.bullets.remove(bullet)
                else:
                    if bullet.pos[0] > self.display.get_width():
                        self.bullets.remove(bullet)
                    if self.player.pos[1] > self.display.get_height():
                        self.bullets.remove(bullet)
                    if self.player.pos[0] < 0 - bullet.size[0]:
                        self.bullets.remove(bullet)
                    if self.player.pos[1] < 0 - bullet.size[1]:
                        self.player.pos[1] = 0 
                    bullet.render(self.display, offset=render_scroll)

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
                if self.player.pos[0] > self.display.get_width() - 42:
                    self.player.pos[0] = self.display.get_width() - 42
                if self.player.pos[1] > self.display.get_height() - 42:
                    self.player.pos[1] = self.display.get_height() - 42
                if self.player.pos[0] < 0:
                    self.player.pos[0] = 0 
                if self.player.pos[1] < 0:
                    self.player.pos[1] = 0 
                self.player.render(self.display, offset=render_scroll)

            #Show time left
            min = math.floor((self.game_timer/1000/60))
            sec = math.floor((self.game_timer/1000) % 60)
            ms = self.game_timer - math.floor(self.game_timer/1000) * 1000
            if sec == 0:
                sec = '00'
            elif sec < 10:
                sec = '0' + str(sec)
            if min:
                formatted_timer = str(min) + ':' + str(sec)
            else:
                formatted_timer = str(sec)
                if int(sec) <= 10:
                    formatted_timer = formatted_timer + '.' + str(ms)
            level_bar.render(self.display, 50, color=(0, 0, 0), text=formatted_timer)

            # player cursor display bulleye
            mpos = pygame.mouse.get_pos() # gets mouse positon
            mpos = (mpos[0] / (self.screen_size[0]/self.display.get_width()), mpos[1] / (self.screen_size[1]/self.display.get_height())) # since screen sometimes scales
            self.display.blit(pygame.transform.scale(self.assets['target'], (32, 32)), (mpos[0], mpos[1]))


            for event in pygame.event.get():
                if event.type == pygame.QUIT: # have to code the window closing
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not self.dead:
                        dx = mpos[0] - self.player.rect().centerx
                        dy = mpos[1] - self.player.rect().centery
                        bullet_angle = math.atan2(dx, -dy) - (math.pi/2)
                        new_bullet = Bullet(self, self.player.rect().center, 10, bullet_angle, (18, 18))
                        self.bullets.append(new_bullet)
                        self.game_timer -= 1000
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
                    self.has_moved = True
                if event.type == pygame.KEYUP: # when key is released
                    if event.key == pygame.K_a: 
                        self.movement[0] = False
                    elif event.key == pygame.K_d: 
                        self.movement[1] = False
                    elif event.key == pygame.K_w:
                        self.movement[2] = False
                    elif event.key == pygame.K_s:
                        self.movement[3] = False
                
            if self.movement[1] - self.movement[0] == 0 and self.movement[3] - self.movement[2] == 0 or self.dead:
                self.slowdown = True
            else:
                self.slowdown = False

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display, self.screen_size), screenshake_offset)
            pygame.display.update()
            self.deltatime = self.clock.tick(60) # run at 60 fps, like a sleep

# returns the game then runs it
Game().main_menu()