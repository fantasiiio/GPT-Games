import pygame

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FONT_SIZE = 74

# Initialize screen and font
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Colorful Name')
font = pygame.font.Font(None, FONT_SIZE)

# User's name and initial colors
name = "John"
colors = [(255, 255, 255) for _ in name]  # White by default

# Color options
color_options = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
selected_letter_index = 0

# Main loop
clock = pygame.time.Clock()
running = True

picker_width, picker_height = 256, 256
color_picker = pygame.Surface((picker_width, picker_height))

# Fill color picker with blended colors
for x in range(picker_width):
    for y in range(picker_height):
        R = int(x / (picker_width - 1) * 255)
        G = int(y / (picker_height - 1) * 255)
        B = 255 - int((R + G) / 2)
        color_picker.set_at((x, y), (R, G, B))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            x, y = event.pos
            if 50 <= x <= 50 + picker_width and 50 <= y <= 50 + picker_height:
                picked_color = color_picker.get_at((x - 50, y - 50))
                colors[selected_letter_index] = picked_color
            for i, letter in enumerate(name):
                letter_width, letter_height = font.size(letter)
                letter_rect = pygame.Rect(400 + sum(font.size(name[j])[0] for j in range(i)), 300, letter_width, letter_height)
                if letter_rect.collidepoint(x, y):
                    selected_letter_index = i


    # Clear screen
    screen.fill((0, 0, 0))

    # Draw color options
    for i, color in enumerate(color_options):
        pygame.draw.rect(screen, color, (50 + i * 50, 50, 40, 40))

    # Render each letter with its color and draw a box around the selected one
    x_offset = 0  # Initialize x offset for drawing text
    for i, letter in enumerate(name):
        letter_surface = font.render(letter, True, colors[i])
        screen.blit(letter_surface, (400 + x_offset, 300))
        if i == selected_letter_index:
            letter_width, letter_height = letter_surface.get_size()
            pygame.draw.rect(screen, (255, 255, 255), (400 + x_offset, 300, letter_width, letter_height), 2)
        x_offset += letter_surface.get_width()

    screen.blit(color_picker, (50, 50))
    pygame.display.flip()    
    clock.tick(30)

pygame.quit()

