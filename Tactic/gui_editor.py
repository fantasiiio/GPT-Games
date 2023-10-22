import pygame
from GraphicUI import *
from UIConfigFlat import *
# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SIDEBAR_WIDTH = 150
PROPERTIES_PANEL_HEIGHT = 150

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
UIManager.screen = screen
UIManager.ui_settings = ui_settings_flat
# UI Manager
ui_manager = UIManager()

# Main UI Container for the entire application
editor_container = UIContainer(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
ui_manager.add_container(editor_container)

# 1. Sidebar containing the UI elements (widgets) list.
sidebar = UIContainer(0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
editor_container.add_element(sidebar)

# Adding some UI elements to the sidebar as examples
sidebar.add_element(UIButton(10, 10, 130, 30, "Button"))
sidebar.add_element(UIList(10, 60, 130, 200))
sidebar.add_element(UITextBox(10, 280, 130, 30, "Textbox..."))

# 2. Main Canvas Area
canvas = UIContainer(SIDEBAR_WIDTH, 0, SCREEN_WIDTH - SIDEBAR_WIDTH, SCREEN_HEIGHT - PROPERTIES_PANEL_HEIGHT)
editor_container.add_element(canvas)

# 3. Properties Panel
properties_panel = UIContainer(SIDEBAR_WIDTH, SCREEN_HEIGHT - PROPERTIES_PANEL_HEIGHT, SCREEN_WIDTH - SIDEBAR_WIDTH, PROPERTIES_PANEL_HEIGHT)
editor_container.add_element(properties_panel)
properties_panel.add_element(UITextBox(10, 10, 280, 30, "Properties..."))

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui_manager.handle_event(event)

    # Draw everything
    screen.fill((255, 255, 255))
    ui_manager.draw(screen)

    # Update the display
    pygame.display.flip()

pygame.quit()
