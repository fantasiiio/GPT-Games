from RandomEvents import RandomEvents
from Helicopter import Helicopter
import random
import pygame
from GraphicUI import UIPanel, UIButton,UIImage, UILabel
#import pygame_gui
import sys
from grid import Grid
from Player import Player
from Soldier import Soldier
from Tank import Tank
import pygame.mixer
from config import GameStateString, screen, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY, GameState
from Inputs import Inputs
from MusicPlayer import MusicPlayer
from Boat import Boat


pygame.mixer.init()



class StrategyGame:
    def __init__(self, selected_team1= [], selected_team2= [], init_pygame=True, full_screen=False, screen=None):
        self.init_graphics(init_pygame, full_screen, screen, GRID_WIDTH, GRID_HEIGHT)        
        self.selected_team = {}
        self.selected_team[1] = selected_team1
        self.selected_team[2] = selected_team2

        pygame.display.set_caption('Strategy Game')
        #self.manager = pygame_gui.UIManager((GRID_WIDTH, GRID_HEIGHT))
        self.grid = Grid(pygame, self.screen, "assets\\maps\\terrain1.tmx")
        self.players = {1: Player(1, True), 2: Player(2, False)}
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
        self.game_state = GameState.UNIT_PLACEMENT
        self.observers = []
        self.placing_unit_index = 0
        self.random_events = []
        self.current_player = 1
        self.init_ui()
        self.place_next_unit()
        self.ignore_next_click = False

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

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_all_units(self, event, value):
        for observer in self.observers:
            observer.on_message(event, value)


    def update_state_label(self):
        self.state_label.set_text(f"{GameStateString[self.game_state.name]}")
        self.state_label.rect.x = self.ui_panel.rect.width / 2 - self.state_label.rect.width / 2
        self.state_label2.set_text(f"Player {self.current_player}")
        self.state_label2.rect.x = self.ui_panel.rect.width / 2 - self.state_label2.rect.width / 2

    def init_ui(self):
        # Create UI panel
        self.ui_panel = UIPanel(0, 0, GRID_WIDTH, 100, color=(0,0,0))
        
        # Create labels
        self.state_label = UILabel(10, 10, "", self.ui_panel, font_size=60)
        self.state_label2 = UILabel(10, 60, "", self.ui_panel, font_size=40)
        self.update_state_label()

        # Create button  
        self.end_turn_button = UIButton(0, 10, 200, 60, 
            "End Turn", parent=self.ui_panel,image="Box03.png", font_size=40, callback=self.end_turn_button_clicked)
        
        self.end_turn_button.rect.right = GRID_WIDTH - 10
        self.end_turn_button.rect.bottom = GRID_HEIGHT - 10
        self.end_turn_button.enabled = False

        self.ui_panel.add_element(self.state_label)
        self.ui_panel.add_element(self.state_label2)
        self.ui_panel.add_element(self.end_turn_button)

    def random_event(self):
        if self.game_state == GameState.RANDOM_EVENT:
            random_event = RandomEvents(self.players[self.current_player], self.players[3-self.current_player])
            event = random_event.random_event()
            if event.type == "good":
                self.event_good_sound.play()
            elif event.type == "bad":
                self.event_bad_sound.play()

    def generate_id(self):
            id = self.global_id 
            self.global_id += 1
            return id   
    
    def place_next_unit(self):
        team = self.selected_team[self.current_player]
        if self.placing_unit_index == len(team):
            return
        placing_unit_type = team[self.placing_unit_index]
        if placing_unit_type == "Soldier":
            placing_unit = Soldier(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished)
        elif placing_unit_type == "Tank":
            placing_unit = Tank(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
        elif placing_unit_type == "Helicopter":
            placing_unit = Helicopter(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished)
        elif placing_unit_type == "Boat":
            placing_unit = Boat(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished)

        self.placing_unit_index += 1
        placing_unit.current_player = self.current_player
        placing_unit.current_game_state = self.game_state
        self.players[1].add_unit(placing_unit)        

    def action_finished(self, unit):
        if self.placing_unit_index == len(self.selected_team[self.current_player]):
            self.end_turn_button.enabled = True
        self.register_observer(unit)
        unit.current_game_state = None
        if self.game_state == GameState.UNIT_PLACEMENT:
            self.place_next_unit()

    def change_player(self):
        self.current_player = 3 -self.current_player
        self.notify_all_units("player_changed", self.current_player)

    def change_state(self, state):
        self.game_state = state
        self.update_state_label()
        self.notify_all_units("game_state_changed", self.game_state)

    def end_turn_button_clicked(self, button):
        self.whoosh_sound.play()
        self.inputs.mouse.clicked[0] = False
        self.inputs.mouse.ignore_next_click = True        
        if self.game_state == GameState.UNIT_PLACEMENT:
            if self.current_player == 1:
                self.change_player()
                self.placing_unit_index = 0
                self.update_state_label()
                self.place_next_unit()                
            else:
                self.change_player()
                self.change_state(GameState.RANDOM_EVENT)
                self.end_turn_button.enabled = False
                self.random_event()

    def handle_mouse_click(self, pos):
        pass

    def get_unit_index(self, unit):
        for i, u in enumerate(self.players[unit.player].units):
            if u == unit:
                return i
        return -1

    def update_ui(self):
        if self.grid.selected_tile and self.grid.selected_tile.unit:
            unit = self.grid.selected_tile.unit
            self.unit_info_label.set_text(f"Health: 100  Points: {unit.action_points}")

    def game_loop(self):
        running = True
        mouse_pos = (0, 0)
        while running:
            time_delta = pygame.time.Clock().tick(60) / 1000.0
            self.inputs.update()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_mouse_click(event.pos)
                if event.type == pygame.QUIT:
                    running = False

                self.ui_panel.handle_event(event)

            self.grid.update(self.inputs)
            self.grid.draw_grid(self.inputs)

            for player in self.players.values():
                for unit in player.units:
                    if self.grid.selected_tile and unit == self.grid.selected_tile.unit:
                        continue
                    unit.update(self.inputs)
                    unit.draw()

            if self.grid.selected_tile:
                unit = self.grid.selected_tile.unit
                if unit:
                    unit.update(self.inputs)
                    unit.draw()

            self.ui_panel.draw(self.screen)
            pygame.display.flip()

        if self.init_pygame:
            pygame.quit()    

if __name__ == "__main__":
    selected_team1 = ["Helicopter", "Helicopter"] 
    selected_team2 = ["Tank", "Tank"] 
    game = StrategyGame(selected_team1, selected_team2)
    game.game_loop()
