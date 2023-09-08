import math
import pygame
from Animation import Animation

class Bullet:
    def __init__(self, x, y, angle, speed=5, target_tile = None, base_folder = "", filename="bullet.png"):
        from main import screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        self.target_tile = target_tile
        self.offset = (0,0)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        #self.animation = Animation(screen, base_folder, filename, False, (32,32))
        self.offset = (32, 32)
        self.target_reached = False

    def update(self):
        from main import screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
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
        from main import screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        pygame.draw.circle(screen, (0,0,0), (self.x + self.offset[0], self.y + self.offset[1]), 2)
        #self.animation.draw(self.x, self.y, self.angle)