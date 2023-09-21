import math
import pygame
from Animation import Animation
from config import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY

class Bullet:
    def __init__(self, x, y, angle, screen, speed=5, target_tile = None, base_folder = "", image=None, damage = 1, reach_callback=None, explosion_sound=None, explosion_animation=None):
        self.explosion_animation = explosion_animation
        self.explosion_sound = explosion_sound
        self.reach_callback = reach_callback
        self.screen = screen
        self.target_tile = target_tile
        self.offset = (0,0)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.animation = image
        #self.offset = (32, 32)
        self.target_reached = False
        self.is_alive = True

    def update(self):
        if self.explosion_animation:
            self.explosion_animation.update()

        if not self.is_alive:
            return
        # Update bullet position based on angle and speed
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        target_x = self.target_tile.x * TILE_SIZE
        target_y = self.target_tile.y * TILE_SIZE
        delta_x, delta_y = target_x - self.x, target_y - self.y
        distance = math.sqrt((delta_x)**2 + (delta_y)**2)
        if distance < self.speed:
            self.is_alive = False
            self.target_reached = True
            if self.reach_callback:
                self.reach_callback(self)
            self.target_tile.unit.take_damage(self.damage)
            if self.explosion_animation:
                self.explosion_animation.play()
            if self.explosion_sound:
                self.explosion_sound.play()

        
            

    def draw(self):
        if self.explosion_animation and self.explosion_animation.is_playing:            
            target_x = self.target_tile.x * TILE_SIZE
            target_y = self.target_tile.y * TILE_SIZE        
            center = self.explosion_animation.get_current_rect().center
            center = center[0] - 80, center[1]      
            self.explosion_animation.draw(target_x, target_y, -self.angle, center)


        if not self.is_alive:
            return
                        
        if self.animation:
            self.animation.draw(self.x, self.y, -self.angle)
        else:
            pygame.draw.circle(self.screen, (0,0,0), (self.x , self.y ), 2)
