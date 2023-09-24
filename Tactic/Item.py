import pygame

class Item():
    def __init__(self, screen, grid, name, tile, image_file):
        self.image = pygame.image.load(image_file)
        self.screen = screen
        self.name = name
        self.tile = tile
        self.grid = grid
        tile.item = self

    def draw(self):
        self.screen.blit(self.image, (self.tile.x * self.grid.tile_size + self.grid.get_camera_screen_position()[0], self.tile.y * self.grid.tile_size + self.grid.get_camera_screen_position()[1]))