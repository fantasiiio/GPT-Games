from collections import deque
from Bullet import Bullet
from Animation import Animation
from Unit import Unit
import math
from config import get_unit_settings, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH
import pygame
import random

class HelicopterBlades():
    def __init__(self, base_folder, screen, parent):
        self.parent = parent
        self.screen = screen
        self.animations = {}
        self.current_animation = "Fast"
        self.offset = (0,0)
        self.x = 0
        self.y = 0
        #self.parent_angle = 0
        self.angle = 0
        self.animations["Idle"] = Animation(self.screen,base_folder,"Helicopter_blades_", "Idle", 0, (0,-10),90)
        self.animations["Slow"] = Animation(self.screen,base_folder,"blades_", "Move_slow", -1, (0,-10),90, frame_duration=50)
        self.animations["Fast"] = Animation(self.screen,base_folder,"blades_", "Move_fast", -1, (0,-10),90, frame_duration=50)
        self.animations["Fast"].play()


    def draw(self):
        center = self.animations["Idle"].get_current_rect().center
        lst = list(center)
        # Modify the list
        lst[1] -= 10
        # Convert list back to tuple
        center = tuple(lst)

        outline_color=None
        outline_thickness=None
        if self.parent.player != self.parent.grid.current_player:
            outline_color = (255,0,0)
            outline_thickness = 2

        if self.current_animation == "Fire":
            self.animations["Shot"].draw(self.x, self.y, -self.angle, (46, 32), outline_color ,outline_thickness)
            self.animations["Fire"].draw(self.x, self.y, -self.angle, (46,-10), outline_color ,outline_thickness)
        else:
            self.animations[self.current_animation].draw(self.x, self.y, -self.angle, center, (0,0), outline_color ,outline_thickness)


    def rotate_rect(self, rect, angle_degrees):
        cx, cy = rect.center  # Center point of the rectangle
        corners = [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]
        
        angle_radians = math.radians(angle_degrees)
        rotated_corners = []

        for x, y in corners:
            # Rotate each corner around the center of the rectangle
            new_x = cx + (x - cx) * math.cos(angle_radians) - (y - cy) * math.sin(angle_radians)
            new_y = cy + (x - cx) * math.sin(angle_radians) + (y - cy) * math.cos(angle_radians)
            rotated_corners.append((new_x, new_y))

        return rotated_corners
    

    def get_shoot_positions(self, rotated_corners, distance_from_center=20, distance_from_axis=20):

        # Top side is defined by the first two points in the rotated_corners
        top_left = rotated_corners[0]
        top_right = rotated_corners[1]
        
        # Calculate the center of the top side
        center_x = (top_left[0] + top_right[0]) / 2
        center_y = (top_left[1] + top_right[1]) / 2
        
        # Determine the direction vector of the top side
        dx = top_right[0] - top_left[0]
        dy = top_right[1] - top_left[1]
        
        # Normalize the direction vector
        length = math.sqrt(dx*dx + dy*dy)
        dx /= length
        dy /= length
        
        # Determine the perpendicular vector to the direction vector
        perp_dx = -dy
        perp_dy = dx
        
        # Calculate the positions for the lights adjusting in both directions
        light1_position = (center_x - dx * distance_from_center + perp_dx * distance_from_axis, 
                        center_y - dy * distance_from_center + perp_dy * distance_from_axis)
        
        light2_position = (center_x + dx * distance_from_center - perp_dx * -distance_from_axis, 
                        center_y + dy * distance_from_center - perp_dy * -distance_from_axis)
        
        return light1_position, light2_position

    

    def update(self, parent_pos, angle):

        rect =self.animations["Idle"].get_current_rect().copy()
        rect.x = parent_pos[0] - self.parent.offset[0]
        rect.y = parent_pos[1] - self.parent.offset[1]

        self.angle = angle

        rotated_corners  = self.rotate_rect(rect, self.angle + 90)
        #pygame.draw.polygon(self.screen, (0, 0, 255), rotated_corners, 2)
        self.shoot_positions = self.get_shoot_positions(rotated_corners, 5, 10)
        # pygame.draw.circle(self.screen, (0,0,0), self.shoot_positions[0], 2)
        # pygame.draw.circle(self.screen, (0,0,0), self.shoot_positions[1], 2)
        self.x = parent_pos[0] + self.offset[0]
        self.y = parent_pos[1] + self.offset[1]
        #self.parent_angle = -parent_angle

        for animation in self.animations.values():
            animation.update(self.x, self.y) 

        # if self.current_animation == "Fire":
        #     finished = self.animations["Fire"].is_finished() and self.animations["Shot"].is_finished()
        #     if finished:
        #         self.animations["Shot"].reset()
        #         self.animations["Fire"].reset()
        #         self.current_animation = "Idle"



