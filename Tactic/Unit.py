import os
from Animation import Animation
from Structure import Structure
import math
import pygame

class Unit:

    
    def __init__(self, target_tile, unit_type='soldier', action_points=10, base_folder='assets\\images\\Gunner'):
        from main import screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        self.unit_type = unit_type
        self.action_points = action_points
        self.max_action_points = action_points        
        self.target_screen_x = None  # Target position for movement
        self.target_screen_y = None
        self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)  # Current position on the screen
        target_tile.unit = self
        self.tile = target_tile
        self.animations = {}
        self.current_action = "Idle"
        self.load_animations(base_folder)
        self.angle = 0

    def load_animations(self, base_folder):
        from main import screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        self.animations["Idle"] = Animation(screen, base_folder, "Idle", True)
        self.animations["Walk"] = Animation(screen, base_folder, "Walk", True)
        self.animations["Fire"] = Animation(screen, base_folder, "Fire", False)
        self.animations["Die"] = Animation(screen, base_folder, "Die", False)


    def calc_screen_pos(self,tile_x, tile_y):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        screen_x = tile_x * TILE_SIZE + TILE_SIZE / 2
        screen_y = tile_y * TILE_SIZE + TILE_SIZE / 2
        return screen_x, screen_y

    def can_attack(self, target_tile):
        """Check if the unit can attack a target."""
        distance = abs(self.x - target_tile.x) + abs(self.y - target_tile.y)
        return distance == 1

    def draw(self):
        self.draw_soldier()

    def move(self, target_tile):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        squares_to_target = (target_x - self.x) / TILE_SIZE, (target_y - self.y) / TILE_SIZE
        movement_cost = abs(squares_to_target[0]) + abs(squares_to_target[1])
        self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.target_x = target_x
            self.target_y = target_y
            self.movement_cost = movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_action = "Walk"
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if(self.distance_to_target > 1):
                # Unit's speed
                speed = 1
                self.dx = ((self.target_x - self.x) / self.distance_to_target) * speed
                self.dy = ((self.target_y - self.y) / self.distance_to_target) * speed
                speed= speed

    def update(self):
        """Update the unit's position if it's moving."""
        self.animations[self.current_action].update(self.x, self.y)
        if self.current_action == "Walk":
            # Update the unit's position
            self.x += self.dx
            self.y += self.dy

            # Check if the unit is close enough to the target to stop
            if abs(self.x - self.target_x) < abs(self.dx) and abs(self.y - self.target_y) < abs(self.dy):
                self.x = self.target_x
                self.y = self.target_y
                self.current_action = "Idle"
                self.angle = 0
                self.action_points -= self.movement_cost
                self.movement_cost = 0
        elif self.current_action == "Fire":
            pass
        elif self.die:
            pass
        else:
            pass

        animation = self.animations[self.current_action]
        if animation.is_finished() and not animation.is_looping:
            self.current_action = "Idle"

        


    def attack(self, target_unit):
        """Attack a target unit."""
        if self.action_points > 0:
            damage = 10  # static damage for simplicity; can be made dynamic later
            target_unit.take_damage(damage)
            self.action_points -= 2  # Assuming an attack takes 2 action points

    def take_damage(self, damage):
        """Reduce the unit's health by the given damage."""
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        """Handle the unit's death."""
        # Remove the unit from the tile and game
        # This can be expanded with more features like animations, sounds, etc.

    def build(self, target_tile, structure_type):
        """Build a structure on a target tile."""
        if self.action_points > 0 and not target_tile.structure:
            new_structure = Structure(target_tile.x, target_tile.y, structure_type)
            target_tile.structure = new_structure
            self.action_points -= 3  # Assume building costs 3 action points

    def draw_soldier(self):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y
        x, y = self.x, self.y
        self.animations[self.current_action].draw(x, y, -self.angle+ 90)
