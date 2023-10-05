import threading
from queue import Queue
from menu import MainMenu
from Game import StrategyGame
from BuildTeam import TeamBuilder
from instructions import Instructions
from PlankAndBall import PlankAndBall
from GraphicUI import UIMessageBox
import pygame
from Connection import Connection
from config import server_ip, server_port
class MainFrame():
    def __init__(self):
        self.init_graphics(True, False, None, 1500, 1280)
        self.msg_box = None
        self.connection = None
        self.waiting_for_match = False
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

    def listen_for_messages(self, connection):
        while connection.is_connected:
            command_type, data = connection.receive_command()
            self.incoming_messages.put((command_type, data))
            
            if command_type == "new_match_created":
                self.waiting_for_match = False
                
    def start_game(self, connection):
        team_builder = TeamBuilder(1, False, False, self.screen)
        selected_team1, selected_team2 = team_builder.run()
        game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
        game.game_loop()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running =  False
                if self.msg_box:
                    self.msg_box.handle_event(event)   

            if self.msg_box:
                self.msg_box.draw(self.screen)
            if self.waiting_for_match:
                pass
            else:
                main_menu = MainMenu(False, False, self.screen)
                selected_menu_item = main_menu.run()
                if selected_menu_item == "Single Player":
                    team_builder = TeamBuilder(1, False, False, self.screen)
                    selected_team1 = team_builder.run()
                    team_builder = TeamBuilder(2, False, False, self.screen)
                    selected_team2 = team_builder.run()
                    game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
                    game.game_loop()
                elif selected_menu_item == "Multi-Player":
                    #try:
                    self.connection = Connection(host=server_ip, port=server_port, use_singleton=True)
                    self.connection.sock.connect((server_ip, server_port))
                    self.connection.perform_handshake(is_server=False)
                    #except Exception as e:
                    #    self.msg_box = UIMessageBox("Could not connect to server", 500, 500)

                    if self.connection and self.connection.is_connected:
                        self.incoming_messages = Queue()
                        # Create a new thread for listening to messages
                        listener_thread = threading.Thread(target=self.listen_for_messages, args=(self.connection,))
                        listener_thread.daemon = True
                        listener_thread.start()                          
                        self.waiting_for_match = True
                    #    team_builder = TeamBuilder(1, False, False, self.screen)
                    #    selected_team1 = team_builder.run()                
                elif selected_menu_item == "Instructions":
                    instructions = Instructions(init_pygame=False, full_screen=False, screen=self.screen)
                    instructions.run()
                elif selected_menu_item == "Mini Game":
                    mini_game = PlankAndBall(init_pygame=False, full_screen=False, screen=self.screen)
                    mini_game.run_game()

                elif selected_menu_item == "Quit":
                    running = False

main = MainFrame()
main.run()
