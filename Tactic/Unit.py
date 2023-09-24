import os
from abc import ABC, abstractmethod
from Animation import Animation
from Structure import Structure
import math
import pygame
from Bullet import Bullet
import pygame.mixer
from config import get_unit_settings, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH

class Unit:

    
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Gunner', screen=None, type=None, action_finished=None):
        gun_sound_file="assets\\sounds\\machinegun.wav"
        self.action_finished = action_finished
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
        self.screen_x = 0
        self.screen_y = 0
        self.draw_x = 0
        self.draw_y = 0
        self.tile = None
        self.world_pos_x, self.world_pos_y = 0, 0
        if target_tile:
            self.world_pos_x, self.world_pos_y = target_tile.x * TILE_SIZE, target_tile.y * TILE_SIZE
            self.screen_x, self.screen_y = self.calc_screen_pos((self.world_pos_x, self.world_pos_y))  
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
        self.current_event = None

        self.original_hp = 0
        self.can_attack = True
        self.is_disabled = False
        self.type = type
        self.settings = get_unit_settings(self.type)
        self.current_player = None
        self.current_game_state = None
        self.swapped = False
        self.is_vehicle = False

        self.MOVE_SPEED = self.settings["Speed"]
        self.grid = grid
        self.max_move = self.settings["Max Move Range"]
        self.max_action_points = self.settings["Max AP"]
        self.action_points = self.max_action_points  
        self.max_health = self.settings["Max HP"]
        self.health = self.max_health / 2
        self.NUM_BULLETS = self.settings["Num Bullet Per Shot"]
        self.BULLET_SPEED = self.settings["Bullet Speed"]
        self.FIRING_RATE = self.settings["Firing Rate"]
        self.fire_range = self.settings["Max Attack Range"]
        self.attack_damage = self.settings["Damage"]
        self.seat_taken = 0
        if "Seats" in self.settings.keys():
            self.seats = self.settings["Seats"]
            self.seat_left = self.seats		
        self.move_cost = self.settings["Move Cost"]
        self.fire_cost = self.settings["Fire Cost"]        
#position
# max_hp
# hp
# damage
# AP
# can_attack
# is_disabled
# resources
# damage
# Max_Move_Range
# Max_Attack_Range
# Move_Cost
# Fire_Cost
    def get_stats(self):
        stats = {}
        stats["HP"] = self.health
        stats["AP"] = self.action_points
        stats["Damage"] = self.attack_damage
        stats["Move Range"] = self.max_move
        stats["Attack Range"] = self.fire_range
        stats["Type"] = self.type
        stats["Player"] = self.player
        return stats

    def draw_actions_menu(self):
        font = pygame.font.SysFont(None, 25)
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position

        # Initialize the list to store action rects
        self.action_rects = []

        # First, calculate the rects for each action based on their positions
        for index, action in enumerate(self.actions):
            action_pos = (self.draw_x, self.draw_y - 30 - index * 30)
            text_surface = font.render(action, True, (255, 255, 255))
            rect = text_surface.get_rect(topleft=action_pos)
            self.action_rects.append(rect)

        # Calculate the encompassing rectangle
        if self.action_rects:
            self.action_menu_rect = self.action_rects[0].copy()
            for action_rect in self.action_rects[1:]:
                self.action_menu_rect.union_ip(action_rect)

            # Inflate the encompassing rectangle for padding
            padding = 10
            self.action_menu_rect.inflate_ip(padding * 2, padding * 2)

            # Draw the encompassing rectangle
            pygame.draw.rect(self.screen, (50, 50, 50), self.action_menu_rect)

        # Draw each action text with appropriate color based on hover state
        for index, action in enumerate(self.actions):
            action_pos = (self.draw_x, self.draw_y - 30 - index * 30)
            if self.is_disabled or (action == "Fire" and not self.can_attack):                
                text_surface = font.render(f"{action}", True, (100, 100, 100))
            elif self.action_rects[index].collidepoint(mouse_pos):
                text_surface = font.render(f"{action}", True, (255, 255, 0))  # Hover color
            else:
                text_surface = font.render(f"{action}", True, (255, 255, 255))  # Default color

            self.screen.blit(text_surface, action_pos)

    def place_on_tiles(self, tile):
        tile.unit = self
        if self.tile:
            self.tile.unit = None
        self.tile = tile

    def get_unit_out(self):
        if self.action_points < 1:
            return
        if self.seat_taken > 0:
            self.action_points -= 1
            self.seat_taken -= 1
            self.seat_left += 1
            last_passenger = self.passengers.pop()            
            free_tile = self.find_free_tile(self.tile)
            free_tile.unit = last_passenger
            last_passenger.is_driver = False
            last_passenger.x = free_tile.x * TILE_SIZE
            last_passenger.y = free_tile.y * TILE_SIZE
            self.grid.selected_tile = free_tile
            self.tile.unit = self
            self.current_action = None
            return last_passenger

    def take_seat(self, unit):
        if self.seat_left == 0:
            return False
        self.passengers.append(unit)
        self.seat_left -= 1
        self.seat_taken += 1
        unit.is_driver = True
        unit.current_action = None
        return True      
    

    def calc_screen_pos(self, world_pos):
        screen_x = world_pos[0] + self.grid.get_camera_screen_position()[0]
        screen_y = world_pos[1] + self.grid.get_camera_screen_position()[1]
        return screen_x, screen_y
        


    def place_unit(self, inputs):
        self.mouse_x, self.mouse_y = inputs.mouse.pos
        # Snap mouse position to grid
        grid_x = (self.mouse_x // TILE_SIZE) * TILE_SIZE 
        grid_y = (self.mouse_y // TILE_SIZE) * TILE_SIZE       
        self.screen_x = grid_x
        self.screen_y = grid_y
        self.tower.update((self.screen_x, self.screen_y), self.tower.angle if self.tower.angle else 0) 
        
        if inputs.mouse.clicked[0] and self.grid.selected_tile and not self.grid.selected_tile.unit: 
            self.place_on_tiles(self.grid.selected_tile)
            self.action_finished(self)

    def on_message(self, event, value):
        if event == "game_state_changed":
            self.current_game_state = value
        elif event == "player_changed":
            self.current_player = value


    @abstractmethod
    def draw_actions_menu(self):
        pass


    @abstractmethod
    def take_damage(self, damage):
        pass

    def load_animations(self, base_folder):
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