class Helicopter(Unit):
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Helicopter', screen=None, gun_sound_file="assets\\sounds\\helicoptergun.wav"):
        super().__init__(target_tile, player, grid, base_folder, screen)
        self.engine_sound = pygame.mixer.Sound("assets\\sounds\\helicopterEngine.wav")
        self.type = "Helicopter"
        self.settings = get_unit_settings(self.type)
        self.gun_sound = pygame.mixer.Sound(gun_sound_file)
        self.FIRING_RATE = self.settings["Firing Rate"]
        self.NUM_BULLETS = self.settings["Num Bullet Per Shot"]
        self.BULLET_SPEED = self.settings["Bullet Speed"]
        self.MOVE_SPEED = self.settings["Speed"]
        self.grid = grid
        self.max_move = self.settings["Max Move Range"]
        self.fire_range = self.settings["Max Attack Range"]
        self.max_action_points = self.settings["Max AP"]
        self.action_points = self.max_action_points  
        self.max_health = self.settings["Max HP"]
        self.health = self.max_health
        self.attack_damage = self.settings["Damage"]
        self.seat_taken = 0
        self.seats = self.settings["Seats"]
        self.seat_left = self.seats
        self.move_cost = self.settings["Move Cost"]
        self.fire_cost = self.settings["Fire Cost"]
        self.actions = {"Move To":self.move_cost, "Fire":self.fire_cost, "Get Out": 1}
        self.tower = HelicopterBlades(base_folder, screen, self)
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.offset = (32,32)
        self.tower.offset = tuple(a + b for a, b in zip(self.tower.offset, self.offset))
        self.tile = None
        self.place_on_tiles(target_tile)
        self.x, self.y = self.calc_screen_pos(target_tile.x, target_tile.y)
        self.load_animations(base_folder)
        self.animations["Idle"].play()
        self.angle = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.last_fired = pygame.time.get_ticks()  # Time when the last bullet was fired
        self.bullets_fired = 0  # Number of bullets fired
        self.target_tile = target_tile
        self.canon_number = 0
        #self.driver = None
        self.passengers = []
        self.target_x = 0
        self.target_y = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.gun_sound_channel = None
        self.angle = 90
        self.tower.angle = self.angle
        # self.tower.animations["Fire"].play() 

    def take_seat(self, unit):
        if self.seat_left == 0:
            return False
        self.passengers.append(unit)
        self.seat_left -= 1
        self.seat_taken += 1

        unit.is_driver = True
        unit.current_action = None
        self.grid.selected_tile = unit.tile

        return True        

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
        for index, (action, value) in enumerate(self.actions.items()):
            action_pos = (self.x, self.y - 30 - index * 30)
            text_surface = font.render(f"{action} ({value})", True, (255, 255, 255))
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
        for index, (action, value) in enumerate(self.actions.items()):
            action_pos = (self.x, self.y - 30 - index * 30)

            # Check if the mouse is hovering over this action
            if self.action_rects[index].collidepoint(mouse_pos):
                text_surface = font.render(f"{action} ({value})", True, (255, 255, 0))  # Hover color
            else:
                text_surface = font.render(f"{action} ({value})", True, (255, 255, 255))  # Default color

            self.screen.blit(text_surface, action_pos)



    
    def take_damage(self, damage):
        pass

    def load_animations(self, base_folder):
        self.animations["Idle"] = Animation(self.screen,base_folder,"Helicopter_base_", "Idle", 0, self.offset, 90)
        self.animations["Idle_shadow"] = Animation(self.screen,base_folder,"Helicopter_shadow_", "Idle", 0, self.offset, 90)
        #self.animations["Broken"] = Animation(self.screen,base_folder,"Helicopter_base_", "Broken", 0, self.offset, 90)

    
    def calc_screen_pos(self,tile_x, tile_y):
        screen_x = tile_x * TILE_SIZE
        screen_y = tile_y * TILE_SIZE
        return screen_x, screen_y

    
    def draw(self):
        if self.player != self.grid.current_player:
            self.animations[self.current_animation].draw(self.x, self.y, -self.angle, None, None, (255,0,0), 2)
        else:
            self.animations[self.current_animation].draw(self.x, self.y, -self.angle, None, None)
        
        self.tower.draw()
        if self.seat_taken == 0:
            self_selected = False
            if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
                self_selected = True
            if self_selected:
                bar_width = (SQUARE_SIZE+SQUARE_SPACING) * self.seats
                self.draw_points_as_squares(self.x + 64 - bar_width, self.y , self.seat_taken, self.seats, (0,200,0), (200,0,0) ,10)                            
            return
        
        rect = self.animations[self.current_animation].get_current_rect()

        for bullet in self.bullets:
            bullet.draw()
        # Assuming soldier_rect is the rectangle of the soldier sprite
        status_bar_x = self.x + rect.left
        status_bar_y = rect.bottom + 32+ 2

        status_bar_x = self.x + rect.left
        status_bar_y = self.y + 32 + 16

        # Draw health status bar
        self.draw_status_bar(status_bar_x, status_bar_y, self.health, self.max_health, HEALTH_COLOR)
        self.draw_status_bar(status_bar_x, status_bar_y + STATUS_BAR_HEIGHT, self.action_points, self.max_action_points, POINTS_COLOR) 

        self.draw_points_left()

        bar_width = (SQUARE_SIZE+SQUARE_SPACING) * self.seats
        self.draw_points_as_squares(self.x + 64 - bar_width, self.y , self.seat_taken, self.seats, (0,200,0), (200,0,0) ,10)

        if self.current_action == "choosing_move_target":
            self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), min(self.max_move, self.action_points / self.move_cost), (00, 100, 00, 50), self.current_action)       

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
        if hasattr(target_tile, 'no_walk'):
            if target_tile.no_walk:
                return        
        
        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        squares_to_target = (target_x - self.x) / TILE_SIZE, (target_y - self.y) / TILE_SIZE
        movement_cost = (abs(squares_to_target[0]) + abs(squares_to_target[1])) * self.settings["Move Cost"]
        if movement_cost <= self.action_points:
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.x + self.offset[0], self.y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.tile.unit = None
            self.tile = target_tile
            self.tile.unit = self
            self.grid.selected_tile = target_tile
            self.target_tile = target_tile
            self.action_points -= movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_animation = "Move"
            self.engine_sound.play(loops=-1)
            self.animations[self.current_animation].play()
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if self.distance_to_target < self.min_distance:
                self.min_distance = self.distance_to_target

            if(self.distance_to_target > self.MOVE_SPEED):
                self.velocity_x = ((self.target_point[0] - self.origin_point[0]) / self.distance_to_target) * self.MOVE_SPEED
                self.velocity_y = ((self.target_point[1] - self.origin_point[1]) / self.distance_to_target) * self.MOVE_SPEED



    def fire(self, target_tile):
        if self.is_alive == False:
            return
        
        if target_tile.unit and target_tile.unit.is_alive == False:
            return

        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        fire_cost = self.fire_cost
        #angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if fire_cost <= self.action_points:
            #self.tower.angle = self.angle
            self.bullets_fired = 0
            self.gun_sound_channel  = self.gun_sound.play()
            self.gun_sound_playing = True

            self.target_tile = target_tile
            self.attack_damage
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.x + self.offset[0], self.y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.action_points -= fire_cost
            self.tower.animations["Shot"].play()
            self.tower.animations["Fire"].play() 
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.tower.current_animation = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)

        

    def update(self, inputs):
        # If there's no driver, just update the tower's position and angle and exit.
        if self.seat_taken == 0:
            self.tower.update((self.x, self.y), self.tower.angle if self.tower.angle else 0) 
            return

        # Check if the mouse is hovering over the action menu.
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
                        self.move(tile)
                        self.current_action = "move_to_target"
                if not touching:
                    self.current_action = None
            # Choosing a target to fire at.
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
            # Choosing an action from the menu.
            elif self.current_action == "choosing_action":
                if self.hover_menu:
                    for index, action in enumerate(self.actions):
                        if self.action_rects[index].collidepoint(inputs.mouse.pos):
                            if action == "Move To":
                                self.current_action = "choosing_move_target"
                            elif action == "Fire":
                                self.current_action = "choosing_fire_target"
                            elif action == "Get Out":
                                self.get_unit_out()
                else:
                    self.current_action = None     

        # Right mouse click cancels the current action.
        elif inputs.mouse.clicked[2]:  
            self.current_action = None     
        # Escape key also cancels the current action.
        elif inputs.keyboard.clicked[pygame.K_ESCAPE]:
                self.current_action = None

        # if self.gun_sound_channel and not self.gun_sound_channel.get_busy():
        #     if self.gun_sound_playing:
        #         self.tower.animations["Shot"].stop()
        #         self.tower.animations["Fire"].stop()  
        #         self.tower.current_animation = "Idle"              
        #     self.gun_sound_playing = False


        # Update animations.
        for animation in self.animations.values():
            animation.update(self.x, self.y)        

        # Update the tower's position and angle.
        current_time = pygame.time.get_ticks()

        # Check if the shooting action is finished.
        finished_shooting = True
        if self.current_action == "fire_to_target":
            finished_shooting = self.bullets_fired == self.NUM_BULLETS

        # Shoot bullets at a specific firing rate.
        point_x = self.target_tile.x*TILE_SIZE
        point_y = self.target_tile.y*TILE_SIZE        
        if not finished_shooting and  current_time - self.last_fired > self.FIRING_RATE:
            shoot_positions = self.tower.shoot_positions
            shoot_position = shoot_positions[self.canon_number]
            self.canon_number += 1
            self.canon_number %= 2
            angle = math.atan2(self.target_tile.y*TILE_SIZE - shoot_position[1] + self.offset[1], self.target_tile.x*TILE_SIZE - shoot_position[0] + self.offset[0]) * 180 / math.pi

            self.bullets.append(Bullet(shoot_position[0], shoot_position[1],  angle, self.screen ,self.BULLET_SPEED, self.target_tile, self.base_folder, damage=self.attack_damage / self.NUM_BULLETS))
            self.bullets_fired += 1
            self.last_fired = current_time


        self.origin_point = (self.x , self.y)
        self_selected = False
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
            self_selected = True
            if self.current_action == "choosing_fire_target":
                self.target_point = (inputs.mouse.pos[0], inputs.mouse.pos[1])
                self.tower.angle = -self.angle + math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            elif self.current_action == "fire_to_target" or self.current_action == "move_to_target":
                self.target_point = (point_x, point_y)
                self.tower.angle = -self.angle + math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            else:
                self.tower.angle = 0                
        else:
            self.tower.angle = 0

        self.tower.update((self.x, self.y), self.tower.angle + self.angle) 
        #self.tower.update(self.origin_point , self.tower.angle)

        # If choosing a fire target, adjust the tower's angle towards the mouse.
        # if inputs.mouse.button[1]:
        #     self.angle = math.atan2(inputs.mouse.pos[1] - self.origin_point[1], inputs.mouse.pos[0] - self.origin_point[0]) * 180 / math.pi

        # If moving to a target, update the unit's position.
        if self.current_action == "move_to_target":
            self.target_point = (point_x + self.offset[0], point_y + self.offset[1])
            self.origin_point = (self.x + self.offset[0], self.y + self.offset[1])
            self.distance_to_target = math.sqrt((self.target_point[0] - self.origin_point[0])**2 + (self.target_point[1] - self.origin_point[1])**2)
            self.current_animation == "Walk"
            self.x += self.velocity_x
            self.y += self.velocity_y
            
            if self.distance_to_target < self.MOVE_SPEED:
                self.x = self.target_x
                self.y = self.target_y
                self.animations[self.current_animation].stop()
                self.engine_sound.stop()
                self.current_animation = "Idle"
                self.current_action = None
        
        # Update bullet positions and check for hits.
        for bullet in self.bullets:
            bullet.update()
            if bullet.target_reached:
                self.bullets.remove(bullet)
                if bullet.target_tile.unit:
                    bullet.target_tile.unit.take_damage(10)
                    
        if finished_shooting and self.current_action == "fire_to_target":            
            self.current_action = None
            self.current_animation = "Idle"

        # if self_selected:
        #     self.draw_points_left()

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

    def find_free_tile(self, start_tile):

        rows, cols = len(self.grid.tiles), len(self.grid.tiles[0])
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
        visited = set()
        queue = deque([start_tile])

        while queue:
            tile = queue.popleft()
            if not tile.unit:
                return tile

            for dx, dy in directions:
                new_x, new_y = tile.x + dx, tile.y + dy
                if 0 <= new_x < rows and 0 <= new_y < cols:
                    neighbor = self.grid.tiles[new_x][new_y]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

        return None  # No free tile found

        
    def process_events(self, event):
        pass
        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

        
    def die(self):
        pass        

    def draw_points_as_squares(self, x, y, current_points, max_points, color1, color2, max_squares_per_row):
        for i in range(max_points):
            row = i // max_squares_per_row
            col = i % max_squares_per_row
            
            square_x = x + col * (SQUARE_SIZE + SQUARE_SPACING)
            square_y = y + row * (SQUARE_SIZE + SQUARE_SPACING)
            
            if i < current_points:
                pygame.draw.rect(self.screen, color1, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))
            else:
                pygame.draw.rect(self.screen, color2, (square_x, square_y, SQUARE_SIZE, SQUARE_SIZE))    