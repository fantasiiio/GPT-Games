from Bullet import Bullet
from Animation import Animation
from Unit import Unit
import math
from config import screen, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, MAX_SQUARES_PER_ROW, SQUARE_SPACING, SQUARE_SIZE, BACKGROUND_COLOR, POINTS_COLOR, HEALTH_COLOR, STATUS_BAR_HEIGHT, STATUS_BAR_WIDTH
import pygame


class BTRTower:
    def __init__(self, base_folder, screen, parent):
        self.parent = parent
        self.screen = screen
        self.animations = {}
        self.current_animation = "Idle"
        self.offset = (0,0)
        self.x = 0
        self.y = 0
        self.parent_angle = 0
        self.angle = 0
        self.animations["Idle"] = Animation(self.screen,base_folder,"BTR_tower_", "Idle", 0, self.offset, 90)
        self.animations["Fire"] = Animation(self.screen,base_folder,"BTR_tower_", "Fire", 5, (0,0), 90)
        self.animations["Shot"] = Animation(self.screen,base_folder,"BTR_tower_", "Shot", 10, self.offset, 90)
        self.animations["Broken"] = Animation(self.screen,base_folder,"BTR_tower_", "Broken", 0, self.offset, 90)
        self.animations["Fire"].play()
        self.rotated_image_rect = self.animations[self.current_animation].get_current_rect()

    def get_shoot_positions(self, rect, orientation, distance=10, offset=5):
        if orientation == 'horizontal':
            midpoint_y = rect.top + rect.height // 2
            left_light = (rect.left - offset, midpoint_y - distance // 2)
            right_light = (rect.left - offset, midpoint_y + distance // 2)
            return left_light, right_light
        else:  # vertical orientation
            midpoint_x = rect.left + rect.width // 2
            top_light = (midpoint_x - distance // 2, rect.top - offset)
            bottom_light = (midpoint_x + distance // 2, rect.top - offset)
            return top_light, bottom_light


    def draw(self):
        center = self.animations[self.current_animation].get_current_rect().center
        lst = list(center)
        # Modify the list
        lst[1] -= 10
        # Convert list back to tuple
        center = tuple(lst)

        rotated_image, self.rotated_image_rect = self.animations[self.current_animation].draw(self.x, self.y, -self.angle + self.parent_angle, center)
        pygame.draw.rect(self.screen, (0, 0, 255), self.rotated_image_rect, 2)      
        if self.current_animation == "Fire":
            self.animations["Fire"].draw(self.x, self.y, -self.angle, (46,-10))

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
    
    def get_shoot_positions(self, rotated_corners, distance_from_center=20):

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
        
        # Calculate the positions for the lights
        light1_position = (center_x - dx * distance_from_center, center_y - dy * distance_from_center)
        light2_position = (center_x + dx * distance_from_center, center_y + dy * distance_from_center)
        
        return light1_position, light2_position
    

    def update(self, parent_pos, parent_angle, mouse_pos):
        rect = self.animations[self.current_animation].get_current_rect().copy()
        rect.x = parent_pos[0] - self.parent.offset[0]
        rect.y = parent_pos[1] - self.parent.offset[1]
        rotated_corners  = self.rotate_rect(rect, self.angle + parent_angle + 90)
        #pygame.draw.polygon(self.screen, (0, 0, 255), rotated_corners)
        self.shoot_positions = self.get_shoot_positions(rotated_corners, 5)

        self.x = parent_pos[0] + self.offset[0]
        self.y = parent_pos[1] + self.offset[1]
        self.parent_angle = parent_angle

        for animation in self.animations.values():
            animation.update(self.x, self.y) 
        if self.current_animation == "Fire":
            finished = self.animations["Fire"].is_finished() and self.animations["Shot"].is_finished()
            if finished:
                self.animations["Shot"].reset()
                self.animations["Fire"].reset()
                self.current_animation = "Idle"



class BTR(Unit):
    def __init__(self, target_tile, player, grid, unit_type='BTR', action_points=30, base_folder='assets\\images\\BTR', screen=None, gun_sound_file=None):
        super().__init__(target_tile, player, grid, unit_type, action_points, base_folder, screen, gun_sound_file)
        self.grid = grid
        self.max_move = 10
        self.fire_range = 10
        self.actions = ["Move To", "Fire"]
        self.tower = BTRTower(base_folder, screen, self)
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
        self.dx = 0
        self.dy = 0
        self.FIRING_RATE = 100  # 100ms
        self.NUM_BULLETS = 5
        self.BULLET_SPEED = 15
        self.last_fired = pygame.time.get_ticks()  # Time when the last bullet was fired
        self.bullets_fired = 0  # Number of bullets fired
        self.target_tile = target_tile
        self.canon_number = 0

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



    
    def take_damage(self, damage):
        pass

    def load_animations(self, base_folder):
        self.animations["Idle"] = Animation(self.screen,base_folder,"BTR_base_", "Idle", -1, self.offset, 90)
        self.animations["Move"] = Animation(self.screen,base_folder,"BTR_base_", "Move", -1, self.offset, 90)
        self.animations["Broken"] = Animation(self.screen,base_folder,"BTR_base_", "Broken", 0, self.offset, 90)

    
    def calc_screen_pos(self,tile_x, tile_y):
        screen_x = tile_x * TILE_SIZE
        screen_y = tile_y * TILE_SIZE
        return screen_x, screen_y

    
    def draw(self):
        self.animations[self.current_animation].draw(self.x, self.y, -self.angle)
        self.tower.draw()

        #if self.current_animation == "Fire":        

        rect = self.animations[self.current_animation].get_current_rect()

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
        self.draw_points_as_squares(status_bar_x, points_y, self.action_points, self.max_action_points, HEALTH_COLOR, MAX_SQUARES_PER_ROW)  

        if self.current_action == "choosing_move_target":
            self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), min(self.max_move, self.action_points), (100, 00, 00, 128), False)       

        if self.current_action == "choosing_fire_target":
            self.grid.highlight_tiles((self.x // TILE_SIZE, self.y // TILE_SIZE), self.fire_range, (00, 100, 00, 128), True)       


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
        movement_cost = abs(squares_to_target[0]) + abs(squares_to_target[1])
        self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.tile.unit = None
            self.tile = target_tile
            self.tile.unit = self
            self.grid.selected_tile = target_tile
            self.target_tile = target_tile
            self.action_points -= movement_cost
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.current_animation = "Move"
            self.animations[self.current_animation].play()
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

        """Set the target destination for the unit."""

        # Calculate the distance to the target
        target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
        movement_cost = 1
        angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
        if movement_cost <= self.action_points:
            self.bullets_fired = 0
            self.gun_sound.play()
            self.target_tile = target_tile
            self.angle = math.atan2(target_y - self.y, target_x - self.x) * 180 / math.pi
            self.action_points -= movement_cost
            self.tower.animations["Shot"].play()
            self.tower.animations["Fire"].play()
            self.target_x, self.target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.tower.current_animation = "Fire"
            self.distance_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)

            
            #target_x, target_y = self.calc_screen_pos(target_tile.x, target_tile.y) 
            self.bullets.append(Bullet(self.x, self.y,  angle, self.screen ,self.BULLET_SPEED, target_tile, self.base_folder, "Bullet"))

        
    def update(self, mouse_pos):

        """Update the unit's position if it's moving."""
        for animation in self.animations.values():
            animation.update(self.x, self.y)        
        
        self.tower.update((self.x, self.y) , self.angle, mouse_pos)
        angle = math.atan2(self.target_tile.y*TILE_SIZE - self.y, self.target_tile.x*TILE_SIZE - self.x) * 180 / math.pi
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fired > self.FIRING_RATE and self.bullets_fired < self.NUM_BULLETS:
            # rect = self.rotated_image_rect
            shoot_positions = self.tower.shoot_positions
            shoot_position = shoot_positions[self.canon_number]
            self.canon_number += 1
            self.canon_number %= 2
            self.bullets.append(Bullet(shoot_position[0], shoot_position[1],  angle, self.screen ,self.BULLET_SPEED, self.target_tile, self.base_folder, "Bullet"))
            self.bullets_fired += 1
            self.last_fired = current_time

        if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
           self.tower.angle = self.angle + math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x) * 180 / math.pi

        if self.current_action == "move_to_target":
            self.current_animation == "Walk"
            # Update the unit's position
            self.x += self.dx
            self.y += self.dy

            # Check if the unit is close enough to the target to stop
            if abs(self.x - self.target_x) < 1 and abs(self.y - self.target_y) < 1:
                self.x = self.target_x
                self.y = self.target_y
                self.animations[self.current_animation].stop()
                self.current_animation = "Idle"
                self.current_action = None
                

        for bullet in self.bullets:
            bullet.update()
            if bullet.target_reached:
                self.bullets.remove(bullet)
                if bullet.target_tile.unit:
                    bullet.target_tile.unit.take_damage(10)
                    self.current_action = None

        # Draw each action text with appropriate color based on hover state
        font = pygame.font.SysFont(None, 25)
        self.hover_menu = self.action_menu_rect and self.action_menu_rect.collidepoint(mouse_pos)


        
    def process_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click 
                if self.current_action is None:
                    if self.grid.selected_tile and self.grid.selected_tile.unit == self and self.is_alive:
                        self.current_action = "choosing_action"

                elif self.current_action == "choosing_move_target":
                    touching = False
                    for tile in self.grid.highlighted_tiles:
                        if tile.rect.collidepoint(event.pos):
                            touching = True
                            self.move(tile)
                            self.current_action = "move_to_target"  
                    if not touching:
                        self.current_action = None
                elif self.current_action == "choosing_fire_target":
                    touching = False
                    for tile in self.grid.highlighted_tiles:
                        if tile.rect.collidepoint(event.pos):
                            touching = True
                            if tile.unit and tile.unit.player != self.player:
                                self.fire(tile)
                                self.current_action = "fire_to_target"                               
                    if not touching:
                        self.current_action = None

                elif self.current_action == "choosing_action":
                    if self.hover_menu:
                        for index, action in enumerate(self.actions):
                            if self.action_rects[index].collidepoint(event.pos):
                                if action == "Move To":
                                    self.current_action = "choosing_move_target"
                                elif action == "Fire":
                                    self.current_action = "choosing_fire_target"
                                elif action == "Build":
                                    pass

                    else:
                        self.current_action = None     

            elif event.button == 3:  
                self.current_action = None     

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_action = None

        
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.die()

        
    def die(self):
        pass        