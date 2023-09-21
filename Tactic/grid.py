from collections import deque
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
from config import TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.unit = None
        self.structure = None
        self.image = None
        self.no_walk = False
        self.properties = []
        self.rect = pygame.Rect(x * 64, y * 64, 64, 64)
        #self.image = pygame.image.load("path_to_tile_image.png")
        # width = self.image.get_width
        # height = self.image.get_height
        # sub_divisions_x = width / 64
        # sub_divisions_y = height / 64
        # self.sub_tiles = self.split_rectangle(self.image, sub_divisions_x, sub_divisions_y)


    def split_rectangle(rect, x_splits, y_splits):

        if x_splits <= 0 or y_splits <= 0:
            raise ValueError("x_splits and y_splits must be positive integers.")

        # Calculate the width and height of each smaller rectangle
        width = rect.width // x_splits
        height = rect.height // y_splits

        # Generate the smaller rectangles
        rectangles = []
        for j in range(y_splits):
            row = []
            for i in range(x_splits):
                x_pos = rect.x + i * width
                y_pos = rect.y + j * height
                row.append(pygame.Rect(x_pos, y_pos, width, height))
            rectangles.append(row)

        return rectangles


class Grid:
    def __init__(self, pygame, screen, file_name):
        self.offset = (0,0)
        self.current_player = 1
        self.pygame = pygame
        self.screen = screen
        self.tiles = None
        self.selected_tile = None
        self.tile_width = 0
        self.load_tmx_map(file_name)
        self.mouse_over_tile = None
        self.highlighted_tiles = []

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
        self.tile_width = tmx_data.tilewidth
        self.tile_height = tmx_data.tileheight          
        self.tiles_x = tmx_data.width
        self.tiles_y = tmx_data.height
        self.tiles = [[Tile(x, y) for y in range(tmx_data.height)] for x in range(tmx_data.width)]
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
        tile_x = (x-self.offset[0]) // TILE_SIZE
        tile_y = (y-self.offset[1]) // TILE_SIZE
        # Return the corresponding tile object (this assumes you have a 2D list of tiles representing your map)
        return self.tiles[int(tile_x)][int(tile_y)]

    def tiles_in_range_manhattan(self, x, y, r):
        r = int(r)
        max_x = self.tiles_x * TILE_SIZE
        max_y = self.tiles_y * TILE_SIZE
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
            highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            
            highlight_color = (color[0], color[1], color[2], 110)  # Example: more opaque color for tiles with units
            
            # Fill the surface with the determined color
            highlight_surface.fill(highlight_color)
            
            # Draw the tile with the chosen color
            self.screen.blit(highlight_surface, (tile[0] * TILE_SIZE, tile[1] * TILE_SIZE))            
            #self.pygame.draw.rect(self.screen, (255, 0, 0), (tile[0]*TILE_SIZE, tile[1]*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)

            # decide if the text will be dra on top or below the tile
            # start = path[0]
            # action_pos = None
            # if len(path) > 1:
            #     if start[1] - path[1][1] > 0:
            #         action_pos = (start[0]* TILE_SIZE, start[1] * TILE_SIZE + TILE_SIZE)
            #     else:
            #         action_pos = (start[0]* TILE_SIZE, start[1] * TILE_SIZE - TILE_SIZE)

            #if action_pos:
                #font = pygame.font.SysFont(None, 25)
                #action_cost = self.selected_tile.unit.move_cost
                #self.draw_text_with_border(self.screen, f"Cost: {action_cost}", font, action_pos[0], action_pos[1], (255, 255, 255), (0, 0, 0), 2)

    def update(self, inputs):
        selected_tile = self.selected_tile
        x, y = inputs.mouse.pos
        clicked_tile = self.get_tile_from_coords(x, y)
        self.mouse_over_tile = self.get_tile_from_coords(x, y)
        if inputs.mouse.clicked[0]:
            if clicked_tile != selected_tile:
                if selected_tile and selected_tile.unit and selected_tile.unit.current_action is not None:
                    return
                if not (clicked_tile.unit and clicked_tile.unit.current_action != None):
                    self.selected_tile = clicked_tile
            else:
                if not (self.selected_tile and self.selected_tile.unit):
                    self.selected_tile = None  



    def highlight_tiles(self, unit_position, range, color, action):
        self.highlighted_tiles = []
        TILE_SIZE = 64  # assuming each tile is 64x64 pixels

        tiles = self.tiles_in_range_manhattan(unit_position[0], unit_position[1], range)
        for tile_pos in tiles:
            if self.position_is_in_grid(tile_pos[0], tile_pos[1]):  # corrected typo: posision -> position
                tile = self.tiles[int(tile_pos[0])][int(tile_pos[1])]
                if self.is_passable(tile.x, tile.y, action):
                    self.highlighted_tiles.append(tile)
                    
                    # Create a fresh surface for this tile
                    highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                    
                    # Check conditions to determine the color of the tile
                    if tile.unit is not None:
                        highlight_color = (color[0], color[1], color[2], 200)  # Example: more opaque color for tiles with units
                    else:
                        highlight_color = color  # Default color
                    
                    # Fill the surface with the determined color
                    highlight_surface.fill(highlight_color)
                    
                    # Draw the tile with the chosen color
                    self.screen.blit(highlight_surface, (tile.x * TILE_SIZE, tile.y * TILE_SIZE))
       



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
        self.offset = (x, y)
        
    def draw_grid(self, inputs):
        """Draw a simple grid on the screen."""
        for x in range(0, self.tiles_x):
            for y in range(0, self.tiles_y):
                image = self.tiles[x][y].image
                if self.tiles[x][y].image:
                    self.screen.blit(image, (x * image.get_width() + self.offset[0], y * image.get_height() + self.offset[1]))
                
                self.pygame.draw.rect(self.screen, GRAY, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
                if self.mouse_over_tile and self.mouse_over_tile.x == x and self.mouse_over_tile.y == y:
                    self.pygame.draw.rect(self.screen, (255, 255, 255), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
                if self.selected_tile and self.selected_tile.x == x and self.selected_tile.y == y:
                    self.pygame.draw.rect(self.screen, (0, 0, 255), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
        
        selected_tile = self.selected_tile
        x, y = inputs.mouse.pos
        clicked_tile = self.get_tile_from_coords(x, y)        
        if selected_tile and selected_tile.unit and selected_tile.unit.current_action == "choosing_move_target":
            path = self.manhattan_path((selected_tile.x, selected_tile.y), (clicked_tile.x, clicked_tile.y))
            touching = False
            for tile in self.highlighted_tiles:
                if tile.x == path[-1][0] and tile.y == path[-1][1]:
                    touching = True
            if touching:
                self.draw_path(path, (0, 100, 0, 150))                    

    def get_adjacent_tile(self, unit, direction):
        """
        Return the tile adjacent to the given unit in the specified direction.
        """
        x, y = unit.x, unit.y

        if direction == 'up':
            y -= TILE_SIZE
        elif direction == 'down':
            y += TILE_SIZE
        elif direction == 'left':
            x -= TILE_SIZE
        elif direction == 'right':
            x += TILE_SIZE

        # Ensure the coordinates are within the map boundaries
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.tiles[x // TILE_SIZE][y // TILE_SIZE]
        else:
            return None                    

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
                        if 0 <= neighbor_x < len(row) and 0 <= neighbor_y < GRID_WIDTH:
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