import os
from Animation import Animation
from Structure import Structure
import math
import pygame
from Bullet import Bullet
import pygame.mixer
from Unit import Unit

from config import  GameState, pick_random_name, get_unit_settings, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH


class Soldier(Unit):
    
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Gunner', screen=None, gun_sound_file="assets\\sounds\\pistol.wav", action_finished=None):
        super().__init__(target_tile, player, grid, base_folder, screen, "Soldier-Pistol", action_finished)
        self.gun_sound = pygame.mixer.Sound(gun_sound_file)
        self.death_sound = pygame.mixer.Sound("assets\\sounds\\dying2.wav")
        self.screen = screen

        self.name = pick_random_name()
        self.grid = grid
        self.is_alive = True
        self.move_cost = self.settings["Move Cost"]
        self.fire_cost = self.settings["Fire Cost"]
        self.actions = {"Move To", "Fire"}

        self.last_fired = pygame.time.get_ticks() 
        self.animations = {}
        self.current_animation = "Idle"
        self.current_action = None
        self.angle = 0
        self.offset = (32,32)
        self.load_animations(base_folder)
        self.bullets = []
        self.action_rects = []
        self.action_menu_rect = None
        self.is_driver = False

        self.target_tile = target_tile
        self.target_point = None
        self.origin_point = None
        self.dx = 0
        self.dy = 0
        self.target_x = 0
        self.target_y = 0
        self.last_action = None
        self.last_action_target = None


    def draw_actions_menu(self):  # Added soldier_name as a parameter
        soldier_name = self.name
        font = pygame.font.SysFont(None, 25)
        title_font = pygame.font.SysFont(None, 30)  # Font for the soldier's name
        mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position

        # Initialize the list to store action rects
        self.action_rects = []
        action_pos = (self.draw_x, self.draw_y - 30 - (len(self.actions)) * 30)        
        title_surface = title_font.render(soldier_name, True, (0, 0, 255))
        title_rect = title_surface.get_rect(topleft=action_pos)
        self.action_rects.append(title_rect)

        # First, calculate the rects for each action based on their positions
        for index, action in enumerate(self.actions):
            action_pos = (self.draw_x, self.draw_y - 30 - index * 30)  # Shifted down by 60 units to make space for soldier's name
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
        action_pos = (self.draw_x, self.draw_y - 30 - (len(self.actions)) * 30)
        title_surface = title_font.render(soldier_name, True, (0, 0, 255))  # Blue color for distinction
        title_rect = title_surface.get_rect(topleft=action_pos)
        pygame.draw.rect(self.screen, (100, 100, 100), title_rect)  # Gray background for the title
        self.screen.blit(title_surface, action_pos)

        # Draw each action text with appropriate color based on hover state
        for index, action in enumerate(self.actions):
            action_pos = (self.draw_x, self.draw_y - 30 - (index) * 30)  # Adjusted for the title

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

    def draw(self):
        if self.is_driver:
            return
        
        outline_color=None
        outline_thickness=None
        if self.swapped:
            if self.player == self.current_player:
                outline_color = (0, 255, 0)
            else:
                outline_color = (255, 0, 0)
            outline_thickness = 5
        elif self.player != self.current_player:
            outline_color = (255, 0, 0)
            outline_thickness = 2		
		
        self.animations[self.current_animation].draw(self.draw_x, self.draw_y, -self.angle, None, None, outline_color, outline_thickness, outline_fade=True)

            
        if self.current_animation == "Fire":
            self.animations["GunEffect"].draw(self.draw_x, self.draw_y, -self.angle, (14,-15))

        rect = self.animations[self.current_animation].get_current_rect()

        for bullet in self.bullets:
            bullet.draw()

        # Assuming soldier_rect is the rectangle of the soldier sprite<
        status_bar_x = self.draw_x + rect.left
        status_bar_y = self.draw_y + 32 + 16

        # Draw health status bar
        self.draw_status_bar(status_bar_x, status_bar_y, self.health, self.max_health, HEALTH_COLOR)
        self.draw_status_bar(status_bar_x, status_bar_y + STATUS_BAR_HEIGHT, self.action_points, self.max_action_points, POINTS_COLOR)



        if self.current_action == "choosing_move_target":
            self.grid.highlight_tiles((self.draw_x // TILE_SIZE, self.draw_y // TILE_SIZE),self.max_move, (00, 100, 00, 50), self.current_action)       

        if self.current_action == "choosing_fire_target":
            self.grid.highlight_tiles((self.draw_x // TILE_SIZE, self.draw_y // TILE_SIZE), self.fire_range, (100, 00, 00, 50), self.current_action)       


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
        squares_to_target = (target_x - self.screen_x) / TILE_SIZE, (target_y - self.screen_y) / TILE_SIZE
        movement_cost = self.settings["Move Cost"]
        if movement_cost <= self.action_points:
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.grid.selected_tile = target_tile
            self.target_tile = target_tile
            self.action_points -= movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_animation = "Walk"
            self.animations[self.current_animation].play()
            self.distance_to_target = math.sqrt((self.target_x - self.screen_x)**2 + (self.target_y - self.screen_y)**2)
            if self.distance_to_target < self.min_distance:
                self.min_distance = self.distance_to_target

            if(self.distance_to_target > self.MOVE_SPEED):
                self.velocity_x = ((self.target_point[0] - self.origin_point[0]) / self.distance_to_target) * self.MOVE_SPEED
                self.velocity_y = ((self.target_point[1] - self.origin_point[1]) / self.distance_to_target) * self.MOVE_SPEED

            if not (self.grid.selected_tile.unit and (self.grid.selected_tile.unit.type == "Tank" or self.grid.selected_tile.unit.type == "Boat" or self.grid.selected_tile.unit.type == "Helicopter")):
                self.tile.unit = None
                self.tile = self.target_tile
                self.tile.unit = self




    def fire(self, target_tile):
        if self.is_alive == False:
            return
        
        if target_tile.unit and target_tile.unit.is_alive == False:
            return

        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        fire_cost = self.fire_cost
        #angle = math.atan2(target_y - self.screen_y, target_x - self.screen_x) * 180 / math.pi
        if fire_cost <= self.action_points:
            self.bullets_fired = 0
            self.gun_sound.play()
            
            self.target_tile = target_tile
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.action_points -= fire_cost
            self.animations["Fire"].play()
            self.animations["GunEffect"].play()
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_animation = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.screen_x)**2 + (self.target_y - self.screen_y)**2)

    def bullet_reach_target(self, bullet):
        pass

    def update(self, inputs):
        if self.current_game_state == GameState.UNIT_PLACEMENT:
            self.place_unit(inputs)
            return
        if self.is_driver or self.current_player != self.player:
            self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
            self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]  
            return
        self.hover_menu = self.action_menu_rect and self.action_menu_rect.collidepoint(inputs.mouse.pos)
        # Handle left mouse click events.
        if inputs.mouse.clicked[0]:  # Left click
            # No current action and selected tile contains the unit and the unit is alive.
            if self.current_action is None:
                if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
                    self.current_action = "choosing_action"
            # Choosing a tile to move to.
            elif self.current_action == "choosing_move_target":
                touching = False
                for tile in self.grid.highlighted_tiles:
                    if tile.rect.collidepoint(inputs.mouse.pos):
                        touching = True
                        self.last_action = "move_to_target"
                        self.last_action_target = tile
                        #self.action_finished(self)
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
                            self.last_action = "fire_to_target"
                            self.last_action_target = tile
                            #self.action_finished(self)
                            self.fire(tile)
                            self.current_action = "fire_to_target"                               
                if not touching:
                    self.current_action = None

            elif self.current_action == "choosing_action":
                if self.hover_menu and not self.is_disabled:
                    for index, action in enumerate(self.actions):
                        if self.action_rects[index+1].collidepoint(inputs.mouse.pos):
                            if action == "Move To":
                                self.current_action = "choosing_move_target"
                            elif action == "Fire":
                                if self.can_attack:
                                    self.current_action = "choosing_fire_target"
                            elif action == "Build":
                                pass

                else:
                    self.current_action = None     

        elif inputs.mouse.clicked[2]:  
                self.current_action = None     

        elif inputs.keyboard.clicked[pygame.K_ESCAPE]:
                self.current_action = None

        all_reached_target = True
        finished_shooting = False
        for bullet in self.bullets:
            bullet.update()
            if not bullet.target_reached:
                all_reached_target = False

        if all_reached_target and self.current_action == "fire_to_target" and self.bullets_fired == self.NUM_BULLETS:
            finished_shooting = True
        point_x = self.target_tile.x*TILE_SIZE + self.offset[0]
        point_y = self.target_tile.y*TILE_SIZE + self.offset[1]
        current_time = pygame.time.get_ticks()
        if self.current_action == "fire_to_target" and not finished_shooting and self.bullets_fired < self.NUM_BULLETS and current_time - self.last_fired > self.FIRING_RATE:
            shoot_position = self.screen_x, self.screen_y
            angle = math.atan2((self.target_tile.y*TILE_SIZE) - shoot_position[1] , (self.target_tile.x*TILE_SIZE) - shoot_position[0]) * 180 / math.pi

            self.bullets.append(Bullet(shoot_position[0],shoot_position[1],angle, self.screen ,self.BULLET_SPEED, self.target_tile, self.base_folder, damage=self.attack_damage / self.NUM_BULLETS))
            self.bullets_fired += 1
            self.last_fired = current_time


        self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
        self_selected = False
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
            self_selected = True            
            if self.current_action == "choosing_fire_target":
                self.target_point = (inputs.mouse.pos[0], inputs.mouse.pos[1])
                self.angle = math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            elif self.current_action == "fire_to_target" or self.current_action == "move_to_target":
                self.target_point = (point_x, point_y)
                self.angle = math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            else:
                self.angle = 0                
        else:
            self.angle = 0

        for animation in self.animations.values():
            animation.update()        
        

        if self.current_action == "move_to_target":
            self.target_point = (point_x, point_y)
            self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
            self.distance_to_target = math.sqrt((self.target_point[0] - self.origin_point[0])**2 + (self.target_point[1] - self.origin_point[1])**2)
            self.current_animation == "Walk"
            self.screen_x += self.velocity_x
            self.screen_y += self.velocity_y
            
            if self.distance_to_target < self.MOVE_SPEED:

                self.screen_x = self.target_x
                self.screen_y = self.target_y
                self.animations["Walk"].stop()
                self.current_animation = "Idle"
                self.current_action = None
        
        self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
        self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]   
                    
        if finished_shooting and self.current_action == "fire_to_target":
            self.current_action = None
            self.current_animation = "Idle"


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
        self.screen.blit(background_surface, (self.screen_x + padding, self.screen_y + padding))

        # Blit the text over the semi-transparent rectangle
        self.screen.blit(number_surface, (self.screen_x + padding, self.screen_y + padding))

    def process_events(self, event):
        pass

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        self.is_alive = False
        self.death_sound.play()
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
