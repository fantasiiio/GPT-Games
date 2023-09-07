
import pygame
import pytmx
from pytmx.util_pygame import load_pygame

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.unit = None
        self.structure = None
        self.image = None

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
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y, GRAY
        self.pygame = pygame
        self.screen = screen
        self.tiles = None
        self.selected_tile = None
        self.tile_width = 0
        self.load_tmx_map(file_name)

    def load_tmx_map(self, filename):
        tmx_data = load_pygame(filename)
        self.tile_width = tmx_data.tilewidth
        self.tile_height = tmx_data.tileheight          
        self.tiles = [[Tile(x, y) for y in range(tmx_data.height)] for x in range(tmx_data.width)]
        for layer in tmx_data.visible_layers:
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:                  
                    self.tiles[x][y].image = tile
                    self.tiles[x][y].x = x
                    self.tiles[x][y].y = y

    def get_tile_from_coords(self,x, y):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y, GRAY
        tile_x = x // TILE_SIZE
        tile_y = y // TILE_SIZE
        # Return the corresponding tile object (this assumes you have a 2D list of tiles representing your map)
        return self.tiles[tile_x][tile_y]



    def draw_grid(self):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y, GRAY
        """Draw a simple grid on the screen."""
        for x in range(0, TILES_X):
            for y in range(0, TILES_Y):
#                if 
                if self.selected_tile and self.selected_tile.x == x and self.selected_tile.y == y:
                    self.pygame.draw.rect(self.screen, (255, 0, 0), (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
                image = self.tiles[x][y].image
                if self.tiles[x][y].image:
                    screen.blit(image, (x * image.get_width(), y * image.get_height()))

    def get_adjacent_tile(self, unit, direction):
        from main import pygame,screen, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, TILES_X, TILES_Y, GRAY
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
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            return self.tiles[x // TILE_SIZE][y // TILE_SIZE]
        else:
            return None                    