import os
from Animation import Animation
from Structure import Structure
import math
import pygame
from Bullet import Bullet

STATUS_BAR_WIDTH = 60  # or the width of your soldier sprite
STATUS_BAR_HEIGHT = 6  # adjust based on preference
HEALTH_COLOR = (255, 0, 0)  # Red
POINTS_COLOR = (0, 0, 255)  # Blue
BACKGROUND_COLOR = (200, 200, 200)  # Light gray for depleted sections
SQUARE_SIZE = 5  # adjust based on preference
SQUARE_SPACING = 1  # spacing between squares
MAX_SQUARES_PER_ROW = 10 
class Unit:

    
    def __init__(self, target_tile, player, grid, unit_type='soldier', action_points=30, base_folder='assets\\images\\Gunner', screen=None):
        self.screen = screen
        self.max_move = 5
        self.grid = grid
        self.is_alive = True
        self.base_folder = base_folder
        self.player = player
        self.health = 100
        self.max_health = self.health
        from main import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        self.unit_type = unit_type
        self.action_points = action_points
        self.max_action_points = action_points        
        self.target_screen_x = None  # Target position for movement
        self.target_screen_y = None
        self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)  
        target_tile.unit = self
        self.tile = target_tile
        self.animations = {}
        self.current_action = "Idle"
        self.angle = 0
        self.offset = (32,32)
        self.load_animations(base_folder)
        self.min_distance = 99999
        self.bullets = []
        self.actions = ["Move To", "Fire", "Build"]
        self.action_rects = []

    def draw_actions_menu(self):
        font = pygame.font.SysFont(None, 25)
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position

        # Initialize the list to store action rects
        self.action_rects = []

        # First, calculate the rects for each action based on their positions
        for index, action in enumerate(self.actions):
            action_pos = (self.x, self.y - 30 - index * 30)
            text_surface = font.render(action, True, (255, 255, 255))
            rect = text_surface.get_rect(topleft=action_pos)
            self.action_rects.append(rect)

        # Calculate the encompassing rectangle
        if self.action_rects:
            encompassing_rect = self.action_rects[0].copy()
            for action_rect in self.action_rects[1:]:
                encompassing_rect.union_ip(action_rect)

            # Inflate the encompassing rectangle for padding
            padding = 10
            encompassing_rect.inflate_ip(padding * 2, padding * 2)

            # Draw the encompassing rectangle
            pygame.draw.rect(self.screen, (50, 50, 50), encompassing_rect)

        # Draw each action text with appropriate color based on hover state
        for index, action in enumerate(self.actions):
            action_pos = (self.x, self.y - 30 - index * 30)

            # Check if the mouse is hovering over this action
            if self.action_rects[index].collidepoint(mouse_pos):
                text_surface = font.render(action, True, (255, 255, 0))  # Hover color
            else:
                text_surface = font.render(action, True, (255, 255, 255))  # Default color

            self.screen.blit(text_surface, action_pos)

  


    def take_damage(self, damage):
        """Reduce the unit's health by the given damage."""
        self.health -= damage
        if self.health <= 0:
            self.die()

    def load_animations(self, base_folder):
        self.animations["Idle"] = Animation(self.screen, base_folder, "Idle", True, self.offset, 90)
        self.animations["Walk"] = Animation(self.screen, base_folder, "Walk", True, self.offset, 90)
        self.animations["Die"] = Animation(self.screen, base_folder, "Die", False, self.offset, 90)
        self.animations["Fire"] = Animation(self.screen, base_folder, "Fire", False, self.offset, 90)
        self.animations["GunEffect"] = Animation(self.screen, base_folder, "GunEffect", False, self.offset, 90)
        #self.animations["Bullet"] = Animation(self.screen, base_folder, "Bullet", False, self.offset)


    def calc_screen_pos(self,tile_x, tile_y):
        from main import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        screen_x = tile_x * TILE_SIZE
        screen_y = tile_y * TILE_SIZE
        return screen_x, screen_y

    def can_attack(self, target_tile):
        """Check if the unit can attack a target."""
        distance = abs(self.x - target_tile.x) + abs(self.y - target_tile.y)
        return distance == 1

    def draw(self):
        from main import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        self.animations[self.current_action].draw(self.x, self.y, -self.angle)
        if self.current_action == "Fire":
            self.animations["GunEffect"].draw(self.x, self.y, -self.angle, (14,-15))

        rect = self.animations[self.current_action].get_current_rect()

        for bullet in self.bullets:
            bullet.draw()
        # Assuming soldier_rect is the rectangle of the soldier sprite
        status_bar_x = self.x + rect.left
        status_bar_y = self.y   # 2 pixels gap

        # Draw health status bar
        self.draw_status_bar(status_bar_x, status_bar_y, self.health, self.max_health, HEALTH_COLOR)
        STATUS_BAR_HEIGHT = 6  # adjust based on preference

        # Draw points as squares below the health bar
        points_y = status_bar_y + STATUS_BAR_HEIGHT + 1
        self.draw_points_as_squares(status_bar_x, points_y, self.action_points, self.max_action_points, POINTS_COLOR, MAX_SQUARES_PER_ROW)  

        #from main import grid
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and not self.current_action == "Walk" and self.is_alive:
            self.draw_actions_menu()
            #self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), min(self.max_move, self.action_points), (100, 00, 00, 128))       
        

    def draw_status_bar(self, x, y, current_value, max_value, color):
        # Calculate width of the filled portion
        fill_width = int(STATUS_BAR_WIDTH * (current_value / max_value))
        
        # Draw the background (depleted section)
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, (x, y, STATUS_BAR_WIDTH, STATUS_BAR_HEIGHT))
        
        # Draw the filled portion
        pygame.draw.rect(self.screen, color, (x, y, fill_width, STATUS_BAR_HEIGHT))

    def move(self, target_tile):
        if self.is_alive == False:
            return
        if hasattr(target_tile, 'no_walk'):
            if target_tile.no_walk:
                return        
        
        from main import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        squares_to_target = (target_x - self.x) / TILE_SIZE, (target_y - self.y) / TILE_SIZE
        movement_cost = abs(squares_to_target[0]) + abs(squares_to_target[1])
        self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.tile.unit = None
            self.tile = target_tile
            self.tile.unit = self
            self.action_points -= movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_action = "Walk"
            self.animations["Walk"].play()
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if self.distance_to_target < self.min_distance:
                self.min_distance = self.distance_to_target
            if(self.distance_to_target > 1):
                # Unit's speed
                speed = 2
                self.dx = ((self.target_x - self.x) / self.distance_to_target) * speed
                self.dy = ((self.target_y - self.y) / self.distance_to_target) * speed
                speed= speed

    def fire(self, target_tile):
        if self.is_alive == False:
            return
        
        if target_tile.unit and target_tile.unit.is_alive == False:
            return

        from main import  TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        movement_cost = 1
        angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
            self.action_points -= movement_cost
            self.animations["Fire"].play()
            self.animations["GunEffect"].play()
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_action = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)

            speed = 15
            #target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.bullets.append(Bullet(self.x, self.y,  angle, speed, target_tile, self.base_folder, "Bullet"))

    def update(self, x,y):

        """Update the unit's position if it's moving."""
        for animation in self.animations.values():
            animation.update(self.x, self.y)        
        
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
            self.angle = math.atan2(y - self.y, x - self.x) * 180 / math.pi

        if self.current_action == "Walk":
            # Update the unit's position
            self.x += self.dx
            self.y += self.dy

            # Check if the unit is close enough to the target to stop
            if abs(self.x - self.target_x) < 1 and abs(self.y - self.target_y) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.animations["Walk"].stop()

                self.current_action = "Idle"
                

        for bullet in self.bullets:
            bullet.update()
            if bullet.target_reached:
                self.bullets.remove(bullet)
                bullet.target_tile.unit.take_damage(10)

        if self.current_action == "Fire":
            finished = self.animations["Fire"].is_finished() and self.animations["GunEffect"].is_finished()
            if finished:
                self.animations["GunEffect"].reset()
                self.animations["Fire"].reset()
                self.current_action = "Idle"


    def take_damage(self, damage):
        """Reduce the unit's health by the given damage."""
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        self.animations["Die"].play()
        self.current_action = "Die"

    def build(self, target_tile, structure_type):
        """Build a structure on a target tile."""
        if self.action_points > 0 and not target_tile.structure:
            new_structure = Structure(target_tile.x, target_tile.y, structure_type)
            target_tile.structure = new_structure
            self.action_points -= 3  # Assume building costs 3 action points

    def draw_points_as_squares(self, x, y, current_points, max_points, color, max_squares_per_row):
        rows = (max_points + max_squares_per_row - 1) // max_squares_per_row  # Calculate the total number of rows required
        
        for i in range(max_points):
            row = i // max_squares_per_row
            col = i % max_squares_per_row
            
            square_x = x + col * (SQUARE_SIZE + SQUARE_SPACING)
            square_y = y + row * (SQUARE_SIZE + SQUARE_SPACING)
            
            if i < current_points:
                pygame.draw.rect(self.screen, color, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(self.screen, BACKGROUND_COLOR, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))
