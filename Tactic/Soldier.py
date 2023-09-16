import os
from Animation import Animation
from Structure import Structure
import math
import pygame
from Bullet import Bullet
import pygame.mixer
from Unit import Unit

from config import  pick_random_name, get_unit_settings, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH


class Soldier(Unit):
    
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Gunner', screen=None, gun_sound_file="assets\\sounds\\pistol.wav"):
        super().__init__(target_tile, player, grid, base_folder, screen)

        self.gun_sound = pygame.mixer.Sound(gun_sound_file)
        self.screen = screen
        self.type = "Soldier"
        self.settings = get_unit_settings(self.type)

        self.MOVE_SPEED = self.settings["Speed"]
        self.grid = grid
        self.max_move = self.settings["Max Move Range"]
        self.max_action_points = self.settings["Max AP"]
        self.action_points = self.max_action_points  
        self.max_health = self.settings["Max HP"]
        self.health = self.max_health
        self.NUM_BULLETS = self.settings["Pistol"]["Num Bullet Per Shot"]
        self.BULLET_SPEED = self.settings["Pistol"]["Bullet Speed"]
        self.FIRING_RATE = self.settings["Pistol"]["Firing Rate"]
        self.fire_range = self.settings["Pistol"]["Max Attack Range"]
        self.attack_damage = self.settings["Pistol"]["Damage"]

        self.name = pick_random_name()
        self.grid = grid
        self.is_alive = True
        self.move_cost = self.settings["Move Cost"]
        self.fire_cost = self.settings["Pistol"]["Fire Cost"]
        self.actions = {"Move To":self.move_cost, "Fire":self}

        self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)  

        self.animations = {}
        self.current_animation = "Idle"
        self.current_action = None
        self.angle = 0
        self.offset = (32,32)
        self.tile = None
        self.place_on_tiles(target_tile)
        self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)
        self.load_animations(base_folder)
        self.bullets = []
        self.action_rects = []
        self.action_menu_rect = None
        self.is_driver = False

        self.target_point = None
        self.origin_point = None
        self.dx = 0
        self.dy = 0
        self.target_x = 0
        self.target_y = 0

    def place_on_tiles(self, tile):
        tile.unit = self
        if self.tile:
            self.tile.unit = None
        self.tile = tile

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
            action_pos = (self.x, self.y - 30 - index * 30)

            # Check if the mouse is hovering over this action
            if self.action_rects[index].collidepoint(mouse_pos):
                text_surface = font.render(action, True, (255, 255, 0))  # Hover color
            else:
                text_surface = font.render(action, True, (255, 255, 255))  # Default color

            self.screen.blit(text_surface, action_pos)

    def draw_actions_menu(self):  # Added soldier_name as a parameter
        soldier_name = self.name
        font = pygame.font.SysFont(None, 25)
        title_font = pygame.font.SysFont(None, 30)  # Font for the soldier's name
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position

        # Initialize the list to store action rects
        self.action_rects = []
        action_pos = (self.x, self.y - 30 - (len(self.actions)) * 30)        
        title_surface = title_font.render(soldier_name, True, (0, 0, 255))
        title_rect = title_surface.get_rect(topleft=action_pos)
        self.action_rects.append(title_rect)

        # First, calculate the rects for each action based on their positions
        for index, action in enumerate(self.actions):
            action_pos = (self.x, self.y - 30 - index * 30)  # Shifted down by 60 units to make space for soldier's name
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

        # Render and draw the soldier's name
        action_pos = (self.x, self.y - 30 - (len(self.actions)) * 30)
        title_surface = title_font.render(soldier_name, True, (0, 0, 255))  # Blue color for distinction
        title_rect = title_surface.get_rect(topleft=action_pos)
        pygame.draw.rect(self.screen, (100, 100, 100), title_rect)  # Gray background for the title
        self.screen.blit(title_surface, action_pos)

        # Draw each action text with appropriate color based on hover state
        for index, action in enumerate(self.actions):
            action_pos = (self.x, self.y - 30 - (index) * 30)  # Adjusted for the title

            # Check if the mouse is hovering over this action
            if self.action_rects[index+1].collidepoint(mouse_pos):
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
        self.animations["Idle"] = Animation(self.screen, base_folder,"Gunner" ,"Idle", -1, self.offset, 90)
        self.animations["Walk"] = Animation(self.screen, base_folder,"Gunner" , "Walk", -1, self.offset, 90)
        self.animations["Die"] = Animation(self.screen, base_folder,"Gunner" , "Die", 0, self.offset, 90)
        self.animations["Fire"] = Animation(self.screen, base_folder,"Gunner" , "Fire", 0, self.offset, 90)
        self.animations["GunEffect"] = Animation(self.screen, base_folder,"Gunner" , "GunEffect", False, self.offset, 90)
        #self.animations["Bullet"] = Animation(self.screen, base_folder, "Bullet", False, self.offset)


    def calc_screen_pos(self,tile_x, tile_y):
        screen_x = tile_x * TILE_SIZE
        screen_y = tile_y * TILE_SIZE
        return screen_x, screen_y

    def draw(self):
        if self.is_driver:
            return
        self.animations[self.current_animation].draw(self.x, self.y, -self.angle)
        if self.current_animation == "Fire":
            self.animations["GunEffect"].draw(self.x, self.y, -self.angle, (14,-15))

        rect = self.animations[self.current_animation].get_current_rect()

        for bullet in self.bullets:
            bullet.draw()
        # Assuming soldier_rect is the rectangle of the soldier sprite
        status_bar_x = self.x + rect.left
        status_bar_y = self.y + 32 + 16

        # Draw health status bar
        self.draw_status_bar(status_bar_x, status_bar_y, self.health, self.max_health, HEALTH_COLOR)
        self.draw_status_bar(status_bar_x, status_bar_y + STATUS_BAR_HEIGHT, self.action_points, self.max_action_points, POINTS_COLOR)


        if self.current_action == "choosing_move_target":
            self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), min(self.max_move, self.action_points), (00, 100, 00, 50), self.current_action)       

        if self.current_action == "choosing_fire_target":
            self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), self.fire_range, (100, 00, 00, 50), self.current_action)       


        if self.current_action == "choosing_action":
            self.draw_actions_menu()
        

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
        
        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        squares_to_target = (target_x - self.x) / TILE_SIZE, (target_y - self.y) / TILE_SIZE
        movement_cost = abs(squares_to_target[0]) + abs(squares_to_target[1]) * self.move_cost
        self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.tile.unit = None
            self.tile = target_tile
            if not target_tile.unit:
                self.tile.unit = self
            elif target_tile.unit.type != "Tank" and target_tile.unit.type != "Boat":
                self.tile.unit = None
                self.tile = target_tile
                
            self.grid.selected_tile = target_tile
            self.action_points -= movement_cost
            self.target_x, self.target_y = target_x, target_y 
            self.current_animation = "Walk"
            self.animations["Walk"].play()
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if(self.distance_to_target > 1):
                # Unit's speed
                speed = 2
                self.dx = ((self.target_x - self.x) / self.distance_to_target) * speed
                self.dy = ((self.target_y - self.y) / self.distance_to_target) * speed

    def fire(self, target_tile):
        if self.is_alive == False:
            return
        
        if target_tile.unit and target_tile.unit.is_alive == False:
            return

        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        movement_cost = self.fire_cost
        #angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.gun_sound.play()
            
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.x + self.offset[0], self.y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.action_points -= movement_cost
            self.animations["Fire"].play()
            self.animations["GunEffect"].play()
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_animation = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)

            speed = 15
            #target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.bullets.append(Bullet(self.origin_point[0], self.origin_point[1],  self.angle , self.screen, speed, target_tile, self.base_folder, "Bullet"))

    def update(self, inputs):
        if self.is_driver:
            return
        self.hover_menu = self.action_menu_rect and self.action_menu_rect.collidepoint(inputs.mouse.pos)

        if inputs.mouse.clicked[0]:  # Left click 
            if self.grid.selected_tile and self.current_action is None and self.grid.selected_tile.unit == self and self.is_alive:
                self.current_action = "choosing_action"

            elif self.current_action == "choosing_move_target":
                touching = False
                for tile in self.grid.highlighted_tiles:
                    if tile.rect.collidepoint(inputs.mouse.pos):
                        touching = True
                        self.move(tile)
                        self.current_action = "move_to_target"  
                if not touching:
                    self.current_action = None
            elif self.current_action == "choosing_fire_target":
                touching = False
                for tile in self.grid.highlighted_tiles:
                    if tile.rect.collidepoint(inputs.mouse.pos):
                        touching = True
                        if tile.unit and tile.unit.player != self.player:
                            self.fire(tile)
                            self.current_action = "fire_to_target"                               
                if not touching:
                    self.current_action = None

            elif self.current_action == "choosing_action":
                if self.hover_menu:
                    for index, action in enumerate(self.actions):
                        if self.action_rects[index+1].collidepoint(inputs.mouse.pos):
                            if action == "Move To":
                                self.current_action = "choosing_move_target"
                            elif action == "Fire":
                                self.current_action = "choosing_fire_target"
                            elif action == "Build":
                                pass

                else:
                    self.current_action = None     

        elif inputs.mouse.clicked[2]:  
                self.current_action = None     

        elif inputs.keyboard.clicked[pygame.K_ESCAPE]:
                self.current_action = None

        self_selected = False            
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
            self_selected = True            
            if (self.current_action == "choosing_move_target" or self.current_action == "choosing_fire_target"):
                self.angle = math.atan2(inputs.mouse.pos[1] - self.y - self.offset[1], inputs.mouse.pos[0] - self.x - self.offset[0]) * 180 / math.pi

        for animation in self.animations.values():
            animation.update(self.x, self.y)        
        

        if self.current_action == "move_to_target":
            self.current_animation == "Walk"
            # Update the unit's position
            self.x += self.dx
            self.y += self.dy

            # Check if the unit is close enough to the target to stop
            if abs(self.x - self.target_x ) < 1 and abs(self.y - self.target_y) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.animations["Walk"].stop()
                self.current_animation = "Idle"
                self.current_action = None
                if self.grid.selected_tile.unit and (self.grid.selected_tile.unit.type == "Tank" or self.grid.selected_tile.unit.type == "Boat"):
                    self.grid.selected_tile.unit.take_seat(self)
                

        for bullet in self.bullets:
            bullet.update()
            if bullet.target_reached:
                self.bullets.remove(bullet)
                if bullet.target_tile.unit:
                    bullet.target_tile.unit.take_damage(10)
                    self.current_action = None

        if self.current_animation == "Fire":
            finished = self.animations["Fire"].is_finished() and self.animations["GunEffect"].is_finished()
            if finished:
                self.animations["GunEffect"].reset()
                self.animations["Fire"].reset()
                self.current_animation = "Idle"
                
        if self_selected:
            self.draw_points_left()

    def draw_points_left(self):
        # Draw each action text with appropriate color based on hover state
        font = pygame.font.SysFont(None, 15)
        dark_gray = (50, 50, 50, 128)  # Dark gray color
        padding = 2  # Amount of space you want around the text inside the rectangle

        number_surface = font.render(f"{int(self.action_points)}/{self.max_action_points} pts", True, (255, 255, 255))  # This will render the number in white color

        background_surface = pygame.Surface((number_surface.get_width() + 2 * padding, 
                                            number_surface.get_height() + 2 * padding), 
                                            pygame.SRCALPHA)
        
        background_surface.fill(dark_gray)       
        # Blit the semi-transparent surface on the screen at the top-left corner of the cell
        self.screen.blit(background_surface, (self.x + padding, self.y + padding))

        # Blit the text over the semi-transparent rectangle
        self.screen.blit(number_surface, (self.x + padding, self.y + padding))

    def process_events(self, event):
        pass

    def take_damage(self, damage):
        super().take_damage(damage)

    def die(self):
        self.is_alive = False
        self.animations["Die"].play()
        self.current_animation = "Die"

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
