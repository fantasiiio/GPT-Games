import pygame
from grid import Grid 
from Inputs import Inputs
from GraphicUI import UIPanel, UIButton,UIImage
from Tank import Tank

TILE_SIZE = 64
MENU_TILES_X = 20
MENU_TILES_Y = 20
GRID_WIDTH = TILE_SIZE * MENU_TILES_X
GRID_HEIGHT = TILE_SIZE * MENU_TILES_Y

pygame.init()
# Get native screen resolution
info = pygame.display.Info()
full_screen = False
if full_screen:
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)    
else:
    screen_width = 1500
    screen_height = 1200
    screen = pygame.display.set_mode((screen_width, screen_height))    

# Set the display mode to fullscreen and native resolution
#screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)

pygame.display.set_caption('Strategy Game')
inputs = Inputs()
panel_width = 250
grid = Grid(pygame, screen, "assets\\maps\\menu.tmx")
grid_offset = (-(grid.tiles_x*64)/2 + screen_width/2, -(grid.tiles_y*64)/2 + screen_height/2 + 64*2)
grid.move(grid_offset[0], grid_offset[1])

panel = UIPanel(screen_width/2 - panel_width/2, 20, panel_width, 200, image="panel.png", border_size=12)
new_game_button = UIButton(20, 20, 200, 50, "New Game",40, image="Box03.png", border_size=23)
panel.add_element(new_game_button)

tank = Tank(grid.tiles[35][26], 2, grid, screen=screen)
tank.angle = 180
tank.tower.angle = 180

tank.max_action_points = 50
tank.action_points = 50
tank.action_points = 50
tank.current_action = "move_to_target"
tank.seat_taken = 1

silence_sound = pygame.mixer.Sound("assets\\sounds\\silence.wav")
tank.gun_sound = silence_sound
tank.engine_sound = silence_sound
tank.explosion_sound = silence_sound

tank.move(grid.tiles[25][26])


running = True
while running:
    screen.fill((60, 60, 60))  # Fill background
    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            pass


        if event.type == pygame.MOUSEBUTTONUP:
            pass

    inputs.update()
    grid.update(inputs)
    grid.draw_grid(inputs)
    
    tank.update(inputs)
    tank.draw()

    panel.draw(screen)

    pygame.display.flip()
#    clock.tick(60)

pygame.quit()




