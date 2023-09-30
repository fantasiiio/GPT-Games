from collections import deque
import pygame
from pytmx.util_pygame import load_pygame
from config import  GRAY
import random
class Tile:
    def __init__(self, x, y, grid):
        self.grid = grid
        self.x = x
        self.y = y
        self.unit = None
        self.item = None
        self.structure = None
        self.image = None
        self.no_walk = False
        self.properties = {}
        self.rect = pygame.Rect(x * self.grid.tile_size, y * self.grid.tile_size, self.grid.tile_size, self.grid.tile_size)

    def get_screen_rect(self): 
        return pygame.Rect(self.x * self.grid.tile_size + self.grid.get_camera_screen_position()[0], self.y * self.grid.tile_size + self.grid.get_camera_screen_position()[1], self.grid.tile_size, self.grid.tile_size)

class Grid:
    def __init__(self, pygame, screen, file_name):
        self.pygame = pygame
        self.screen = screen
        self.tiles = None
        self.selected_tile = None
        self.tile_size = 0
        self.grid_width = 0
        self.grid_height = 0
        self.load_tmx_map(file_name)
        self.mouse_over_tile = None
        self.highlighted_tiles = []
        self.clicked_position = None
        self.camera_target = None
        self.camera_is_moving = False
        self.camera_start = (0,0)
        self.camera_world_position = (0,0)
        self.camera_move_start_time = 0
        self.camera_direction_vector = (0,0)
        self.current_player = 1

    def get_camera_screen_position(self):
        return (self.camera_world_position[0] + self.screen.get_rect().width/2, self.camera_world_position[1] + self.screen.get_rect().height/2)
    

    def set_camera_world_position(self, x, y):
        # # Calculate the boundaries based on the grid size and tile size
        # min_x = 0 - (self.grid_width - self.screen.get_width()/2)
        # min_y = 0 - (self.grid_height - self.screen.get_height()/2)
        
        # # Screen size (assuming you have these variables)
        # screen_width, screen_height = self.screen.get_size()
        
        # # If the camera view goes out of the grid, we set it to the boundary value
        # if x > -self.screen.get_width()/2:
        #     x = -self.screen.get_width()/2
        # elif x < min_x:
        #     x = min_x

        # if y > -self.screen.get_height()/2:
        #     y = -self.screen.get_height()/2
        # elif y < min_y:
        #     y = min_y
        
        self.camera_world_position = (x, y)


    def set_camera_screen_position(self, x, y):
        self.camera_world_position = (x - self.screen.get_rect().width/2, y - self.screen.get_rect().height/2)
        self.camera_world_position = self.camera_world_position

    def get_tiles_with_property(self, property_name, property_value):
        tiles = []
        for x in range(self.tiles_x):
            for y in range(self.tiles_y):
                tile = self.tiles[x][y]
                if tile.properties and tile.properties.get(property_name):
                    tiles.append(tile)
        return tiles

    def load_tmx_map(self, filename):
        tmx_data = load_pygame(filename)
        self.tile_size = tmx_data.tilewidth
        self.tiles_x = tmx_data.width
        self.tiles_y = tmx_data.height
        self.grid_width = self.tiles_x * self.tile_size
        self.grid_height = self.tiles_y * self.tile_size
        self.tiles = [[Tile(x, y, self) for y in range(tmx_data.height)] for x in range(tmx_data.width)]
        for layer in tmx_data.visible_layers:
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:                  
                    properties = tmx_data.get_tile_properties(x, y, 0)
                    self.tiles[x][y].no_walk = False
                    if properties is not None:
                        no_walk = properties.get('no_walk', "False")
                        if no_walk == "True":
                            self.tiles[x][y].no_walk = True
                            self.tiles[x][y].properties = properties                    
                    self.tiles[x][y].image = tile
                    self.tiles[x][y].x = x
                    self.tiles[x][y].y = y

    def update(self):
        self.highlight_tiles = []

    def get_tile_from_coords(self,x, y):
        tile_x = (x-self.get_camera_screen_position()[0]) // self.tile_size
        tile_y = (y-self.get_camera_screen_position()[1]) // self.tile_size
        if tile_x < 0 or tile_y < 0 or tile_x >= self.tiles_x or tile_y >= self.tiles_y:
            return None
        # Return the corresponding tile object (this assumes you have a 2D list of tiles representing your map)
        return self.tiles[int(tile_x)][int(tile_y)]

    def is_tile_free(self, x, y):
        if self.tiles[x][y].unit:
            return False
        return True

    def get_next_point_within_max_range(start_point, next_straight_point, max_range):
        dx = next_straight_point[0] - start_point[0]
        dy = next_straight_point[1] - start_point[1]
        
        # Calculate the distance to the next straight point
        distance = abs(dx) + abs(dy)
        
        if distance <= max_range:
            # If the next straight point is within max_range, return it
            return next_straight_point
        
        # If the next straight point is outside max_range, find a point within max_range along the line to the next_straight_point
        if dx == 0:
            # Vertical movement
            next_point = (start_point[0], start_point[1] + max_range if dy > 0 else start_point[1] - max_range)
        elif dy == 0:
            # Horizontal movement
            next_point = (start_point[0] + max_range if dx > 0 else start_point[0] - max_range, start_point[1])
        else:
            # Diagonal movement: For simplicity, we could move vertically or horizontally until we reach max_range
            next_point = (start_point[0] + max_range if dx > 0 else start_point[0] - max_range, start_point[1]) if abs(dx) > abs(dy) else (start_point[0], start_point[1] + max_range if dy > 0 else start_point[1] - max_range)
        
        return next_point

    def get_manathan_range(self, start_x, start_y, end_x, end_y):
        return abs(start_x - end_x) + abs(start_y - end_y)
    def tiles_in_range_manhattan(self, x, y, r):
        r = int(r)
        max_x = self.tiles_x
        max_y = self.tiles_y
        tiles = []
        for i in range(-r, r + 1):
            for j in range(-r + abs(i), r - abs(i) + 1):
                new_x, new_y = x + i, y + j
                if 0 <= new_x < max_x and 0 <= new_y < max_y:
                    tiles.append((new_x, new_y))
        return tiles

    def position_is_in_grid(self, x, y):
        if x < 0 or y < 0:
            return False
        if x >= self.tiles_x or y >= self.tiles_y:
            return False
        return True

    def manhattan_path(self, start, end):
        x1, y1 = start
        x2, y2 = end
        path = []

        # Move in the x direction
        while x1 < x2:
            path.append((x1, y1))
            x1 += 1
        while x1 > x2:
            path.append((x1, y1))
            x1 -= 1

        # Move in the y direction
        while y1 < y2:
            path.append((x1, y1))
            y1 += 1
        while y1 > y2:
            path.append((x1, y1))
            y1 -= 1

        # Add the end point
        path.append(end)

        return path

    def draw_text_with_border(self, screen, text, font, x, y, text_color, border_color, border_thickness=1):
        # Render and draw the border
        for offset_x in range(-border_thickness, border_thickness + 1):
            for offset_y in range(-border_thickness, border_thickness + 1):
                border_text = font.render(text, True, border_color)
                screen.blit(border_text, (x + offset_x, y + offset_y))
        
        # Render and draw the main text
        main_text = font.render(text, True, text_color)
        screen.blit(main_text, (x, y))

    def draw_path(self, path, color):
        if not self.selected_tile.unit:
            return        
        
        for index, tile in enumerate(path):
            if self.selected_tile.unit.current_action == "choosing_move_target":
                if index > self.selected_tile.unit.max_move+1:
                    return
            elif self.selected_tile.unit.current_action == "choosing_fire_target":
                if index > self.selected_tile.unit.fire_range+1:
                    return
            
            if index == 0:
                continue
            # Create a fresh surface for this tile
            highlight_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            
            highlight_color = (color[0], color[1], color[2], 110)  # Example: more opaque color for tiles with units
            
            # Fill the surface with the determined color
            highlight_surface.fill(highlight_color)
            
            # Draw the tile with the chosen color
            self.screen.blit(highlight_surface, (tile[0] * self.tile_size + self.get_camera_screen_position()  [0], tile[1] * self.tile_size + self.get_camera_screen_position()  [1]))            
            #self.pygame.draw.rect(self.screen, (255, 0, 0), (tile[0]*self.tile_width, tile[1]*self.tile_width, self.tile_width, self.tile_width), 2)

            # decide if the text will be dra on top or below the tile
            # start = path[0]
            # action_pos = None
            # if len(path) > 1:
            #     if start[1] - path[1][1] > 0:
            #         action_pos = (start[0]* self.tile_width, start[1] * self.tile_width + self.tile_width)
            #     else:
            #         action_pos = (start[0]* self.tile_width, start[1] * self.tile_width - self.tile_width)

            #if action_pos:
                #font = pygame.font.SysFont(None, 25)
                #action_cost = self.selected_tile.unit.move_cost
                #self.draw_text_with_border(self.screen, f"Cost: {action_cost}", font, action_pos[0], action_pos[1], (255, 255, 255), (0, 0, 0), 2)

    def update(self, inputs):
        selected_tile = self.selected_tile
        x, y = inputs.mouse.pos
        self.mouse_over_tile = self.get_tile_from_coords(x, y)
        if inputs.mouse.clicked[0]:
            if self.mouse_over_tile != selected_tile:
                if selected_tile and selected_tile.unit and selected_tile.unit.current_action is not None:
                    return
                if not (self.mouse_over_tile.unit and self.mouse_over_tile.unit.current_action != None):
                    self.selected_tile = self.mouse_over_tile
            else:
                if not (self.selected_tile and self.selected_tile.unit):
                    self.selected_tile = None  
        if inputs.mouse.clicked[1]:
            self.clicked_position = inputs.mouse.pos
            self.camera_start = self.camera_world_position
            self.camera_start = self.camera_start
        elif inputs.mouse.button[1]:
            if self.clicked_position:
                x, y = inputs.mouse.pos
                offset = (x - self.clicked_position[0], y - self.clicked_position[1])
                self.set_camera_world_position(self.camera_start[0] + offset[0], self.camera_start[1] + offset[1])



    def highlight_tiles(self, unit_position, range, color, action):
        self.highlighted_tiles = []

        tiles = self.tiles_in_range_manhattan(unit_position[0], unit_position[1], range)
        for tile_pos in tiles:
            if self.position_is_in_grid(tile_pos[0], tile_pos[1]):  # corrected typo: posision -> position
                tile = self.tiles[int(tile_pos[0])][int(tile_pos[1])]
                if self.is_passable(tile.x, tile.y, action):
                    self.highlighted_tiles.append(tile)
                    
                    # Create a fresh surface for this tile
                    highlight_surface = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    
                    # Check conditions to determine the color of the tile
                    if tile.unit is not None:
                        highlight_color = (color[0], color[1], color[2], 200)  # Example: more opaque color for tiles with units
                    else:
                        highlight_color = color  # Default color
                    
                    # Fill the surface with the determined color
                    highlight_surface.fill(highlight_color)
                    
                    # Draw the tile with the chosen color
                    self.screen.blit(highlight_surface, (tile.x * self.tile_size + self.get_camera_screen_position()[0], tile.y * self.tile_size + self.get_camera_screen_position()[1]))
       


    def can_place_unit(self, unit_type, tile, player):
        # Check if a unit is already present on the tile
        if tile.unit:
            return False
        
        # Check for terrain compatibility
        if tile.properties:
            terrain_type = tile.properties.get("type")
            if terrain_type == "water" and unit_type != "Boat":
                return False
            if terrain_type == "grass" and unit_type == "Boat":
                return False
        
        # Check if the player is allowed to place a unit on this part of the map
        middle_x = self.tiles_x // 2
        if player == 1 and tile.x >= middle_x:
            return False
        if player == 2 and tile.x < middle_x:
            return False

        return True

    def is_passable(self, x, y, action):

        tile = self.tiles[x][y]

        # Check for other units
        if tile == self.selected_tile:
            return False

        if action == "choosing_move_target" and tile.unit is not None:
            if tile.unit and self.selected_tile.unit and tile.unit.player == self.selected_tile.unit.player:
                if (tile.unit.type == "Tank" and tile.unit.seat_left >  0) or (tile.unit.type == "Boat" and tile.unit.seat_left >  0) or (tile.unit.type == "Helicopter" and tile.unit.seat_left >  0):
                    if tile.unit.is_alive:
                        return True
            return False
        
        if action == "choosing_move_target" and self.selected_tile.unit and self.selected_tile.unit.type == "Boat":
            if not tile.properties or not tile.properties["type"] == "water":
                return False

        if action == "choosing_fire_target" and self.selected_tile.unit and tile.unit is not None and tile.unit.player == self.selected_tile.unit.player:
            return False

        if action == "choosing_fire_target" and self.selected_tile.unit and tile.unit is not None and not tile.unit.is_alive:
            return False


        # if action == "choosing_fire_target" and tile.unit is not None and tile.unit.type == "Tank" and tile.unit.driver:
        #     return False

        # Check for structures
        if tile.structure is not None:
            return False

        # Check for impassable terrain
        if action == "choosing_move_target" and (not self.selected_tile.unit or self.selected_tile.unit.type != "Boat"):
            if tile.no_walk:
                return False


        return True

    def move(self, x, y):
        self.set_camera_world_position(x, y)
        
    def ease_in_out_cubic(self, t):
        if t < 0.5:
            return 4 * t ** 3
        return 1 - pow(-2 * t + 2, 3) / 2

    def ease_in_out_cubic2(self, t, b, c, d):
        t /= d / 2
        if t < 1:
            return c / 2 * t * t * t + b
        t -= 2
        return c / 2 * (t * t * t + 2) + b

    def magnitude(self, vector):
        return (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    def update_camera(self):
        if not self.camera_is_moving:
            return self.camera_world_position 

        move_duration = 2000
        current_time = self.pygame.time.get_ticks()
        delta_time = current_time - self.camera_move_start_time

        if delta_time >= move_duration:
            delta_time = move_duration
            self.camera_is_moving = False

        # Get the eased_t value
        eased_t = self.ease_in_out_cubic2(delta_time,0, 1,  move_duration)

        dx_scaled = self.camera_direction_vector[0] * eased_t
        dy_scaled = self.camera_direction_vector[1] * eased_t

        # Update camera position
        new_x = self.camera_start[0] - dx_scaled
        new_y = self.camera_start[1] - dy_scaled

        self.set_camera_screen_position(new_x, new_y)
        return (new_x, new_y)

    def move_camera_to(self, target):
        self.camera_is_moving = True
        self.camera_start = self.get_camera_screen_position() 
        self.camera_target = target
        self.camera_move_start_time = self.pygame.time.get_ticks()
        self.camera_direction_vector = (target[0] + self.camera_start[0], target[1] + self.camera_start[1])
        #self.set_camera_world_position(self.camera_start[0], self.camera_start[1])

    def move_camera_to_tile(self, tile):
        self.move_camera_to((tile.x * self.tile_size + self.get_camera_screen_position()[0], tile.y * self.tile_size + self.get_camera_screen_position()[1]))

    def draw_grid(self, inputs):
        """Draw a simple grid on the screen."""
        camera_pos = self.get_camera_screen_position()
        cam_x, cam_y = camera_pos[0], camera_pos[1]
        screen_width, screen_height = self.screen.get_size()
        
        min_x = int(max(0, -cam_x // self.tile_size))
        min_y = int(max(0, -cam_y // self.tile_size))
        max_x = int(min(self.tiles_x, (-cam_x + screen_width) // self.tile_size + 1))
        max_y = int(min(self.tiles_y, (-cam_y + screen_height) // self.tile_size + 1))

        selected_tile = self.selected_tile
        selected_tile_coords = (selected_tile.x, selected_tile.y) if selected_tile else None

        for x in range(min_x, max_x):
            for y in range(min_y, max_y):
                tile = self.tiles[x][y]
                image = tile.image
                tile_pos_x = x * self.tile_size + cam_x
                tile_pos_y = y * self.tile_size + cam_y
                
                if image:
                    self.screen.blit(image, (tile_pos_x, tile_pos_y))

                self.pygame.draw.rect(self.screen, GRAY, (tile_pos_x, tile_pos_y, self.tile_size, self.tile_size), 1)

                if self.mouse_over_tile and (self.mouse_over_tile.x, self.mouse_over_tile.y) == (x, y):
                    self.pygame.draw.rect(self.screen, (255, 255, 255), (tile_pos_x, tile_pos_y, self.tile_size, self.tile_size), 2)
                
                if selected_tile_coords and selected_tile_coords == (x, y):
                    self.pygame.draw.rect(self.screen, (0, 0, 255), (tile_pos_x, tile_pos_y, self.tile_size, self.tile_size), 2)

        if selected_tile and selected_tile.unit and selected_tile.unit.current_action == "choosing_move_target":
            x, y = inputs.mouse.pos
            clicked_tile = self.get_tile_from_coords(x, y)
            path = self.manhattan_path((selected_tile.x, selected_tile.y), (clicked_tile.x, clicked_tile.y))
            
            touching = False
            for tile in self.highlighted_tiles:
                if tile.x == path[-1][0] and tile.y == path[-1][1]:
                    touching = True
                    
            if touching:
                self.draw_path(path, (0, 100, 0, 150))


        # Darken the area where the current player cannot place units
        middle_x = self.tiles_x // 2
        if self.current_player == 1:
            start_x = middle_x * self.tile_size + self.get_camera_screen_position()[0]
            width = self.grid_width - start_x
        elif self.current_player == 2:
            start_x = self.get_camera_screen_position()[0]
            width = middle_x * self.tile_size

        height = self.grid_height

        darken_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        darken_surface.fill((0, 0, 0, 128))  # RGBA
        self.screen.blit(darken_surface, (start_x, 0))

                   

    def get_adjacent_tile(self, unit, direction):
        """
        Return the tile adjacent to the given unit in the specified direction.
        """
        x, y = unit.x, unit.y

        if direction == 'up':
            y -= self.tile_size
        elif direction == 'down':
            y += self.tile_size
        elif direction == 'left':
            x -= self.tile_size
        elif direction == 'right':
            x += self.tile_size

        # Ensure the coordinates are within the map boundaries
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.tiles[x // self.tile_size][y // self.tile_size]
        else:
            return None                    

    def get_random_tile(self, water = False):
        water_tiles = []
        non_water_tiles = []
        for x in range(self.tiles_x):
            for y in range(self.tiles_y):
                tile = self.tiles[x][y]
                if tile.unit:
                    continue
                if tile.properties:
                    type = tile.properties.get("type")
                    if type == "water":
                        water_tiles.append(tile)
                    else:
                        non_water_tiles.append(tile)     
                else:
                    non_water_tiles.append(tile)     

        if water:
            if water_tiles:
                return random.choice(water_tiles)
            else:
                return None
            
        elif non_water_tiles:  # Make sure the list is not empty
            return random.choice(non_water_tiles)
        else:
            return None  # Return None if there are no non-water tiles

    def find_path(self, start, end):
        rows, cols = len(self.tiles), len(self.tiles[0])
        
        # Helper function to check if a given cell is within self.tiles boundaries and is accessible
        def is_valid(x, y, visited):
             return 0 <= x < rows and 0 <= y < cols and (x, y) not in visited
        
        if start is None or end is None:
            return []
        
        visited = set()  # Set to keep track of visited cells
        queue = deque([(start, [start])])  # Queue for BFS. Each element is a tuple containing current cell coordinates and the path taken to reach there.
        
        while queue:
            (cur_x, cur_y), path = queue.popleft()
            
            # If we've reached the end, return the path
            if (cur_x, cur_y) == end:
                return path
            
            # Mark the current cell as visited
            visited.add((cur_x, cur_y))
            
            # Visit all valid neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x, new_y = cur_x + dx, cur_y + dy
                
                if is_valid(new_x, new_y, visited):
                    queue.append(((new_x, new_y), path + [(new_x, new_y)]))
                    visited.add((new_x, new_y))
                    
        return []


    def get_farthest_walkable_point(self, path, max_range):
        if not path or len(path) < 2:
            return None

        start = path[0]
        furthest_point = start  # Initialize to the start point
        distance_covered = 0

        rows, cols = len(self.tiles), len(self.tiles[0])

        for idx, point in enumerate(path[1:]):
            dx, dy = point[0] - start[0], point[1] - start[1]
            norm_dx = dx // abs(dx) if dx != 0 else 0
            norm_dy = dy // abs(dy) if dy != 0 else 0

            x, y = start
            obstructed = False

            # Initialize last_valid_point to start, will update this as we move along
            last_valid_point = start

            # Check all tiles along the line from start to this point to see if they are walkable
            while (x, y) != point:
                x += norm_dx
                y += norm_dy

                if x < 0 or y < 0 or x >= rows or y >= cols:
                    obstructed = True
                    furthest_point = last_valid_point
                    break

                    tile = self.tiles[y][x]
                    if tile.properties is not None:
                        no_walk = tile.properties.get('no_walk', "False")
                        if no_walk == "True":
                            obstructed = True
                            furthest_point = last_valid_point
                            break

                # Update last_valid_point as we've found a new valid point
                last_valid_point = (x, y)
            
            if obstructed:
                break  # Path is obstructed, so we stop

            # If we are here, this point is walkable. Update furthest_point.
            furthest_point = point  
            distance_covered += 1  # Update the distance covered

            # Check if max_range has been reached
            if distance_covered >= max_range:
                break

        return furthest_point  # Return the furthest point found that is walkable and within max_range


    def draw_selected_perimeter(self):
        line_width = 5
        #transformed_shape = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
        
        # Draw perimeter line for the transformed shape
        for i, row in enumerate(self.tiles):
            for j, cell in enumerate(row):
                if cell:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        neighbor_x, neighbor_y = j + dx, i + dy
                        
                        # Check if the neighboring cell is outside the piece
                        if 0 <= neighbor_x < len(row) and 0 <= neighbor_y < self. grid_width:
                            if self.tiles[neighbor_y][neighbor_x].unit is not None:
                                is_empty_inside = False
                            is_empty_inside = self.tiles[neighbor_y][neighbor_x] == 0
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