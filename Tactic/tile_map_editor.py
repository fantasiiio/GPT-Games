import pygame
import pygame_gui
from DirectoryBrowser import DirectoryBrowser

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
TILE_SIZE = 64
TILES_X = 14
TILES_Y = 14
GRID_WIDTH = TILE_SIZE * TILES_X
GRID_HEIGHT = TILE_SIZE * TILES_Y
GRID_HEIGHT = GRID_HEIGHT

LEFT_PANEL_WIDTH = 340
RIGHT_PANEL_WIDTH = 340


# Colors
WHITE = (255, 255, 255)
GRAY = (220, 220, 220)

# Create screen and GUI manager
pygame.init()


# Dummy tiles for the demonstration
tiles = [
    pygame.Surface((TILE_SIZE, TILE_SIZE)),
    pygame.Surface((TILE_SIZE, TILE_SIZE))
]
tiles[0].fill((0, 128, 0))  # Green for grass
tiles[1].fill((0, 0, 128))  # Blue for water

# Starting with grass tile
current_tile = 0
screen = pygame.display.set_mode((GRID_WIDTH + RIGHT_PANEL_WIDTH + LEFT_PANEL_WIDTH, GRID_HEIGHT))
pygame.display.set_caption('Tile Map Editor')
manager = pygame_gui.UIManager((GRID_WIDTH + RIGHT_PANEL_WIDTH+ LEFT_PANEL_WIDTH, GRID_HEIGHT))
# 2D list to represent the map
tile_map = [[0 for _ in range(TILES_X)] for _ in range(TILES_Y)]



def handle_tile_placement(pos):
    """Handle placing tiles on the grid."""
    global current_tile
    
    # Check if click is on the grid
    if pos[0] < GRID_WIDTH:
        x, y = pos[0] // TILE_SIZE, pos[1] // TILE_SIZE
        tile_map[x][y] = current_tile
    
    # Check if click is on the tile palette
    elif GRID_WIDTH + 10 <= pos[0] <= GRID_WIDTH + 10 + TILE_SIZE:
        for i in range(len(tiles)):
            if 10 + i * (TILE_SIZE + 10) <= pos[1] <= 10 + i * (TILE_SIZE + 10) + TILE_SIZE:
                current_tile = i

def split_spritesheet(filename, columns, rows):

    # Load the sprite sheet
    spritesheet = pygame.image.load(filename)
    
    # Calculate the dimensions of individual sprites
    sprite_width = spritesheet.get_width() // columns
    sprite_height = spritesheet.get_height() // rows
    
    # Extract individual sprites
    sprites = []
    for y in range(rows):
        for x in range(columns):
            sprite = pygame.Surface((sprite_width, sprite_height))
            sprite.blit(spritesheet, (0, 0), (x * sprite_width, y * sprite_height, sprite_width, sprite_height))
            sprites.append(sprite)
    
    return sprites

def on_sub_tile_click(event):
    # Determine which tile was clicked based on the event's x and y
    clicked_tile = get_clicked_tile(event.x, event.y)
    
    # Set this tile as the active drawing tile
    set_active_tile(clicked_tile)

def display_tile_grid(panel):
    # For each tile in our 5x5 grid
    for x in range(5):
        for y in range(5):
            # Display the tile
            # (In a real-world scenario, you'd reference a spritesheet or individual tile images)
            tile = get_tile_image(x, y) 
            panel.draw_tile(tile, x, y) 


import os
import tkinter as tk
from tkinter import filedialog
from pygame_gui.elements.ui_image import UIImage

# Initialize tkinter (used for the folder dialog)
root = tk.Tk()
root.withdraw()  # Hide the main tkinter window
current_selected_image = None

class TileMapEditor:
    def __init__(self):
        self.screen = pygame.display.set_mode((LEFT_PANEL_WIDTH + GRID_WIDTH + RIGHT_PANEL_WIDTH, GRID_HEIGHT))
        pygame.display.set_caption('Tile Map Editor with Directory Tree Browser')
        self.manager = pygame_gui.UIManager((LEFT_PANEL_WIDTH + GRID_WIDTH + RIGHT_PANEL_WIDTH, GRID_HEIGHT))
        
        # Directory Browser on the left
        self.directory_browser = DirectoryBrowser(self.manager, (0, 0), (LEFT_PANEL_WIDTH, GRID_HEIGHT))
        

    def draw_grid(self):
        """Draw the grid, the tiles, and the side panel."""
        
        # Draw RIGHT panel background
        rect = pygame.draw.rect(screen, GRAY, (GRID_WIDTH + LEFT_PANEL_WIDTH, 0, RIGHT_PANEL_WIDTH, GRID_HEIGHT))
        
        # Draw tiles from the tile map
        for x in range(TILES_X):
            for y in range(TILES_Y):
                screen.blit(tiles[tile_map[x][y]], (x * TILE_SIZE + LEFT_PANEL_WIDTH, y * TILE_SIZE))
        
        # Draw grid lines
        GRID_COLOR = (200, 200, 200)
        for x in range(0, GRID_WIDTH, TILE_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x + LEFT_PANEL_WIDTH, 0), (x + LEFT_PANEL_WIDTH, GRID_HEIGHT))
        for y in range(0, GRID_HEIGHT, TILE_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (LEFT_PANEL_WIDTH, y), (GRID_WIDTH + LEFT_PANEL_WIDTH, y))

        if self.directory_browser.selected_thumbnail:
            pygame.draw.rect(screen, pygame.Color('red'), self.directory_browser.selected_thumbnail.rect, 5)


        #self.directory_browser.highlight_selected_thumbnail()

    def browse_directory(self):
        """Open a directory dialog and display the images in the directory in the UI."""
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Clear previous thumbnails
            self.image_thumbnails = []
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_path = os.path.join(folder_path, file)
                    self.image_thumbnails.append(self.create_thumbnail(image_path))
            self.display_directory_images()

    def create_thumbnail(self, image_path):
        """Load an image and create a thumbnail."""
        image = pygame.image.load(image_path)
        return pygame.transform.scale(image, self.thumbnail_size)

    def display_directory_images(self):
        """Display the images from a directory in the UI."""
        y_offset = 50
        for thumbnail in self.image_thumbnails:
            thumbnail_element = UIImage(
                relative_rect=pygame.Rect((10, y_offset), self.thumbnail_size),
                image_surface=thumbnail,
                manager=self.manager
            )
            y_offset += self.thumbnail_size[1] + 10



    def run(self):
        """Main loop for the tile map editor."""
        running = True
        while running:
            time_delta = pygame.time.Clock().tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type < 32000 and event.type != 4352 and event.type != 770 and event.type != 1024 and event.type != 1025:
                    event =event
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.USEREVENT:
                    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        pass
                self.manager.process_events(event)
                self.directory_browser.handle_event(event)  # Handle DirectoryBrowser events
            self.manager.update(time_delta)
            screen.fill(WHITE)
            self.manager.draw_ui(screen)
            self.draw_grid()
            pygame.display.flip()
        pygame.quit()

# Create and run the tile map editor
editor = TileMapEditor()
editor.run()
# Uncomment the above line to run the tile map editor with image loader functionality.

