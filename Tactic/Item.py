import pygame

class Item():
    def __init__(self, screen, grid, name, tile, animation):
        self.animation = animation
        self.animation.play()
        self.screen = screen
        self.name = name
        self.tile = tile
        self.grid = grid
        tile.item = self

    def draw(self):
        screen_pos_x = self.tile.x * self.grid.tile_size + self.grid.get_camera_screen_position()[0]
        screen_pos_y = self.tile.y * self.grid.tile_size + self.grid.get_camera_screen_position()[1]
        self.animation.draw(screen_pos_x, screen_pos_y)

    def update(self):
        self.animation.update()