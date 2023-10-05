import pygame
from Connection import Connection
from GraphicUI import UIList, UIPanel, UIGridList, UILabel, UIProgressBar

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
        #self.panel = UIPanel(600, 0, 400, 1000, "assets\\UI\\Box03.png", border_size=23)
        self.list2 = UIGridList(500, 30, list_width, 200, 4, [20, 100, 50, 30], "assets\\UI\\Box03.png", border_size=23)
        for i in range(20):
            self.list2.add_grid_row([UILabel(0,0, "1", font_size=30),UILabel(0,0, f"Player {i}", font_size=30),UIProgressBar(0,0, 50, 15, 5),UILabel(0,0, "Canada", font_size=30)])

        self.list = UIList(10, 30, list_width, 200, image="assets\\UI\\Box03.png", border_size=23, padding=7)
        for i in range(10):
            self.list.add_item(f"Player {i}")

        #self.panel.add_element(list)

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
            #self.panel.handle_event(event)


    def update(self):
        pass
        
    def render(self):
        #self.panel.draw(self.screen)
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
