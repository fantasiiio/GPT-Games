import pyperclip  # You'll need to install this package
import pygame
from GraphicUI import UIPanel, UILabel

pygame.init()

# Initialize some constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def create_labels_from_clipboard(panel):
    clipboard_content = pyperclip.paste()  # Get the clipboard content

    y_offset = 10  # Starting y-coordinate inside the panel for the first label

    for line in clipboard_content.split('\n'):
        font_size = 20  # Default font size

        # Check for font size tags and adjust accordingly
        if "[large]" in line and "[/large]" in line:
            font_size = 40
            line = line.replace("[large]", "").replace("[/large]", "")
        elif "[medium]" in line and "[/medium]" in line:
            font_size = 30
            line = line.replace("[medium]", "").replace("[/medium]", "")
        elif "[small]" in line and "[/small]" in line:
            font_size = 20
            line = line.replace("[small]", "").replace("[/small]", "")

        label = UILabel(10, y_offset, line, panel, font_size=font_size)
        panel.add_element(label)

        y_offset += font_size + 10  # Update the y-coordinate for the next label

# Create a UIPanel instance
top_panel = UIPanel(0, 0, SCREEN_WIDTH, 70, border_size=10)

# Create UILabels from clipboard content and add them to the UIPanel
create_labels_from_clipboard(top_panel)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything
    screen.fill((0, 0, 0))  # Fill the screen with black
    top_panel.draw(screen)

    pygame.display.flip()
