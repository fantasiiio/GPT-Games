import pygame
from GraphicUI import *

# Initialize Pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))
UIManager.screen = screen
# UI Manager
ui_manager = UIManager()

# UI Container
ui_container = UIContainer(50, 50, 700, 500)
ui_manager.add_container(ui_container)

# UI Header
ui_header = UIHeader(50, 50, 700, 50, ["Header"])
ui_container.add_element(ui_header)

# UI Text Box
ui_textbox = UITextBox(100, 150, 300, 40, "Type here...")
ui_container.add_element(ui_textbox)

# UI Button
ui_button = UIButton(100, 250, 150, 50, "Click Me!", callback=lambda button: print("Button clicked!"))
ui_container.add_element(ui_button)

# UI List
ui_list = UIList(500, 150, 200, 300)
ui_container.add_element(ui_list)

# UI PopupBase
ui_popup = UIPopupBase(200, 200, "Confirm", screen)
ui_popup.hide()  # The popup starts hidden

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ui_manager.handle_event(event)

    # Draw everything
    screen.fill((200, 200, 200))
    ui_manager.draw(screen)
    ui_popup.draw(screen)

    # Update the display
    pygame.display.flip()

pygame.quit()