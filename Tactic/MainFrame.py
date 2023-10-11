import threading
from queue import Queue
from menu import MainMenu
from Game import StrategyGame
from BuildTeam import TeamBuilder
from instructions import Instructions
from PlankAndBall import PlankAndBall
from GraphicUI import *
import pygame
from Connection import *
from config import *
import sys

class MainFrame():
    def __init__(self):
        self.init_graphics(True, False, None, 1500, 1280)
        self.msg_box = UIMessageBox(" ", 0, 0, image=f"{base_path}\\assets\\UI\\Box03.png", border_size=23, padding=20, screen=self.screen)
        self.connection = None
        self.waiting_for_match = False
        self.is_ai = False
        self.login_result = None
        self.current_screen = "Main Menu"
        self.main_menu = MainMenu(False, False, self.screen)
        self.instructions = Instructions(init_pygame=False, full_screen=False, screen=self.screen)
        popup_width = 200
        popup_height = 300
        self.login_popup = UILoginPopup(self.screen_width / 2 - popup_width / 2, self.screen_height / 2 - popup_height / 2 + 100, popup_width, popup_height, screen=self.screen)

        popup_width = 270
        popup_height = 350
        self.register_popup = UIRegistrationPopup(self.screen.get_rect().width / 2 - popup_width / 2 , self.screen.get_rect().height / 2 - popup_height / 2 + 100, popup_width, popup_height, screen=self.screen)


        for i, arg in enumerate(sys.argv[1:]):
            if arg=="-ai":
                self.is_ai = True

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
            try:
                command_type, receiver, data = connection.receive_command()
                self.incoming_messages.put((command_type, data))

                if command_type == "login":
                    result = json.loads(data)
                    if result["success"] == "positive":
                        self.login_result = True
                        #self.waiting_for_match = False
                        message = result["message"]
                        user_settings["token"] = message
                        save_user_settings()
                        print("Login successful")
                    else:
                        self.msg_box.show("Login failed")
                        self.login_result = False
                elif command_type == "new_match_created":
                    self.waiting_for_match = False
                elif command_type == "token":
                    result = json.loads(data)
                    if result["success"] == "positive":
                        self.login_result = True
                        print("Login successful")
                    else:
                        self.msg_box.show("Login failed")
                        self.login_result = False
            except Exception as e:
                print("Error receiving command: ")
                self.msg_box.show("Login failed")
                self.waiting_for_match = False
                connection.close()
                return
                
    def start_game(self, connection):
        team_builder = TeamBuilder(1, False, False, self.screen)
        selected_team1, selected_team2 = team_builder.run()
        game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
        game.game_loop()


    def init_multiplayer(self):
        token = None
        if "token" in user_settings:
            token = user_settings["token"]
        if "username" in user_settings: 
            self.username = user_settings["username"]
        if "password" in user_settings: # Don't store password in user_settings, for debugging purposes;p
            self.password = user_settings["password"]
        try:
            self.connection = Connection(host=server_ip, port=server_port, use_singleton=True)._instance
            self.connection.connect_to_server()
            if token:
                self.connection.send_command("token", "system", data=token)
            else:
                self.login_popup.show()
        except Exception as e:
            self.msg_box.show("Could not connect to server")

        if self.connection and self.connection.is_connected:
            self.incoming_messages = Queue()
            # Create a new thread for listening to messages
            listener_thread = threading.Thread(target=self.listen_for_messages, args=(self.connection,))
            listener_thread.daemon = True
            listener_thread.start()                           
            self.waiting_for_match = True
            #team_builder = TeamBuilder(1, False, False, self.screen)

        self.login_popup.username_field.set_text(self.username)
        self.login_popup.password_field.set_text(self.password)


    def multiplayer(self):
        while self.waiting_for_match:

            if self.return_result:
                self.waiting_for_match = False                
            else:
                #self.running 
                self.msg_box.show("Login failed")
                self.waiting_for_match = False



    def get_screen_by_name(self, name):
        if name == "Main Menu":
            return self.main_menu
        elif name == "Instructions":
            return self.instructions
        elif name == "Single Player":
            return self.game

    def run(self):
        self.running = True
        events_list = []
        while self.running:
            self.screen.fill((0,0,0))
            if self.is_ai:
                self.multiplayer()
            else:
                events_list = []
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        self.running =  False
                        return
                    events_list.append(event)


                if(self.current_screen == "Main Menu"):
                        selected_menu_item = self.main_menu.run_frame(events_list)
                        if selected_menu_item:
                            if(selected_menu_item == "Instructions"):
                                self.current_screen = selected_menu_item
                                screen = self.instructions
                                screen.running = True
                            elif(selected_menu_item == "Multi-Player"):
                                self.init_multiplayer()
                                self.current_screen = "Main Menu"
                                #   

                            self.main_menu.selected_menu_item = None                                                         
                            
                elif(self.current_screen == "Instructions"): 
                    running = self.instructions.run_frame(events_list)
                    if not running:
                        self.current_screen = "Main Menu"
                elif(self.current_screen == "TeamBuilder"):
                    selected_team = self.team_builder.run_frame(events_list)
                    if selected_team:
                        self.current_screen = "Game"
                        #self.game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
                        #self.game.game_loop()


                if self.waiting_for_match:
                    pass
                if self.login_popup and self.login_popup.running:                    
                    result = self.login_popup.run_frame(events_list)
                    if result:
                        if result == "register":
                            self.register_popup.running = True
                if self.register_popup and self.register_popup.running:
                    result = self.register_popup.run_frame(events_list)

            if(self.msg_box.is_visible):
                self.msg_box.handle_event(event)   
                self.msg_box.draw(self.screen)
            pygame.display.flip()



