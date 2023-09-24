import pygame
from grid import Grid 
from Inputs import Inputs
from GraphicUI import UIPanel, UIButton,UIImage, UILabel
from Tank import Tank


class MainMenu:
    def __init__(self, init_pygame=True, full_screen=False, screen=None):
        self.init_graphics(init_pygame, full_screen, screen, 1500,1200)
        
        self.TILE_SIZE = 64
        self.MENU_TILES_X = 20
        self.MENU_TILES_Y = 20
        self.GRID_WIDTH = self.TILE_SIZE * self.MENU_TILES_X
        self.GRID_HEIGHT = self.TILE_SIZE * self.MENU_TILES_Y
        
        pygame.display.set_caption('Strategy Game')
        
        self.inputs = Inputs()
        self.panel_width = 240
        self.panel_height = 300
        self.grid = Grid(pygame, self.screen, "assets/maps/menu.tmx")
        self.grid_offset = (-(self.grid.tiles_x*64)/2 + self.screen_width/2, 
                            -(self.grid.tiles_y*64)/2 + self.screen_height/2 + 64*2)
        
        self.grid.move(self.grid_offset[0], self.grid_offset[1])
        
        self.menu_panel = UIPanel(self.screen_width/2 - self.panel_width/2, 120, 
                             self.panel_width, self.panel_height, image="panel.png")
                             

        self.top_panel = UIPanel(0, 0, 0, 0, color=(0,0,0))
        font = pygame.font.Font('assets\\UI\\Army.ttf', 72)
        self.player_label = UILabel(10, 20, f"Battle Grid", font=font, text_color=(232,217,194), outline_width=1)
        self.player_label.rect.x = self.screen_width / 2 - self.player_label.rect.width / 2
        self.top_panel.add_element(self.player_label)

        self.create_buttons()

        self.tank = Tank(self.grid.tiles[35][26], 2, self.grid, screen=self.screen)
        self.tank.angle = 180
        self.tank.tower.angle = 180
        
        silence_sound = pygame.mixer.Sound("assets\\sounds\\silence.wav")
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
                "New Game": self.menu_clicked,
                "Multiplayer": self.menu_clicked,
                "Instructions": self.menu_clicked,
                "Quit": self.menu_clicked
            }

            y_offset = 20  # Initial vertical offset
            for label, callback in button_map.items():
                button = UIButton(20, y_offset, 200, 50, label, 40, "Box03.png", border_size=23, callback=callback)
                y_offset += 60  # Increment vertical offset for the next button
                self.menu_panel.add_element(button)


    def menu_clicked(self, button):
        self.running = False
        self.selected_menu_item = button.text

    def handle_input(self):
        for event in pygame.event.get():
            self.menu_panel.handle_event(event)
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
        
    def render(self):
        self.screen.fill((60, 60, 60))  
        self.grid.draw_grid(self.inputs)
        self.tank.draw()
        self.menu_panel.draw(self.screen)
        self.top_panel.draw(self.screen)
        pygame.display.flip()
        
    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.render()
        if self.init_pygame:
            pygame.quit()            
        return self.selected_menu_item
            
if __name__ == "__main__":
    game = MainMenu()
    game.run()