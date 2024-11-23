import pygame
import math
import random


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        '''
        initializes entities
        (game, entitiy type, position, size)
        '''
        self.game = game
        self.type = e_type
        self.pos = list(pos) #make sure each entitiy has it's own list, (x,y)
        self.size = size
        self.speed = 5
        self.velocity = [0,0,0, 0]
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        self.action = ''
        self.anim_offset = (0, 0) #renders with an offset to pad the animation against the hitbox
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        '''
        creates a rectangle at the entitiies current postion
        '''
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        '''
        sets a new action to change animation
        (string of animation name) -> animation
        '''
        if action != self.action: # if action has changed
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()


    
    def update(self, tilemap, movement=(0,0)):
        '''
        updates frames and entitiy position 
        '''
        #Normalize movement vector
        movement_magnitude = math.sqrt((movement[0] * movement[0] + movement[1] * movement[1]))
        if movement_magnitude > 0:
            movement = (movement[0] / movement_magnitude, movement[1] / movement_magnitude)

        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False} # this value will be reset every frame, used to stop constant increase of velocity

        frame_movement = ((movement[0] + self.velocity[0]) * self.game.game_speed * self.speed, (movement[1] + self.velocity[1]) * self.game.game_speed * self.speed) # movement based on velocity

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect() # getting the entities rectange

        # move tile based on collision on y axis
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0: # if moving right and you collide with tile
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0: # if moving left
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        # Note: Y-axis collision handling comes after X-axis handling
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()  # Update entity rectangle for y-axis handling
        # move tile based on collision on y axis
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0: # if moving right and you collide with tile
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0: # if moving left
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y


        self.last_movement = movement # keeps track of movement


        if self.collisions['down'] or self.collisions['up']: # if object hit, stop velocity
            self.velocity[1] = 0

        self.animation.update() # update animation


    def render(self, surf, offset={0,0}):
        '''
        renders entitiy asset
        '''
        surf.blit(pygame.transform.flip(self.animation.img(), False, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1])) # fliping agasint horizontal axis

    def shoot(self, target, bullet_type):
        '''
        shoots a bullet
        '''
        bullet = Bullet(self.game, self.pos, (8, 8), target, bullet_type)
        self.game.bullets.append(bullet)

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        '''
        instantiates player entity
        (game, position, size)
        '''
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0,0)):
        '''
        updates players animations depending on movement
        '''
        super().update(tilemap, movement=movement)


    def render(self, surf, offset={0,0}):
        '''
        partly overriding rendering for dashing
        '''
        super().render(surf, offset=offset) # show player

    def shoot(self, target):
        '''
        shoots a bullet
        '''
        super().shoot(target, 'player')
            

class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        '''
        instantiates the enemies
        (game, position: tuple, size)
        '''
        super().__init__(game, 'enemy', pos, size)
        self.set_action('idle')
    
    def update(self, tilemap, movement=(0,0)):
        super().update(tilemap, movement=movement)
            

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

    def shoot(self, target):
        '''
        shoots a bullet
        '''
        super().shoot(target, 'enemy')

        

class Bullet(PhysicsEntity):
    def __init__(self, game, pos, size, target, bullet_type):
        '''
        instantiates the bullets
        (game, position: tuple, size, target)
        '''
        super().__init__(game, bullet_type+'bullet', pos, size)
        self.target = target
        self.speed = 10
        self.type = bullet_type

    def update(self, tilemap, movement=(0,0)):
        '''
        updates the bullets position
        '''
        super().update(tilemap, movement=movement)

        # move towards target in top down
        angle = math.atan2(self.target[1] - self.pos[1], self.target[0] - self.pos[0])
        self.velocity = [math.cos(angle) * self.speed, math.sin(angle) * self.speed]

        # check if bullet is out of bounds
        if self.pos[0] < 0 or self.pos[0] > self.game.tilemap.size[0] or self.pos[1] < 0 or self.pos[1] > self.game.tilemap.size[1]:
            self.game.bullets.remove(self)

                # check if bullet collides with player
        if self.rect().colliderect(self.game.player.rect()) and self.type == 'enemy':
            self.game.bullets.remove(self)
            self.game.player.health -= 1

        # check if bullet collides with enemy
        for enemy in self.game.enemies:
            if self.rect().colliderect(enemy.rect()) and self.type == 'player':
                self.game.bullets.remove(self)
                enemy.health -= 1
        
        # check if bullet collides with tile
        for rect in tilemap.physics_rects_around(self.pos):
            if self.rect().colliderect(rect):
                self.game.bullets.remove(self)
        
        
            
    def render(self, surf, offset=(0, 0)):
        '''
        renders the bullet
        '''
        if self.type == 'playerbullet':
            surf.blit(self.game.assets['playerbullet'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        #else:
        #    surf.blit(self.game.assets['bullet'], (self.pos[0] - offset[0], self.pos[1] - offset[1]))

       