import math
import pygame
from Animation import Animation
from config import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY

class Bullet:
    def __init__(self, x, y, angle, screen, speed=5, target_tile = None, base_folder = "", image=None, damage = 1):
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

    def update(self):
        # Update bullet position based on angle and speed
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        target_x = self.target_tile.x * TILE_SIZE
        target_y = self.target_tile.y * TILE_SIZE
        delta_x, delta_y = target_x - self.x, target_y - self.y
        distance = math.sqrt((delta_x)**2 + (delta_y)**2)
        if distance < self.speed:
            self.target_reached = True
            

    def draw(self):
        if self.animation:
            self.animation.draw(self.x, self.y, self.angle)
        else:
            pygame.draw.circle(self.screen, (0,0,0), (self.x , self.y ), 2)
