import pygame_gui.elements.ui_vertical_scroll_bar
import os
import pygame
from ClickableUIImage import ClickableUIImage

TILE_SIZE = 64
TILES_X = 14
TILES_Y = 14
GRID_WIDTH = TILE_SIZE * TILES_X
GRID_HEIGHT = TILE_SIZE * TILES_Y
SCREEN_HEIGHT = GRID_HEIGHT

LEFT_PANEL_WIDTH = 340
RIGHT_PANEL_WIDTH = 340

class DirectoryBrowser:
    def __init__(self, manager, position, size):
        self.manager = manager
        self.position = position
        self.size = size
        self.directory_buttons = []
        self.image_thumbnails = []
        self.selected_thumbnail = None
        self.panel = pygame_gui.elements.UIScrollingContainer(
            relative_rect = pygame.Rect((0,0),(LEFT_PANEL_WIDTH,GRID_HEIGHT)),
            manager=manager)

        self.directory_input_box = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((5, 5), (self.panel.rect.width - 25, 30)),
            manager=self.manager,
            container=self.panel
        )      

        # Load the last directory from config.txt (if it exists)
        self.config_file = 'config.txt'
        self.last_directory = ''
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.last_directory = f.readline().strip()
                self.directory_input_box.set_text(self.last_directory)
                self.browse_directory(self.last_directory)          


    def load_image(self, image_path):
        """Generate a thumbnail for the image."""
        try:
            image = pygame.image.load(image_path)
            #image = pygame.transform.scale(image, max_size)
            return image
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return None
        
    def on_image_click(self):
        pass
  
    def browse_directory(self, directory_path=""):
        # Clear previous buttons and thumbnails
        for btn in self.directory_buttons:
            btn.kill()
        self.directory_buttons.clear()
        
        for thumbnail in self.image_thumbnails:
            thumbnail.kill()
        self.image_thumbnails.clear()

        # If no directory is provided, use the root
        if not directory_path:
            directory_path = os.path.abspath(os.sep)

        # Create the parent directory button at the top of the list
        parent_dir = os.path.dirname(directory_path)
        parent_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((5, 40), (self.size[0] - 25, 30)),  # leaving space for textbox and scrollbar
            text="..",
            manager=self.manager,
            container=self.panel
        )
     
        self.directory_buttons.append(parent_button)

        # List directories and files
        try:
            items = sorted(os.listdir(directory_path))
        except PermissionError:
            return  # Skip directories without permissions
        

        y_offset = 75  # Start a bit lower to account for the textbox and parent directory button
        total_height = 0
        max_width = 0
        for item in items:
            item_path = os.path.join(directory_path, item)
            
            # If it's an image, generate a thumbnail and display it
            if item_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                thumbnail = self.load_image(item_path)
                if thumbnail:
                    if thumbnail.get_width() > max_width:
                        max_width = thumbnail.get_width()
                    total_height += thumbnail.get_height() + 10  # Space between thumbnails
                    thumbnail_surface = pygame_gui.elements.UIImage(
                        relative_rect=pygame.Rect((5, y_offset), thumbnail.get_size()),
                        image_surface=thumbnail,
                        manager=self.manager,
                        container=self.panel,
                        # action=self.on_image_click,
                    )
                    self.image_thumbnails.append(thumbnail_surface)
                    y_offset += thumbnail.get_height() + 5  # Space between thumbnails

        self.panel.set_scrollable_area_dimensions((max_width,total_height))
        

    # Make sure to add an attribute `self.image_thumbnails = []` to the __init__ method of EnhancedDirectoryBrowser
    # to store references to the thumbnail surfaces.

    # You'll replace the browse_directory method in EnhancedDirectoryBrowser with this updated version.

    def check_image_click(self, pos):
        for thumbnail in self.image_thumbnails:
            if thumbnail.rect.collidepoint(pos):
                self.selected_thumbnail = thumbnail

    def highlight_selected_thumbnail(self):
        from main import screen
        if self.selected_thumbnail:
            pygame.draw.rect(screen, pygame.Color('red'), self.selected_thumbnail.rect, 5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Left click
            if event.button == 1:
                self.check_image_click(event.pos)

        # if event.type == pygame_gui.UI_BUTTON_PRESSED:
        #     btn = event.ui_element
        #     if self.last_directory:
        #         self.browse_directory(self.last_directory)        

        # if event.type == pygame.USEREVENT:
        #     if event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
        #         if event.ui_element == self.directory_input_box:
        #             path = self.directory_input_box.get_text()
        #             self.browse_directory(path)

    


    def update_button_positions(self):
        # Adjust the y-positions of the directory buttons based on the scrollbar's position
        for btn in self.directory_buttons:
            original_y = btn.relative_rect.y
            btn.set_relative_position((btn.relative_rect.x, original_y - scroll_value))

# We'll integrate this DirectoryBrowser class into the main TileMapEditor class in the next step.
