import os
from abc import ABC, abstractmethod
from Animation import Animation
from Structure import Structure
import math
import pygame
from Bullet import Bullet
import pygame.mixer

class Unit:

    
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Gunner', screen=None):
        gun_sound_file="assets\\sounds\\machinegun.wav"
        self.gun_sound = pygame.mixer.Sound(gun_sound_file)
        self.screen = screen
        self.max_move = 5
        self.fire_range = 8
        self.grid = grid
        self.is_alive = True
        self.base_folder = base_folder
        self.player = player
        from config import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y    
        self.target_screen_x = None  # Target position for movement
        self.target_screen_y = None
        if target_tile:
            self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)  
            self.tile = target_tile
            self.tile.unit = self
        self.animations = {}
        self.current_animation = "Idle"
        self.current_action = None
        self.angle = 0
        self.offset = (32,32)
        self.load_animations(base_folder)
        self.min_distance = 99999
        self.bullets = []
        self.action_rects = []
        self.action_menu_rect = None


    @abstractmethod
    def draw_actions_menu(self):
        pass


    @abstractmethod
    def take_damage(self, damage):
        pass

    def load_animations(self, base_folder):
        pass

    @abstractmethod
    def calc_screen_pos(self,tile_x, tile_y):
        pass

    def draw_flag(self):
        pass                

    @abstractmethod
    def draw_status_bar(self, x, y, current_value, max_value, color):
        pass
    
    @abstractmethod    
    def move(self, target_tile):
        pass

    @abstractmethod    
    def fire(self, target_tile):
        pass

    @abstractmethod    
    def update(self, mouse_pos):
        pass

    @abstractmethod    
    def process_events(self, event):
        pass

    @abstractmethod    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    @abstractmethod    
    def die(self):
        pass

    def draw_piece_perimeter(self, transformed_piece, x, y, color):
        line_width = 5
        #transformed_shape = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
        
        # Draw perimeter line for the transformed shape
        for i, row in enumerate(transformed_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        neighbor_x, neighbor_y = j + dx, i + dy
                        
                        # Check if the neighboring cell is outside the piece
                        if 0 <= neighbor_x < len(row) and 0 <= neighbor_y < len(transformed_piece.shape):
                            is_empty_inside = transformed_piece.shape[neighbor_y][neighbor_x] == 0
                        else:
                            is_empty_inside = True  # Treat cells outside the shape boundary as empty
                        
                        if is_empty_inside:
                            if dx == -1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)
                            elif dx == 1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j + 1) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)
                            elif dy == -1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i) * self.cell_size],
                                                line_width)
                            elif dy == 1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i + 1) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)

    def draw_points_as_squares(self, x, y, current_points, max_points, color, max_squares_per_row):
        pass
