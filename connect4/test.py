import pygame
import pygame_gui
import sys

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PANEL_WIDTH = 200

# Create screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pygame GUI Panel Example')
clock = pygame.time.Clock()

# Initialize pygame_gui manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))

# Create list box
list_data = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
list_box_rect = pygame.Rect(WIDTH - PANEL_WIDTH + 10, 10, PANEL_WIDTH - 20, HEIGHT - 20)
list_box = pygame_gui.elements.UISelectionList(relative_rect=list_box_rect,
                                               manager=manager,
                                               item_list=list_data)

# Main loop
while True:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        #manager.process_events(event)

    # Update UI
    #manager.update(0)

    # Draw everything
    screen.fill((255, 255, 255))
    pygame.draw.rect(screen, (200, 200, 200), (WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT))

    manager.draw_ui(screen)

    pygame.display.update()