class UIRegistrationPopup:
    def __init__(self, x, y, width, height, screen):
        self.hide()
        self.return_result = None
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)
        self.container = UIContainer(x, y, width, height, f"{base_path}\\assets\\UI\\Box03.png", border_size=23, padding=40)

      
        # Add labels with padding
        self.email_label = UILabel(10, 20, "Email:", font_size=30, text_color=(255,255,255))
        self.username_label = UILabel(10, 90, "Username:", font_size=30, text_color=(255,255,255))
        self.password_label = UILabel(10, 160, "Password:", font_size=30, text_color=(255,255,255))

        # Add text fields with padding
        self.email_field = UITextBox(10, 50, 250, 40, font_size=30)
        self.username_field = UIColoredTextBox(10, 120, 250, 40, font_size=30)
        self.password_field = UITextBox(10, 190, 250, 40, font_size=30, is_password_field=True)

        # Add register button with padding
        self.register_button = UIButton(10, 250, 250, 40, text="Register", font_size=30, callback=self.register_button_clicked)

        self.container.add_element(self.email_label)
        self.container.add_element(self.username_label)
        self.container.add_element(self.password_label)
        self.container.add_element(self.email_field)
        self.container.add_element(self.username_field)
        self.container.add_element(self.password_field)
        self.container.add_element(self.register_button)
        self.container.adjust_to_content()
        header_height = 50
        self.header = UIHeader(self.container.rect.x, self.container.rect.top - header_height, self.container.rect.width, header_height, ["Register"], [width], pygame.font.Font(None, 40), image=f"{base_path}\\assets\\UI\\Box03.png", horizontal_align="center")

        self.connection = Connection._instance

    def register_button_clicked(self, button):
        self.hide()
        self.perform_registration()

    def perform_registration(self):
        email = self.email_field.text
        username = self.username_field.text
        password = self.password_field.text
        self.connection.send_command(command_type="register", receiver="system", data={"username": username, "password": password, "email": email})
        self.return_result = True  # or False, based on whether registration is successful

    def handle_event(self, event):
        self.container.handle_event(event)

    def draw(self, screen):
        self.container.draw(self.screen)
        self.header.draw(self.screen)        
        pygame.display.flip()

    def handle_input(self, events_list):
        events_list = pygame.event.get() if events_list is None else events_list        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.hide()
            self.handle_event(event)

    def show(self):
        self.running = True
        self.return_result = None    

    def hide(self):
        self.running = False            

    def run_frame(self, events_list=None):
        self.handle_input(events_list)
        self.draw(self.screen)
        return self.return_result
    
    def run(self):
        self.running = True
        while self.running:
            self.handle_input(None)
            self.draw(self.screen)
        return self.return_result

class UILoginPopup:
    def __init__(self, x, y, width, height, screen, main_frame=None):
        self.hide()
        self.return_result = None
        self.connection = Connection._instance
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)#
        self.container = UIContainer(x, y, width, height, f"{base_path}\\assets\\UI\\Box03.png", border_size=23, padding=40)

        padding = 40
        # Add labels
        self.username_label = UILabel(10, 20, "Username:", font_size=30, text_color=(255,255,255))
        self.password_label = UILabel(10, 90, "Password:", font_size=30, text_color=(255,255,255))
        
        # Shift text fields down to make more room for labels
        self.username_field = UITextBox(10, 50, 180, 40, font_size=30)
        self.password_field = UITextBox(10, 120, 180, 40, font_size=30, is_password_field=True)
        
        self.login_button = UIButton(10, 180, 180, 40, text="Login", font_size=30, callback=self.login_button_clicked, trigger_key=pygame.K_RETURN)
        self.register_button = UIButton(10, 230, 180, 40, text="Register", font_size=30, callback=self.register_button_clicked)

        self.container.add_element(self.register_button)
        self.container.add_element(self.username_label)
        self.container.add_element(self.password_label)
        self.container.add_element(self.username_field)
        self.container.add_element(self.password_field)
        self.container.add_element(self.login_button)
        self.container.adjust_to_content()
        header_height = 50
        self.header = UIHeader(self.container.rect.x, self.container.rect.top - header_height, self.container.rect.width, header_height, ["Login"], [width], pygame.font.Font(None, 40), image=f"{base_path}\\assets\\UI\\Box03.png", horizontal_align="center")
        self.connection = Connection._instance


    def register_button_clicked(self, button):
        self.hide()
        self.return_result = "register"

    def login_button_clicked(self, button):
        self.perform_login()

    def handle_event(self, event):
        self.container.handle_event(event)


    def perform_login(self):
        self.connection = Connection._instance        
        username = self.username_field.text
        password = self.password_field.text
        # Perform login logic here
        data={"username": username, "password": password}
        self.connection.send_command(command_type="login", receiver="system", data=data)
        self.hide()
        self.return_result = True

    def draw(self, screen):
        self.container.draw(self.screen)
        self.header.draw(self.screen)        
        #pygame.display.flip()         

    def handle_input(self, events_list):
        events_list = pygame.event.get() if events_list is None else events_list        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.hide()   

            self.handle_event(event)  

    def hide(self):
        self.running = False

    def show(self):
        #self.password_field.text = ""
        self.running = True
        self.return_result = None

    def run_frame(self, events_list=None):
        self.handle_input(events_list)
        self.draw(self.screen)
        return self.return_result


    def run(self):
        self.running = True
        while self.running:
            self.handle_input()
            self.draw(self.screen)
        return self.return_result

main = MainFrame()
main.run()
