import sys
import os
import math
import random
import pygame

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
        '''
        initializes Game
        '''
        pygame.init()

        # change the window caption
        pygame.display.set_caption("Pok N Wack")
        # create window
        self.screen = pygame.display.set_mode((640,480))

        self.display = pygame.Surface((320, 240), pygame.SRCALPHA) # render on smaller resolution then scale it up to bigger screen

        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.movement = [False, False]

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        # adding sound
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        # initalizing player
        self.player = Player(self, (100, 100), (8, 15))

        # initalizing tilemap
        self.tilemap = Tilemap(self, tile_size=16)

        # tracking level
        self.level = 0
        self.max_level = len(os.listdir('data/maps')) # max level
        # loading the level
        self.load_level(self.level)

        # screen shake
        self.screenshake = 0


    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        # keep track
        self.particles = []

        # creating 'camera' 
        self.scroll = [0, 0]

        self.dead = 0

        self.projectiles = []
        self.sparks = []

        # transition for levels
        self.transition = -30

        # leaf particle affect
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect((4 + tree['pos'][0]), (4 + tree['pos'][1]), 23, 13)) # offsetting by 4 due to tree sprite
            # Rect(x, y, width, height)

        # spawn the ememies
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0: 
                self.player.pos = spawner['pos']
                self.player.air_time = 0 # reset air time
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))


    def run(self):
        '''
        runs the Game
        '''
        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        self.sfx['ambience'].play(-1)

        # creating an infinite game loop
        while True:
            self.display.fill((0, 0, 0, 0))    # outlines
            # clear the screen for new image generation in loop
            self.display_2.blit(self.assets['background'], (0,0)) # no outline

            self.screenshake = max(0, self.screenshake-1) # resets screenshake value

            # level transiition
            if not len(self.enemies): # no enemies
                self.transition += 1 # start timer, increasing value past 0
                if self.transition > 30: 
                    self.level = min(self.level + 1, self.max_level) # increase level
                    self.load_level(self.level) # -1 since we start at level 0
            if self.transition < 0:
                self.transition += 1 # goes up automatically until 0

            if self.dead: # get hit once
                self.dead += 1
                if self.dead >= 10: # to make the level transitions smoother
                    self.transition = min(self.transition + 1, 30) # go as high as it can without changing level
                if self.dead > 40: # timer that starts when you die
                    self.load_level(self.level)

            # move 'camera' to focus on player, make him the center of the screen
            # scroll = current scroll + (where we want the camera to be - what we have/can see currently) 
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width()/2 - self.scroll[0])  / 30  # x axis
            self.scroll[1] += (self.player.rect().centery - self.display.get_height()/2 - self.scroll[1]) / 30

            # fix the jitter
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # spawn particles
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update() # updates clouds before the rest of the tiles
            self.clouds.render(self.display_2, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            # render the enemies
            for enemy in self.enemies.copy():
                kill =  enemy.update(self.tilemap, (0,0))
                enemy.render(self.display, offset=render_scroll)
                if kill: # if enemies update fn returns true [**]
                    self.enemies.remove(enemy) 

            if not self.dead:
                # update player movement
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # render/spawn bullet projectiles
            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1] 
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1])) # spawns it the center of the projectile
                if self.tilemap.solid_check(projectile[0]): # if location is a solid tile
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random())) # (math.pi if projectile[1] > 0 else 0), sparks bounce in oppositie direction if hit wall which depends on projectile direction
                elif projectile[2] > 360: #if timer > 6 seconds
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50: # if not in dash
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)  # apply screenshake, larger wont be overrided by a smaller screenshake
                        for i in range(30): # when projectile hits player
                            # on death sparks
                            angle = random.random() * math.pi * 2 # random angle in a circle
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random())) 
                            # on death particles
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle +math.pi) * speed * 0.5, math.sin(angle * math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            # spark affect
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # ouline based on display
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0)) # 180 opaque, 0 transparent
            self.display_2.blit(display_sillhouette, (0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset) # putting what we drew onframe back into display
            

            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3 # making the parlitcle move back and forth smooth'y
                if kill:
                    self.particles.remove(particle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: # have to code the window closing
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: # referencing right and left arrow keys
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT: 
                        self.movement[1] = True
                    if event.key == pygame.K_UP: # jump!, dont care about it's release as I dont want a constant jump on hold
                        if self.player.jump():  # velocity pointing upwards, gravity will pull player back down over time
                            self.sfx['jump'].play()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP: # when key is released
                    if event.key == pygame.K_LEFT: 
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT: 
                        self.movement[1] = False

            # implementing transition
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) # display center of screen, 30 is the timer we chose, 30 * 8 = 180
                transition_surf.set_colorkey((255, 255, 255)) # making the circle transparent now
                self.display_2.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0)) # cast display 2 on display

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset) # render (now scaled) display image on big screen
            pygame.display.update()
            self.clock.tick(60) # run at 60 fps, like a sleep

# returns the game then runs it
Game().run()