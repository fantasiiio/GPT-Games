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
    def __init__(self, selected_team= []):
        selected_team = ["Tank", "Tank"]
        self.selected_team = selected_team 
        pygame.init()
        self.screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
        pygame.display.set_caption('Strategy Game')
        #self.manager = pygame_gui.UIManager((GRID_WIDTH, GRID_HEIGHT))
        self.grid = Grid(pygame, self.screen, "assets\\maps\\terrain1.tmx")
        self.players = {1: Player(1, True), 2: Player(2, False)}
        self.music_folder = 'assets\\music'
        self.music_player = MusicPlayer(self.music_folder)
        self.whoosh_sound = pygame.mixer.Sound("assets\\sounds\\whoosh.wav")
        self.inputs = Inputs()
        self.global_id = 1
        self.game_state = GameState.UNIT_PLACEMENT
        self.init_ui()
        self.observers = []
        self.placing_unit = None
        self.placing_unit_index = 0
        self.place_next_unit()

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_all_units(self, event, value):
        for observer in self.observers:
            observer.on_message(event, value)


    def update_state_label(self):
        self.state_label.text = f"{GameStateString[self.game_state.name]}"

    def init_ui(self):
        # Create UI panel
        self.ui_panel = UIPanel(0, 0, GRID_WIDTH, 80, color=(0,0,0))
        
        # Create labels
        self.state_label = UILabel(10, 30, 
            f"{GameStateString[self.game_state.name]}", self.ui_panel, font_size=60)
        self.state_label.rect.x = self.ui_panel.rect.width / 2 - self.state_label.rect.width / 2
        
        # Create button  
        self.end_turn_button = UIButton(0, 10, 200, 60, 
            "End Turn", parent=self.ui_panel,image="Box03.png", font_size=40, callback=self.end_turn_button_clicked)
        
        self.end_turn_button.rect.right = GRID_WIDTH - 10
        self.end_turn_button.rect.bottom = GRID_HEIGHT - 10
        self.end_turn_button.enabled = False

        self.ui_panel.add_element(self.state_label)
        self.ui_panel.add_element(self.end_turn_button)

    def end_turn_button_clicked(self, button):
        self.whoosh_sound.play()
        if self.game_state == GameState.UNIT_PLACEMENT:
            self.game_state = GameState.PLANNING
            self.update_state_label()
            self.notify_all_units("game_state_changed", self.game_state)
            self.end_turn_button.enabled = False

    def generate_id(self):
            id = self.global_id 
            self.global_id += 1
            return id   
    
    def place_next_unit(self):
        if self.placing_unit_index == len(self.selected_team):
            return
        placing_unit_type = self.selected_team[self.placing_unit_index]
        if placing_unit_type == "Soldier":
            self.placing_unit = Soldier(None, 1, self.grid, screen=self.screen, action_finished=self.action_finished)
        elif placing_unit_type == "Tank":
            self.placing_unit = Tank(None, 1, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
        elif placing_unit_type == "Helicopter":
            self.placing_unit = Helicopter(None, 1, self.grid, screen=self.screen, action_finished=self.action_finished)
        elif placing_unit_type == "Boat":
            self.placing_unit = Boat(None, 1, self.grid, screen=self.screen, action_finished=self.action_finished)

        self.placing_unit_index += 1
        self.placing_unit.current_game_state = self.game_state
        self.players[1].add_unit(self.placing_unit)        

    def action_finished(self, unit):
        if self.placing_unit_index == len(self.selected_team):
            self.end_turn_button.enabled = True
        self.register_observer(unit)
        unit.current_game_state = None
        if self.game_state == GameState.UNIT_PLACEMENT:
            self.place_next_unit()

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

        pygame.quit()

if __name__ == "__main__":
    game = StrategyGame()
    game.game_loop()
