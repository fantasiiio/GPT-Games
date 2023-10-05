from DashedLine import DashedLine
import os
from abc import ABC, abstractmethod
from Animation import Animation
import math
import pygame
from Bullet import Bullet
import pygame.mixer
from config import GameState, get_unit_settings, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH

class Unit:

    
    def __init__(self, target_tile, player, grid, base_folder='assets\\images\\Gunner', screen=None, type=None, action_finished=None, id=None):
        gun_sound_file="assets\\sounds\\machinegun.wav"
        self.id = id
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
            self.screen_x, self.screen_y = self.calc_screen_pos(self.world_pos_x, self.world_pos_y)  
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
        self.planned_actions = []
        self.dahsed_line = None   
        self.is_planning = False
        self.dragging = False             
        self.start_drag_tile = None

    def draw_planned_actions(self):
        font = pygame.font.SysFont(None, 25)
        for index, action in enumerate(self.planned_actions):
            actions_string = f"{index + 1}. {action[0]}\n"   
        text_surface = font.render(actions_string, True, (255, 255, 255))
        screen_pos = self.calc_screen_pos(self.tile.rect.x, self.tile.rect.y)
        text_rect = text_surface.get_rect(topleft=(screen_pos[0], screen_pos[1] - 50))

        # Calculate the encompassing rectangle
        # Inflate the encompassing rectangle for padding
        padding = 10
        text_rect.inflate_ip(padding * 2, padding * 2)

        # Draw the encompassing rectangle
        pygame.draw.rect(self.screen, (50, 50, 50), text_rect)

        self.screen.blit(text_surface, text_rect)

        from_screen_pos = self.calc_screen_pos(self.tile.rect.x + 32, self.tile.rect.y + 32)
        to_scrren_pos = self.calc_screen_pos(action[1].x * TILE_SIZE + 32, action[1].y * TILE_SIZE + 32)
        pygame.draw.circle(self.screen, (255, 255, 255), (to_scrren_pos[0], to_scrren_pos[1]), 5)
        for action in self.planned_actions:
            if action[0] == "Move":
                DashedLine.draw(self.screen, (from_screen_pos[0], from_screen_pos[1]), (to_scrren_pos[0], to_scrren_pos[1]), 20, (0,255,0), 3)
            elif action[0] == "Fire":
                DashedLine.draw(self.screen, (from_screen_pos[0], from_screen_pos[1]), (to_scrren_pos[0], to_scrren_pos[1]), 20, (255,0,0), 3)

    def execute_next_action(self):
        next_action = None if len(self.planned_actions)==0 else self.planned_actions.pop(0)
        if next_action is None:
            return
        if next_action[0] == "Move":
            self.move(next_action[1])
        elif next_action[0] == "Fire":
            self.fire(next_action[1])

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
        self.target_tile = tile
        tile.unit = self
        if self.tile:
            self.tile.unit = None
        self.tile = tile
        self.world_pos_x = tile.x * TILE_SIZE
        self.world_pos_y = tile.y * TILE_SIZE   

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
    

    def calc_screen_pos(self, world_pos_x, world_pos_y):
        screen_x = world_pos_x + self.grid.get_camera_screen_position()[0]
        screen_y = world_pos_y + self.grid.get_camera_screen_position()[1]
        return screen_x, screen_y
        


    def place_unit(self, inputs):
        if self.tile and not self.dragging:
            return

        self.mouse_x, self.mouse_y = inputs.mouse.pos

        tile = self.grid.get_tile_from_coords(self.mouse_x, self.mouse_y)
        self.world_pos_x = tile.x * TILE_SIZE
        self.world_pos_y = tile.y * TILE_SIZE
        self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
        self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]
        grid_x = self.draw_x
        grid_y = self.draw_y
        self.screen_x = self.draw_x
        self.screen_y = self.draw_y


        if hasattr(self, "child"):
            self.child.draw_x = grid_x + self.child.offset[0]    
            self.child.draw_y = grid_y + self.child.offset[1]      
        

        if inputs.mouse.clicked[0] and self.grid.selected_tile and not self.grid.selected_tile.unit: 
            if not self.grid.can_place_unit(self.type, self.grid.selected_tile, 1):
                return
            self.place_on_tiles(self.grid.selected_tile)
            self.action_finished(self)

        if self.dragging:
            tile = self.grid.get_tile_from_coords(self.mouse_x, self.mouse_y)            
            self.grid.highlight_tiles((self.start_drag_tile.x, self.start_drag_tile.y),self.max_move, (00, 100, 00, 50), self.current_action)       

            if inputs.mouse.released[0]:
                if not tile:
                    return

                if not tile.unit or (tile.unit and tile.unit.player == self.player and tile.unit.type != "Soldier" and tile.unit.seat_left > 0):
                    self.planned_actions.append(("Move", tile))
                else:
                    self.planned_actions.append(("Attack", tile))

                self.dragging = False
                self.place_on_tiles(self.tile)

                self.action_finished(self)

    def on_message(self, event, value):
        if event == "game_state_changed":
            self.current_game_state = value
        elif event == "player_changed":
            self.current_player = value


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

    def draw_status_bar(self, x, y, current_value, max_value, color):
        # Calculate width of the filled portion
        fill_width = int(STATUS_BAR_WIDTH * (current_value / max_value))
        
        # Draw the background (depleted section)
        pygame.draw.rect(self.screen, BACKGROUND_COLOR, (x, y, STATUS_BAR_WIDTH, STATUS_BAR_HEIGHT))
        
        # Draw the filled portion
        pygame.draw.rect(self.screen, color, (x, y, fill_width, STATUS_BAR_HEIGHT))

               

    def update(self, inputs):
        use_special_bullet = False
        if self.type == "Helicopter" or self.type == "Tank":
            use_special_bullet = True
        if self.type == "Boat":
            multiple_shoot_positions=False

        if self.current_game_state == GameState.UNIT_PLACEMENT:
            self.place_unit(inputs)
            if self.tile:
                self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
                self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]               

            return
        # Update animations.
        for animation in self.animations.values():
            animation.update()       

        self.explosion_animation.update()

        # If there's no driver, just update the tower's position and angle and exit.
        if self.seat_taken == 0:
            self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
            self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]               
            self.child.update((self.world_pos_x, self.world_pos_y), self.child.angle if self.child.angle else 0) 
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
                    if tile.get_screen_rect().collidepoint(inputs.mouse.pos):
                        touching = True
                        self.planned_actions.append(("move", tile))
                        #self.move(tile)
                        #self.current_action = "move_to_target"
                if not touching:
                    self.current_action = None
            # Choosing a target to fire at.
            elif self.current_action == "choosing_fire_target":
                touching = False
                for tile in self.grid.highlighted_tiles:
                    if tile.get_screen_rect().collidepoint(inputs.mouse.pos):
                        touching = True
                        if tile.unit and tile.unit.player != self.player:
                            self.planned_actions.append(("fire", tile))

                            #self.fire(tile)
                            #self.current_action = "fire_to_target"
                if not touching:
                    self.current_action = None
            # Choosing an action from the menu.
            elif self.current_action == "choosing_action":
                if self.hover_menu and not self.is_disabled:
                    for index, action in enumerate(self.actions):
                        if self.action_rects[index].collidepoint(inputs.mouse.pos):
                            if action == "Move To":
                                self.current_action = "choosing_move_target"
                            elif action == "Fire":
                                if self.seat_taken >= 2 and self.can_attack:
                                    self.current_action = "choosing_fire_target"
                            elif action == "Get Out":
                                self.get_unit_out()
                            elif action == "Take Off":
                                self.take_off()
                            elif action == "Landing":
                                self.land()
                else:
                    self.current_action = None     

        # Right mouse click cancels the current action.
        elif inputs.mouse.clicked[2]:  
            self.current_action = None     
        # Escape key also cancels the current action.
        elif inputs.keyboard.clicked[pygame.K_ESCAPE]:
                self.current_action = None


        # Update the tower's position and angle.
        current_time = pygame.time.get_ticks()


        # Update bullet positions and check for hits.
        all_reached_target = True
        finished_shooting = False
        for bullet in self.bullets:
            bullet.update()
            if not bullet.target_reached:
                all_reached_target = False

        if all_reached_target and self.current_action == "fire_to_target" and self.bullets_fired == self.NUM_BULLETS:
            finished_shooting = True

        # Shoot bullets at a specific firing rate.
        point_x = self.target_tile.x * TILE_SIZE + self.offset[0]
        point_y = self.target_tile.y * TILE_SIZE + self.offset[1]
        current_time = pygame.time.get_ticks()  # Assuming you're using pygame's clock

        if self.current_action == "fire_to_target" and self.bullets_fired < self.NUM_BULLETS and current_time - self.last_fired > self.FIRING_RATE:
            if multiple_positions:
                shoot_positions = self.child.shoot_positions
                shoot_position = shoot_positions[self.canon_number]
                self.canon_number += 1
                self.canon_number %= 2
            else:
                shoot_position = self.child.shoot_position

            shoot_position = shoot_position[0] - self.child.offset[0], shoot_position[1] - self.child.offset[1]
            angle = math.atan2((self.target_tile.y * TILE_SIZE) - shoot_position[1], 
                            (self.target_tile.x * TILE_SIZE) - shoot_position[0]) * 180 / math.pi
            

            bullet_args = {
                'x': shoot_position[0],
                'y': shoot_position[1],
                'angle': angle,
                'screen': self.screen,
                'speed': self.BULLET_SPEED,
                'target_tile': self.target_tile,
                'base_folder': self.base_folder,
                'damage': self.attack_damage / self.NUM_BULLETS
            }
            
            if use_special_bullet:
                bullet_args['image'] = self.bullet_image
                bullet_args['explosion_animation'] = self.bullet_explosion_animation
                bullet_args['explosion_sound'] = self.bullet_explosion_sound

            self.bullets.append(Bullet(**bullet_args))            
            
            self.bullets_fired += 1
            self.last_fired = current_time


        self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
        self_selected = False
        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
            self_selected = True
            if self.current_action == "choosing_fire_target":
                self.target_point = (inputs.mouse.pos[0], inputs.mouse.pos[1])
                self.child.angle = -self.angle + math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            elif self.current_action == "fire_to_target" or self.current_action == "move_to_target":
                self.target_point = (point_x, point_y)
                self.child.angle = -self.angle + math.atan2(self.target_point[1] - self.origin_point[1], self.target_point[0] - self.origin_point[0]) * 180 / math.pi
            else:
                self.child.angle = 0                
        else:
            self.child.angle = 0

        self.child.update((self.screen_x, self.screen_y), self.child.angle + self.angle) 

        # if inputs.mouse.button[1]:
        #     self.angle = math.atan2(inputs.mouse.pos[1] - self.origin_point[1], inputs.mouse.pos[0] - self.origin_point[0]) * 180 / math.pi

        # If moving to a target, update the unit's position.

        if self.current_action == "Taking Off":
            self.start_helicopter()

        if self.current_action == "Landing":
            self.shut_down_helicopter()


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
                #self.animations[self.current_animation].stop()
                self.engine_sound.stop()
                self.current_animation = "Idle"
                self.current_action = None
        
        self.draw_x = self.world_pos_x + self.grid.get_camera_screen_position()[0]
        self.draw_y = self.world_pos_y + self.grid.get_camera_screen_position()[1]    
                    
        if finished_shooting and self.current_action == "fire_to_target":
            self.current_action = None
            self.current_animation = "Idle"
            self.child.current_animation = "Idle"



    def draw(self):
        outline_color=None
        outline_thickness=None
        outline_fade = False
        if self.swapped:
            if self.player == self.current_player:
                outline_color = (0, 255, 0)
            else:
                outline_color = (255, 0, 0)
            outline_thickness = 5
        elif self.player != self.current_player:
            if self.player != 1:
                outline_color = (255, 0, 0)
                outline_thickness = 2
        elif self.is_planning:
            outline_color = (0, 255, 0)
            outline_thickness = 4
            outline_fade = True

        self.animations[self.current_animation].draw(self.draw_x, self.draw_y, -self.angle, None, None, outline_color, outline_thickness, outline_fade)
        
        self.child.draw()

        if self.explosion_animation.is_playing:
            self.explosion_animation.draw(self.draw_x, self.draw_y, 0, None, None)

        if not self.is_alive:
            return
                
        if self.seat_taken == 0:
            self_selected = False
            if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
                self_selected = True
            if self_selected:
                bar_width = (SQUARE_SIZE+SQUARE_SPACING) * self.seats
                self.draw_points_as_squares(self.draw_x + self.grid.tile_size - bar_width, self.draw_y , self.seat_taken, self.seats, (0,200,0), (200,0,0) ,10)                            
        
        rect = self.animations[self.current_animation].get_current_rect()

        for bullet in self.bullets:
            bullet.draw()

        # Assuming soldier_rect is the rectangle of the soldier sprite<
        status_bar_x = self.draw_x + rect.left
        status_bar_y = self.draw_y + 32 + 16

        # Draw health status bar
        self.draw_status_bar(status_bar_x, status_bar_y, self.health, self.max_health, HEALTH_COLOR)
        self.draw_status_bar(status_bar_x, status_bar_y + STATUS_BAR_HEIGHT, self.action_points, self.max_action_points, POINTS_COLOR) 


        bar_width = (SQUARE_SIZE+SQUARE_SPACING) * self.seats
        self.draw_points_as_squares(self.draw_x + self.grid.tile_size - bar_width, self.draw_y , self.seat_taken, self.seats, (0,200,0), (200,0,0) ,10)

        if self.current_action == "choosing_move_target":
            self.grid.highlight_tiles((self.draw_x // TILE_SIZE, self.draw_y // TILE_SIZE),self.max_move, (00, 100, 00, 50), self.current_action)       

        if self.current_action == "choosing_fire_target":
            self.grid.highlight_tiles((self.draw_x // TILE_SIZE, self.draw_y // TILE_SIZE), self.fire_range, (100, 00, 00, 50), self.current_action)       


        if self.current_action == "choosing_action":
            self.draw_actions_menu()        
        



        
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
            self.tile.unit = None
            self.tile = target_tile
            self.tile.unit = self
            self.grid.selected_tile = target_tile
            self.target_tile = target_tile
            self.action_points -= movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            #self.current_animation = "Move"
            self.engine_sound.play(loops=-1)
            self.animations[self.current_animation].play()
            self.distance_to_target = math.sqrt((self.target_x - self.screen_x)**2 + (self.target_y - self.screen_y)**2)
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
        #angle = math.atan2(target_y - self.screen_y, target_x - self.screen_x) * 180 / math.pi
        if fire_cost <= self.action_points:
            #self.child.angle = self.angle
            self.bullets_fired = 0
            self.gun_sound.play()

            self.target_tile = target_tile
            self.target_point = (target_x + self.offset[0], target_y + self.offset[1])
            self.origin_point = (self.screen_x + self.offset[0], self.screen_y + self.offset[1])
            self.angle = math.atan2(self.target_point[1] - self.origin_point[1] ,  self.target_point[0] - self.origin_point[0] ) * 180 / math.pi
            self.action_points -= fire_cost
            #self.child.animations["Shot"].play()
            self.child.animations["Fire"].play() 
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.child.current_animation = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.screen_x)**2 + (self.target_y - self.screen_y)**2)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

        
    def die(self):
        self.is_alive = False
        self.current_animation = "Broken"
        self.child.current_animation = "Broken"
        self.explosion_animation.play()
        self.explosion_sound.play()

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

    def load_animations(self, base_folder):
        pass

    def draw_flag(self):
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

    def draw_dashed_line(self, color, start_pos, end_pos, dash_length, offset=0):
        # Calculate the length and angle of the full line
        delta = end_pos - start_pos
        length = delta.length()
        num_dashes = int(math.floor(length / dash_length))

        # Calculate the direction vector for a single dash
        dash_vec = delta.normalize() * dash_length

        # Calculate the actual number of dashes to be drawn
        num_dashes += 2  # Adding two more for the beginning and the end

        # Initialize the start position with the offset
        cur_pos = start_pos + dash_vec * (offset / dash_length)
        for i in range(num_dashes):
            # Toggle between dash and gap
            if i % 2 == 0:
                next_pos = cur_pos + dash_vec
                pygame.draw.line(self.screen, color, (int(cur_pos.x), int(cur_pos.y)), (int(next_pos.x), int(next_pos.y)))
            cur_pos += dash_vec

    def can_do_actions(self):
        if self.type == "Soldier-Pistol":
            return self.action_points > 0 and self.is_alive
        else:
            return self.action_points > 0 and self.is_alive and self.seat_taken > 0