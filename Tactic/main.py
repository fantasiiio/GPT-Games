import pygame
from PlankAndBall import PlankAndBall

screen = None

def init_graphics(init_pygame, full_screen, width, height):
    global screen_width, screen_height, screen
    init_pygame = init_pygame
    if init_pygame:
        pygame.init()
        full_screen = full_screen 
        
        # Setup screen
        info = pygame.display.Info()
        if full_screen:
            screen_width = info.current_w
            screen_height = info.current_h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)    
        else:
            screen_width = width
            screen_height = height
            screen = pygame.display.set_mode((screen_width, screen_height))
    else:
        screen_width = width
        screen_height = height
        screen = pygame.display.set_mode((screen_width, screen_height))

running = True
def run_game():
    global running, game
    while running:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pass
            if event.type == pygame.QUIT:
                running = False


        running,_ = game.draw_game()
        # Update the display
        pygame.display.flip()

init_graphics(True, False, 1500, 1280)
game = PlankAndBall(init_pygame=False, full_screen=False, screen=screen)
run_game()