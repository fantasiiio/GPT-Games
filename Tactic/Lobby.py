import pygame
from Connection import Connection
from GraphicUI import *
from config import *
from UIConfigArmy import *

class Lobby(UIManager):
    def __init__(self, init_pygame=True, full_screen=False, screen=None):
        super().__init__()
        self.init_graphics(init_pygame, full_screen, screen, 1500,1200)
        self.init_UI()
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
            self.screen_width = width
            self.screen_height = height
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

    def init_UI(self):
        UIManager.ui_settings = ui_settings_army
        padding=10
        screen_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
        list_width = 400
        bottom_container_height = 70
        self.bottom_container = UIContainer(10, self.screen.get_height() - bottom_container_height -padding, self.screen.get_width()- padding*2, 70, f"{base_path}\\assets\\UI-v2\\Window\\Window_small.png", border_size=24, padding=10)
        self.container = UIContainer(0, 0, 0, 0, "", border_size=0, padding=0, color=(0,0,0,0))
        ready_button = UIButton(0,0, 100, 50, "Ready")
        self.bottom_container.add_element(ready_button)
        self.player_list = UIList(0, 200, AUTO, 700, num_columns=4, column_widths=[80, 250, 50, 50, 70], headers=['Win/Loose', 'Name','Status', 'Ping', 'Country'], header_font_size=20)
        row_height = 30
        # for i in range(20):
        #     image = UIImage(20,0, image=get_country_image("CA"))
        #     wins_label = UILabel(0,0, f"10/0", font_size=20)
        #     progress = UIProgressBar(0,0, 40, 15, 5, max_value=5)
        #     progress.current_value = 3
        #     name_label = UILabel(0,0, f"Player {i}", font_size=30)
        #     self.list2.add_row([wins_label,name_label,progress, image])

        delta_x = (self.screen_width - 10) - self.player_list.rect.right
        delta_y = (self.screen_height - 10 - bottom_container_height - 10) - self.player_list.rect.bottom
        self.player_list.move_by_offset(delta_x, delta_y)

        mini_map = UIImage(0,10, image=f"",backgroung_image= f"{base_path}\\assets\\UI-v2\\Window\\Window.png", border_size=80)
        mini_map.rect.width = self.player_list.rect.width
        delta_x = (self.screen_width - 10) - mini_map.rect.width
        mini_map.rect.x += delta_x
        mini_map.rect.height = self.screen_height - (self.player_list.rect.bottom - self.player_list.header.rect.top + bottom_container_height + 10) - 30
        self.container.add_element(self.bottom_container)
        self.container.add_element(mini_map)

        self.container.add_element(self.player_list)
        self.add_container(self.container)

    def update_player_list(self, player_list):
        self.player_list.clear_rows()
        for player in player_list:
            self.add_player(player)

    def add_player(self, player):
        image = UIImage(20,0, image=get_country_image("CA"))
        wins_label = UILabel(0,0, f"10/0", font_size=20)
        progress = UIProgressBar(0,0, 40, 15, 5, max_value=5)
        progress.current_value = 3
        name_label = UILabel(0,0, f"{player['display_name']}", font_size=20)
        self.player_list.add_row([wins_label,name_label,progress, image], player)

    def remove_player(self, guid):
        row_index = self.player_list.find_row_index_by_data("guid", guid)
        if row_index is not None:
            self.player_list.remove_row(row_index)            
        #for player in player_list:

    def handle_input(self, events_list=None):
        events_list = pygame.event.get() if events_list is None else events_list
        for event in events_list:
            if event.type == pygame.QUIT:
                self.running = False     
        
            #self.list.handle_event(event)
            self.player_list.handle_event(event)

    def update(self):
        pass
        
    def render(self):
        self.draw(self.screen)
        #self.list2.draw(self.screen)
        pygame.display.flip()

    def run_frame(self, events_list=None):
        self.handle_input(events_list)
        self.update()
        self.render()

    def run(self):
        while self.running:
            self.screen.fill((60, 60, 60))
            self.run_frame()
        if self.init_pygame:
            pygame.quit()

if __name__ == '__main__':
    connect = Lobby()
    connect.run()
