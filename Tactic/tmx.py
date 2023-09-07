import pygame
import pytmx
from pytmx.util_pygame import load_pygame

def load_tmx_map(filename):
    return load_pygame(filename)

def draw_map(screen, tmx_data):
    """Draws the map on the given screen."""
    for layer in tmx_data.visible_layers:
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    # Load the TMX map
    tmx_file = "C:\\dev-fg\\tiled-test\\terrain1.tmx"
    tmx_data = load_tmx_map(tmx_file)

    # Create a Pygame screen (window) with the size of the map
    screen = pygame.display.set_mode((tmx_data.width * tmx_data.tilewidth, tmx_data.height * tmx_data.tileheight))
    pygame.display.set_caption("Tiled Map Renderer")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the map
        draw_map(screen, tmx_data)

        # Update the display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
