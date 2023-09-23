from menu import MainMenu
from Game import StrategyGame
from BuildTeam import TeamBuilder
from instructions import Instructions
import pygame

class MainFrame():
    def __init__(self):
        self.init_graphics(True, False, None, 1500, 1280)

    def init_graphics(self, init_pygame, full_screen, screen, width, height):
        self.init_pygame = init_pygame
        if init_pygame:
            pygame.init()
            self.full_screen = full_screen 
            
            # Setup screen
            info = pygame.display.Info()
            if self.full_screen:
                self.screen_width = info.current_w
                self.screen_height = info.current_h
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)    
            else:
                self.screen_width = width
                self.screen_height = height
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        else:
            self.screen = screen
            self.screen_width = screen.get_width()
            self.screen_height = screen.get_height() 

    def run(self):
        running = True
        while running:
            main_menu = MainMenu(False, False, self.screen)
            selected_menu_item = main_menu.run()
            if selected_menu_item == "New Game":
                team_builder = TeamBuilder(1, False, False, self.screen)
                selected_team1 = team_builder.run()
                team_builder = TeamBuilder(2, False, False, self.screen)
                selected_team2 = team_builder.run()
                game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
                game.game_loop()
            elif selected_menu_item == "Instructions":
                instructions = Instructions(init_pygame=False, full_screen=False, screen=self.screen)
                instructions.run()
            elif selected_menu_item == "Quit":
                running = False

main = MainFrame()
main.run()
