import pygame
from grid import Grid 
from Inputs import Inputs
from GraphicUI import *
from Tank import Tank
from config import *

class MainMenu:
    def __init__(self, init_pygame=True, full_screen=False, screen=None):
        self.init_graphics(init_pygame, full_screen, screen, 1500,1200)
        
        self.init_ui()
#        self.menu_container.set_position(self.menu_container.rect.x, self.menu_container.rect.y - 200)

        self.tank = Tank(self.grid.tiles[35][26], 2, self.grid, screen=self.screen)
        self.tank.angle = 180
        self.tank.child.angle = 180
        
        silence_sound = pygame.mixer.Sound(f"{base_path}\\assets\\sounds\\silence.wav")
        self.tank.max_action_points = 50
        self.tank.action_points = 50
        self.tank.action_points = 50
        self.tank.current_action = "move_to_target"
        self.tank.seat_taken = 1
        self.tank.gun_sound = silence_sound
        self.tank.engine_sound = silence_sound
        self.tank.explosion_sound = silence_sound
        self.tank.move(self.grid.tiles[25][26])
        self.selected_menu_item = None
        self.running = True
        
    def init_ui(self):
        self.TILE_SIZE = 64
        self.MENU_TILES_X = 20
        self.MENU_TILES_Y = 20
        self.GRID_WIDTH = self.TILE_SIZE * self.MENU_TILES_X
        self.GRID_HEIGHT = self.TILE_SIZE * self.MENU_TILES_Y
        
        pygame.display.set_caption('Strategy Game')
        
        self.inputs = Inputs()
        self.container_width = 240
        self.container_height = 350
        self.grid = Grid(pygame, self.screen, f"{base_path}\\assets\\maps\\menu.tmx")
        tile = self.grid.tiles[26][26]
        tile_pos = tile.x * self.TILE_SIZE, tile.y * self.TILE_SIZE
        
        self.grid.move(-tile_pos[0], -tile_pos[1])


        self.menu_container = UIContainer(100,0, 
                             self.container_width, self.container_height, image=f"{base_path}\\assets\\UI-v2\\Window\\Window_Background.png", padding = 20)
                             
        self.menu_container.adjust_to_content()

        self.top_container = UIContainer(0, 0)
        self.player_label = UILabel(10, 20, f"Battle Grid", text_color=(232,217,194), outline_width=1, font_size=100, font_path=f"{base_path}\\assets\\UI\\Army.ttf")
        self.player_label.rect.x = self.screen_width / 2 - self.player_label.rect.width / 2
        self.top_container.add_element(self.player_label)
        self.top_container.adjust_to_content()
        self.top_container.center_on_screen(self.screen_width, self.screen_height, 20)
        self.create_buttons()
        self.menu_container.center_on_screen(self.screen.get_width(), self.screen.get_height(), 200)

        self.ui_manager = UIManager()        
        self.ui_manager.add_container(self.menu_container)
        self.ui_manager.add_container(self.top_container)



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

    def create_buttons(self):
        button_map = {
            "Single Player": self.menu_clicked,
            "Multi-Player": self.menu_clicked,
            "Instructions": self.menu_clicked,
            "Mini Game": self.menu_clicked,
            "Quit": self.menu_clicked
        }

        y_offset = 20  # Initial vertical offset
        spacing = 20  # Vertical spacing between buttons
        for label, callback in button_map.items():
            button_height = 64
            button = UIButton(20, y_offset, 200, button_height, label, 40, callback=callback)
            y_offset += button_height + spacing
            self.menu_container.add_element(button)

        self.menu_container.adjust_to_content()                


    def menu_clicked(self, button):
        self.running = False
        self.selected_menu_item = button.text

    def handle_input(self, events_list):
        events_list = pygame.event.get() if events_list is None else events_list
        for event in events_list:
            self.menu_container.handle_event(event)
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
                
            if event.type == pygame.MOUSEMOTION:
                pass
                
            if event.type == pygame.MOUSEBUTTONUP:
                pass
                
        self.inputs.update()

    def update(self):
        self.grid.update(self.inputs)
        self.tank.update(self.inputs)
        
    def render(self, no_flip=False):
        self.screen.fill((60, 60, 60))  
        self.grid.draw_grid(self.inputs, False)
        self.tank.draw()
        self.menu_container.draw(self.screen)
        self.top_container.draw(self.screen)
        if not no_flip:
            pygame.display.flip()
        
    def run_frame(self, events_list=None):
        self.handle_input(events_list)
        self.update()
        self.render(True)
        return self.selected_menu_item
    
    def run(self):
        while self.running:
            self.run_frame()
        if self.init_pygame:
            pygame.quit()            
        return self.selected_menu_item
            
if __name__ == "__main__":
    game = MainMenu()
    game.run()