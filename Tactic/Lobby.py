import pygame
from Connection import Connection
from GraphicUI import UIList, UIContainer, UILabel, UIProgressBar, UIButton, UICheckBox
from config import *

class Lobby():
    def __init__(self, init_pygame=True, full_screen=False, screen=None):
        self.init_graphics(init_pygame, full_screen, screen, 1500,1200)
        self.init_UI()
        pass

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

    def init_UI(self):
        list_width = 400
        #self.container = UIContainer(600, 0, 400, 1000, f"{base_path}\\assets\\UI\\Box03.png", border_size=23)
        self.list2 = UIList(10, 100, list_width, 200, image=f"{base_path}\\assets\\UI\\Box03.png", border_size=23, padding=7, num_columns=4, column_widths=[100, 150, 50, 50], headers=["Win/Loose', 'Name', 'Ping', 'Country'], header_height=40)
        row_height = 30
        for i in range(20):
            button1 = UIButton(20,0, 50, row_height, text="Invite")
            checkbox = UICheckBox(0,0, 40, 40, image=f"{base_path}\\assets\\UI\\checkbox.png", icon=f"{base_path}\\assets\\UI\\green_check.png")
            checkbox.checked = True
            progress = UIProgressBar(0,0, 50, 15, 5, max_value=5)
            progress.current_value = 3
            name_label = UILabel(0,0, f"Player {i}", font_size=30)
            self.list2.add_row([checkbox,name_label,progress, button1])


        #self.container.add_element(list)

    def item_selected_callback(self, item):
        pass

    def connect(self, host, port):
        self.connection = Connection(host=host, port=port, use_singleton=True)
        self.connection.connect()


    def update_player_list(self):
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False     
        
            self.list.handle_event(event)
            self.list2.handle_event(event)
            #self.container.handle_event(event)


    def update(self):
        pass
        
    def render(self):
        #self.container.draw(self.screen)
        self.list.draw(self.screen)
        self.list2.draw(self.screen)
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.screen.fill((0,0,0))
            self.handle_input()
            self.update()
            self.render()

connect = Lobby()
connect.run()
