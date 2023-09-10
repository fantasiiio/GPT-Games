
import pygame
import pygame_gui
import random
import os
# Constants
GRID_WIDTH = 800
GRID_HEIGHT = 600
PANEL_WIDTH = 70
PANEL_HEIGHT = 400
# Define some constants for displaying the images
IMAGE_SIZE = 64
IMAGES_PER_ROW = PANEL_WIDTH // IMAGE_SIZE
MAX_IMAGES_DISPLAYED = (PANEL_HEIGHT // IMAGE_SIZE) * IMAGES_PER_ROW
# Create a simple 800 by 600 px window that is definitly too small for the big
# surfaces
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

def load_images_from_directory(directory_path):
    """Load all images from the given directory."""
    images = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".png"):  # assuming all images are PNGs
            image_path = os.path.join(directory_path, filename)
            image = pygame.image.load(image_path)
            images.append(image)
    return images

image_ui_elements = []
def add_images_to_panel(images, container):
    """Add images to the UIPanel starting from the given index."""
    
    global image_ui_elements
    
    # First, we should remove any existing UIImage elements to avoid overlap
    for ui_image in image_ui_elements:
        ui_image.kill()
    image_ui_elements.clear()
    
    x, y = 0, 0
    for i, image in enumerate(images):
        image_rect = pygame.Rect(x + (i % IMAGES_PER_ROW) * IMAGE_SIZE, y + (i // IMAGES_PER_ROW) * IMAGE_SIZE, IMAGE_SIZE, IMAGE_SIZE)
        ui_image = pygame_gui.elements.UIImage(relative_rect=image_rect, image_surface=image, manager=manager, container=container)
        image_ui_elements.append(ui_image)

# Load images
image_directory = "C:\\Users\\Ryzen\\Downloads\\tds-modern-pixel-game-kit\\tds-modern-tilesets-environment\\PNG\\Tiles"
images = load_images_from_directory(image_directory)
# Create the UIManager
manager = pygame_gui.UIManager((width, height))
# Create a UIScrollingContainer that fits exactly into the window/screen
# defined above
scroll_space = pygame_gui.elements.UIScrollingContainer(
    relative_rect = pygame.Rect((0,0),(64,height)),
    manager=manager)

scroll_space.set_scrollable_area_dimensions((IMAGE_SIZE,IMAGE_SIZE*len(images)))

add_images_to_panel(images, scroll_space)


clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Make sure to pass all GUI events also to the UIManager
        manager.process_events(event)

    screen.fill((0, 0, 0))
    manager.update(1/60)
    manager.draw_ui(screen)
    
    pygame.display.flip()
