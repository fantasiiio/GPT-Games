from RandomEvents import RandomEvents
from Helicopter import Helicopter
from Soldier import Soldier
from Tank import Tank
from Boat import Boat
import random
import pygame
from GraphicUI import UIPanel, UIButton,UIImage, UILabel
#import pygame_gui
import sys
from grid import Grid
from Player import Player
import pygame.mixer
from config import GameStateString, screen, GRAY, GameState
from Inputs import Inputs
from MusicPlayer import MusicPlayer
from Item import Item
from Animation import Animation
from PlankAndBall import PlankAndBall
from PlayerAI import PlayerAI
import time

pygame.mixer.init()



class StrategyGame:
    def __init__(self, selected_team1= [], selected_team2= [], init_pygame=True, full_screen=False, screen=None):
        grid_width = 64 * 20
        grid_height = 64 * 20
        self.init_graphics(init_pygame, full_screen, screen, grid_width, grid_height)        
        self.selected_team = {}
        self.selected_team[1] = selected_team1
        self.selected_team[2] = selected_team2
        pygame.display.set_caption('Strategy Game')
        #self.manager = pygame_gui.UIManager((self.grid.grid_width, self.grid.grid_height))
        self.grid = Grid(pygame, self.screen, "assets\\maps\\terrain1.tmx")
        self.item_list = []
        self.coin_animation = Animation(self.screen, "assets\\images","", "Coin", -1, (32,32), 0, frame_duration=100) 

        self.item_list.append(Item(self.screen, self.grid, "coin", self.grid.tiles[4][4], self.coin_animation))
        self.players = {1: Player(1, True), 2: PlayerAI(2)}
        self.players[1].enemy = self.players[2]
        self.players[2].enemy = self.players[1]
        self.music_folder = 'assets\\music'
        self.music_player = MusicPlayer(self.music_folder)
        self.whoosh_sound = pygame.mixer.Sound("assets\\sounds\\whoosh.wav")
        self.event_good_sound = pygame.mixer.Sound("assets\\sounds\\event_good.wav")
        self.event_bad_sound = pygame.mixer.Sound("assets\\sounds\\event_bad.wav")
        self.inputs = Inputs()
        self.inputs.update()
        if self.inputs.mouse.clicked[0]: 
            self.inputs.mouse.ignore_next_click = True 
        self.global_id = 1
        self.observers = []
        self.placing_unit_index = 0
        self.current_player = 2
        self.ignore_next_click = False
        self.grid.set_camera_world_position(-self.grid.grid_width/2, -self.grid.grid_height/2)
        self.playing_mini_game = False
        self.mini_game_score = {}
        popup_width, popup_height = 640, 480
        self.popup_surface = pygame.Surface((popup_width, popup_height))        
        self.changing_game_state = False
        self.last_time_state_changed = 0
        self.next_state = GameState.UNIT_PLACEMENT
        self.game_state = None
        self.change_state()
        self.random_event = None
        # Create a new panel for queue list
        self.queue_panel = YourPanelClass(x_position, y_position_below_stats_panel, width, height)
        self.queue_label = UILabel(10, 10, "", font_size=30)
        self.queue_panel.add_element(self.queue_label)
        self.unit_queue = []

        # if not init_pygame:
        #     self.game_state = GameState.UNIT_PLACEMENT
        #     self.place_next_unit()
        # else:
        #     self.game_state = GameState.RANDOM_EVENT
        #     self.place_units_randomly(self.selected_team[1], 1)
        #     self.players[2].place_units(self.grid, self.selected_team[2], 6, self.screen, self.action_finished)
        #     self.notify_all_units("player_changed", 1)
        #     self.random_event = None
        self.init_ui()

            # Other state
        self.setting_display_order = [
            "Damage", 
            "HP",
            "AP",
            "Move Range",
            "Attack Range",
        ]

    def game_loop(self):
        # Main game loop
        running = True  # Control variable for the game loop
        mouse_pos = (0, 0)  # Initialize mouse position

        while running:
            self.screen.fill((0, 0, 0))  # Fill the screen with black
            current_time = time.time()  # Get the current time

            # Check if the game state is changing and if enough time has passed
            if self.changing_game_state and current_time - self.last_time_state_changed > self.state_change_wait_time:
                self.state_changed()  # Perform state change

            # Enable or disable the end-turn button based on whether player 1 is ready
            self.end_turn_button.enabled = not self.players[1].ready

            # If it's player 2's turn, execute the AI logic
            if self.current_player == 2:
                self.play_AI()

            # Update inputs (this would be your custom input-handling logic)
            self.inputs.update()

            # Initialize a list to hold mini-game events
            mini_game_events = []

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left-click
                        self.handle_mouse_click(event.pos)
                if event.type == pygame.QUIT:  # Close event
                    running = False  # End the game loop

                # Handle UI events
                self.ui_panel.handle_event(event)
                mini_game_events.append(event)

            # Update camera and grid
            self.grid.update_camera()
            self.grid.update(self.inputs)

            # Draw the grid
            self.grid.draw_grid(self.inputs)

            # Update and draw items
            for item in self.item_list:
                item.update()
                item.draw()

            # Update and draw units, skipping the unit on the selected tile
            for player in self.players.values():
                for unit in player.units:
                    if self.grid.selected_tile and unit == self.grid.selected_tile.unit:
                        continue
                    unit.update(self.inputs)
                    unit.draw()

            # Draw the unit on the selected tile, if any
            if self.grid.selected_tile:
                unit = self.grid.selected_tile.unit
                if unit:
                    unit.update(self.inputs)
                    unit.draw()

            # Draw UI panels
            self.ui_panel.draw(self.screen)
            self.update_stats_panel()
            self.update_queue_panel()

            # Draw stats panel if a tile with a unit is selected
            if self.grid.selected_tile and self.grid.selected_tile.unit:            
                self.stats_panel.draw(self.screen)

            # Draw mini-game, if active
            if self.playing_mini_game:
                mini_game_running, self.mini_game_score[self.current_player] = self.mini_game.draw_game()
                self.screen.blit(self.popup_surface, (self.screen.get_width() / 2 - self.popup_surface.get_width() / 2, self.screen.get_height() / 2 - self.popup_surface.get_height() / 2))
                if not mini_game_running:
                    self.playing_mini_game = False  # End the mini-game

            # Update the display
            pygame.display.flip()

        # Quit the pygame library if it was initialized
        if self.init_pygame:
            pygame.quit()



if __name__ == "__main__":
    selected_team1 = ["Tank","Soldier", "Soldier"] 
    selected_team2 = ["Tank","Soldier", "Soldier"] 
    game = StrategyGame(selected_team1, selected_team2)
    game.game_loop()
