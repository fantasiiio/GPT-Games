from RandomEvents import RandomEvents
from Helicopter import Helicopter
from Soldier import Soldier
from Tank import Tank
from Boat import Boat
import random
import pygame
from GraphicUI import UIPanel, UIButton,UIImage, UILabel,UIList
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
        self.whoosh_sound = pygame.mixer.Sound("assets\\sounds\\start.wav")
        self.event_good_sound = pygame.mixer.Sound("assets\\sounds\\event_good.wav")
        self.event_bad_sound = pygame.mixer.Sound("assets\\sounds\\event_bad.wav")
        self.stump_sound = pygame.mixer.Sound("assets\\sounds\\stomp.wav")
        self.green_check_image = pygame.image.load("assets\\UI\\green_check.png")
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
        self.unit_queue = []
        self.queue_panel = None
        self.queue_label = None

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

    def get_units_can_do_action(self, player):
        units = []
        for unit in self.players[player].units:
            if unit.can_do_actions():
                units.append(unit)
        return units

    def get_next_state(self, current_state):
        next_states = {None: GameState.UNIT_PLACEMENT,
            #GameState.UNIT_PLACEMENT: GameState.RANDOM_EVENT,
            GameState.UNIT_PLACEMENT: GameState.PLANNING,
            GameState.PLANNING: GameState.EXECUTION,
            GameState.EXECUTION: GameState.OUTCOME,
            GameState.OUTCOME: GameState.RANDOM_EVENT} 
        return next_states[current_state]
           

    def format_stats(self, data):
        formatted_str = f"Player{data['Player']}: {data['Type']}\n\n"
        for key in self.setting_display_order:
            if key in data:
                formatted_str += f"{key}: {data[key]}\n"
        return formatted_str

    def place_units_randomly(self, team, player):
        for unit_type in team:
            tile = None
            if unit_type == "Soldier":
                tile = self.grid.get_random_tile()
                unit = Soldier(tile, player, self.grid, screen=self.screen, action_finished=self.action_finished)
            elif unit_type == "Tank":
                tile = self.grid.get_random_tile()
                unit = Tank(tile, player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
            elif unit_type == "Helicopter":
                tile = self.grid.get_random_tile()
                unit = Helicopter(tile, player, self.grid, screen=self.screen, action_finished=self.action_finished)
            elif unit_type == "Boat":
                tile = self.grid.get_random_tile(True)
                unit = Boat(tile, player, self.grid, screen=self.screen, action_finished=self.action_finished)
            
            self.register_observer(unit)
            #unit.place_on_tiles(tile)
            self.players[player].add_unit(unit)

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
            self.screen_width = width
            self.screen_height = height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_all_units(self, event, value):
        for observer in self.observers:
            observer.on_message(event, value)


    def update_state_label(self):
        if self.game_state:
            self.state_label.set_text(f"{GameStateString[self.game_state.name]}")
            self.state_label.rect.x = self.ui_panel.rect.width / 2 - self.state_label.rect.width / 2
            if self.game_state == GameState.RANDOM_EVENT and self.random_event:
                self.state_label2.set_text(f"{self.random_event['name']}: {self.random_event['description']}")
                self.state_label2.rect.x = self.ui_panel.rect.width / 2 - self.state_label2.rect.width / 2
            
            else:
                self.state_label2.set_text(f"Player {self.current_player}")
                self.state_label2.rect.x = self.ui_panel.rect.width / 2 - self.state_label2.rect.width / 2

    def update_stats_panel(self):
        if self.grid.selected_tile and self.grid.selected_tile.unit:
            unit = self.grid.selected_tile.unit
            formated_stats = self.format_stats(unit.get_stats())
            self.unit_info_label.set_text(formated_stats)
        else:
            self.unit_info_label.set_text("")

    # Function to update the queue_panel
    # def update_queue_panel(self):
    #     formatted_queue = self.format_queue()
    #     self.queue_label.set_text(formatted_queue)

    # Function to format queue into a string

    # def format_queue(self):
    #     queue_str = "Queue:\n\n "
    #     for unit in self.unit_queue:
    #         if isinstance(unit, str):
    #             queue_str += f"{unit}\n"
    #         else:
    #             queue_str += f"{unit.name}\n"
    #     return queue_str.rstrip(', ')


    def init_ui(self):
        # Create UI panel
        self.ui_panel = UIPanel(0, 0, self.screen.get_width(), 100, color=(0,0,0))
        
        # Create labels
        self.state_label = UILabel(10, 10, "", self.ui_panel, font_size=60)
        self.state_label2 = UILabel(10, 60, "", self.ui_panel, font_size=40)
        self.update_state_label()

        # Create button  
        self.end_turn_button = UIButton(0, 10, 200, 60, 
            "End Turn", parent=self.ui_panel,image="assets\\UI\\Box03.png", font_size=40, callback=self.end_turn_button_clicked)
        
        self.end_turn_button.rect.right = self.screen.get_width() - 10
        self.end_turn_button.rect.bottom = self.screen.get_height() - 10
        self.end_turn_button.enabled = True

        self.ui_panel.add_element(self.state_label)
        self.ui_panel.add_element(self.state_label2)
        self.ui_panel.add_element(self.end_turn_button)

        panel_width = 240
        self.stats_panel = UIPanel(self.screen_width-250, self.ui_panel.rect.bottom + 10, panel_width, 200, color=(0,0,0))
        self.unit_info_label = UILabel(10, 10, "", font_size=30)
        self.stats_panel.add_element(self.unit_info_label)

        rect = self.stats_panel.rect
        self.queue_panel = UIPanel(rect.left, rect.bottom + 20, panel_width, 300, color=(0,0,0))
        # self.queue_label = UILabel(10, 10, "", font_size=30)
        # self.queue_panel.add_element(self.queue_label)

        self.queue_list = UIList(rect.left, rect.bottom + 20, panel_width, 200, item_selected_callback = self.item_selected_callback)
        index = 1
        for unit in self.selected_team[1]:
            self.queue_list.add_item(f"{index}-{unit}", self.green_check_image, id = index)
            index+= 1
        # queue_list.add_item('Item 1')
        # queue_list.add_item('Item 2', self.green_check_image)
        # queue_list.add_item('Item 3')

        self.queue_panel.add_element(self.queue_list)

    def item_selected_callback(self, item):
        print(item)

    def apply_random_event(self):
        if self.game_state == GameState.RANDOM_EVENT:
            random_event = RandomEvents(self.players[self.current_player], self.players[3-self.current_player])
            self.random_event = random_event.random_event()
            if self.random_event["type"] == "good":
                self.event_good_sound.play()
            elif self.random_event["type"] == "bad":
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
            placing_unit = Soldier(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
        elif placing_unit_type == "Tank":
            placing_unit = Tank(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
        elif placing_unit_type == "Helicopter":
            placing_unit = Helicopter(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())
        elif placing_unit_type == "Boat":
            placing_unit = Boat(None, self.current_player, self.grid, screen=self.screen, action_finished=self.action_finished, id=self.generate_id())

        self.placing_unit_index += 1
        placing_unit.current_player = self.current_player
        placing_unit.current_game_state = self.game_state
        self.register_observer(placing_unit)
        self.players[1].add_unit(placing_unit)

    def planify_next_unit(self):
        if self.placing_unit_index > 0:
            self.players[1].units[self.placing_unit_index].is_planning = False
        
        units = self.get_units_can_do_action(1)
        if self.placing_unit_index == len(units):
            return

        planning_unit = units[self.placing_unit_index]
        self.placing_unit_index += 1
        self.grid.selected_tile = planning_unit.tile
        planning_unit.current_action = "choosing_action"
        planning_unit.is_planning = True

        self.queue_list.select_item(planning_unit.id)
        self.grid.move_camera_to_tile(planning_unit.tile)           


    def check_unit_in_list(self, unit):
        item = self.queue_list.get_item_by_id(unit.id)
        if item:
            item.checked = True
            item.disabled = True

    def action_finished(self, unit):
        if self.placing_unit_index == len(self.selected_team[1]):
            self.end_turn_button_clicked(None)

        if self.game_state == GameState.UNIT_PLACEMENT:
            self.place_next_unit()
            self.check_unit_in_list(unit)
            self.stump_sound.play()
        if self.game_state == GameState.PLANNING:
            # self.grid.selected_tile = None

            self.planify_next_unit()
            self.check_unit_in_list(unit)


    def change_player(self):
        self.current_player = 3 -self.current_player
        self.notify_all_units("player_changed", self.current_player)

    def change_state(self):
        self.last_time_state_changed = time.time()
        if(self.game_state):
            self.state_change_wait_time = 1
        else:
            self.state_change_wait_time = 0

        self.changing_game_state = True
        if self.players[1].ready and self.players[2].ready:
            self.next_state = self.get_next_state(self.game_state)

    def state_changed(self):
        self.changing_game_state = False
        self.change_player()

        # Before changing state, check if there is any unit in the queue
        if self.game_state == GameState.UNIT_PLACEMENT:
            self.queue_list.reset_all()


        self.game_state = self.next_state
        if self.current_player == 1:
            if self.game_state != None:
                self.whoosh_sound.play()        

            self.players[1].ready = False
            self.players[2].ready = False
            self.notify_all_units("game_state_changed", self.game_state)

        if self.game_state == GameState.RANDOM_EVENT:
            self.apply_random_event()
        elif self.game_state == GameState.UNIT_PLACEMENT:
            self.placing_unit_index = 0
            if self.current_player == 1:
                #self.unit_queue = self.selected_team[1]
                self.place_next_unit()
        elif self.game_state == GameState.PLANNING:
            self.placing_unit_index = 0
            if self.current_player == 1:
                can_do_action_units =  self.get_units_can_do_action(1)
                for unit in self.players[1].units:
                    if unit not in can_do_action_units:
                        self.queue_list.enable_item(unit.id, False)
                self.planify_next_unit()
                


        self.update_state_label()


    def end_turn_button_clicked(self, button):
        self.inputs.mouse.clicked[0] = False
        self.inputs.mouse.ignore_next_click = True        
        self.end_turn_button.enabled = False
        self.players[1].ready = True
        self.change_state()

    def handle_mouse_click(self, pos):
        pass

    def get_unit_index(self, unit):
        for i, u in enumerate(self.players[unit.player].units):
            if u == unit:
                return i
        return -1

    def AI_planning(self):
        for ai_unit in self.get_units_can_do_action(2):
            closest_enemy = min(self.players[1].units, key=lambda unit: self.grid.get_manathan_range(ai_unit.position, unit.position))
            
            # Step 2: Find path to the closest enemy
            path = self.grid.find_path(ai_unit.position, closest_enemy.position)
            next_straight_point  = self.grid.get_next_straight_point(path)
            next_point_within_range = self.grid.get_next_point_within_max_range(path[0], next_straight_point, ai_unit.move_range)
            range = self.grid.get_manathan_range(ai_unit.position, next_point_within_range)
            if range <= ai_unit.attack_range:
                path = path[:path.index(next_point_within_range)]

            # Step 3: Move towards the enemy
            if path:
                steps_to_take = min(len(path) - 1, ai_unit.move_range)
                ai_unit.position = path[steps_to_take]
                
            # Step 4: Check if the enemy is in attack range
            if distance(ai_unit.position, closest_enemy.position) <= ai_unit.attack_range:
                # Attack
                closest_enemy.health -= ai_unit.attack_damage
            

    def play_AI(self):
        if self.game_state == GameState.UNIT_PLACEMENT and not self.players[2].ready:
            self.players[2].ready = True
            self.players[2].place_units(self.grid, self.selected_team[2], 6, self.screen, self.end_turn_button_clicked)            
            self.change_state()            
        elif self.game_state == GameState.RANDOM_EVENT and not self.players[2].ready:
            self.players[2].ready = True
            self.change_state()
        elif self.game_state == GameState.PLANNING:
            self.AI_planning()

    def game_loop(self):
        running = True
        mouse_pos = (0, 0)
        while running:
            self.screen.fill((0, 0, 0)) 
            current_time = time.time()
            if self.changing_game_state and current_time - self.last_time_state_changed > self.state_change_wait_time:
                self.state_changed()
            
            self.end_turn_button.enabled = not self.players[1].ready

            if self.current_player == 2:
                self.play_AI()

            self.inputs.update()
            mini_game_events = []
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_mouse_click(event.pos)
                if event.type == pygame.QUIT:
                    running = False

                self.ui_panel.handle_event(event)
                self.queue_panel.handle_event(event)
                mini_game_events.append(event)

            self.grid.mouse_over_UI = self.queue_panel.rect.collidepoint(self.inputs.mouse.pos) or self.end_turn_button.rect.collidepoint(self.inputs.mouse.pos)

            self.grid.update_camera()
            self.grid.update(self.inputs)
            self.grid.draw_grid(self.inputs)
            for item in self.item_list:
                item.update()
                item.draw()

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
            self.update_stats_panel()
            #self.update_queue_panel()
            self.queue_panel.draw(self.screen)
            if self.grid.selected_tile and self.grid.selected_tile.unit:            
                self.stats_panel.draw(self.screen)

            if self.playing_mini_game:
                mini_game_running, self.mini_game_score[self.current_player] = self.mini_game.draw_game()
                self.screen.blit(self.popup_surface, (self.screen.get_width() / 2 - self.popup_surface.get_width() / 2, self.screen.get_height() / 2 - self.popup_surface.get_height() / 2))
                if not mini_game_running:
                    self.playing_mini_game = False


            pygame.display.flip()

        if self.init_pygame:
            pygame.quit()    

if __name__ == "__main__":
    selected_team1 = ["Tank","Soldier", "Soldier"] 
    selected_team2 = ["Tank","Soldier", "Soldier"] 
    game = StrategyGame(selected_team1, selected_team2)
    game.game_loop()
