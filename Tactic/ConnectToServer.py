import pygame
from Connection import Connection
from GraphicUI import UIList, UIContainer, UIGridList, UILabel

class ConnectToServer():
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
        list_width = 200
        self.player_list = UIGridList(self.screen_width - list_width - 30, 30, list_width, 200, 4, [20,100,50,30])

        self.player_list.add_row([UILabel(0,0, "1"),UILabel(0,0, "Player 1"),UILabel(0,0, "50ms"),UILabel(0,0, "Canada")])
        #self.container = UIContainer(0, 0, 400, 1000, f"{base_path}\\assets\\UI\\Box03.png", border_size=23)
        #self.player_list = UIList(30, 30, list_width, 200, item_selected_callback = self.item_selected_callback)
        self.container.add_element(self.player_list)

    def item_selected_callback(self, item):
        pass

    def connect(self, host, port):
        self.connection = Connection(host=host, port=port, use_singleton=True)
        self.connection.connect_to_server()


    def update_player_list(self):
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False            
            self.container.handle_event(event)


    def update(self):
        pass
        
    def render(self):
        self.container.draw(self.screen)
        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.screen.fill((0,0,0))
            self.handle_input()
            self.update()
            self.render()

connect = ConnectToServer()
connect.run()
