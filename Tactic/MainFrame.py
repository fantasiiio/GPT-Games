import argparse
from Lobby import Lobby
import re
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
from UIConfigArmy import *

class MainFrame(UIManager):
    _instance = None
    def __init__(self):
        super().__init__()   
        MainFrame._instance = self     
        self.init_graphics(True, False, None, 1500, 1280)
        self.is_active = True
        self.connection = None
        self.waiting_for_match = False
        self.is_ai = False
        self.login_result = None
        self.current_screen = "Main Menu"
        UIManager.ui_settings = ui_settings_army

        self.lobby = Lobby(init_pygame=False, full_screen=False, screen=self.screen)
        self.main_menu = MainMenu(False, False, self.screen)
        self.instructions = Instructions(init_pygame=False, full_screen=False, screen=self.screen)
        self.init_UI()
        self.fake_user = None

        parser = argparse.ArgumentParser()
        parser.add_argument('-ai', type=int, default=None, help='Set the AI level.')
        args = parser.parse_args()
        if isinstance(args.ai, (int, float)):        
            self.fake_user = fake_users[args.ai]
            self.is_ai = True
            self.init_multiplayer()
            self.current_screen = "Main Menu"                

    def init_UI(self):
        UIManager.screen = self.screen
        self.add_child_manager(self.main_menu)
        self.main_menu.is_active = True
        self.main_menu.show()
        self.add_child_manager(self.lobby)
        self.lobby.is_active = False
        self.login_popup = UILoginPopup(0,0,0,0, screen=self.screen)
        self.msg_box = UIMessageBox(" ", 0, 0, screen=self.screen)
        self.display_Name_popup = DisplayNamePopup(0,0, screen=self.screen)
        self.add_container(self.display_Name_popup)
        self.add_container(self.login_popup)
        self.add_container(self.msg_box)


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
                result = json.loads(data)

                if command_type == "login":
                    message = result["message"]
                    if result["success"] == "positive":
                        self.login_result = True
                        #self.waiting_for_match = False
                        
                        user_settings["token"] = message["token"]
                        if not self.is_ai:
                            save_user_settings()
                        self.on_login_success()
                    else:
                        self.msg_box.show(f"Login failed:\n{message}")
                        self.login_result = False
                elif command_type == "new_match_created":
                    self.waiting_for_match = False
                elif command_type == "token":
                    message = result["message"]
                    user = message["user"]
                    if result["success"] == "positive":
                        if "display_name" in user and user["display_name"]:
                            self.display_Name_popup.name_field.deserialize(user["display_name"])
                        self.on_login_success()
                    else:
                        self.msg_box.show(result["message"], self.token_failed_message_ok)
                elif command_type =="display_name":
                    if result["success"] == "positive":
                        # save display_name in player.json 
                        if not self.is_ai:                                           
                            save_user_settings()                                    
                        self.current_screen = "Lobby"
                        self.lobby.is_active = True
                        self.main_menu.is_active = False
                        self.connection.send_command("get_users_list", "system", data=None)
                    else:
                        self.msg_box.show(message)
                elif command_type == "users_list":
                    if result["success"] == "positive":
                        self.lobby.update_player_list(result["message"])
                elif command_type == "register":
                    if result["success"] == "positive":
                        self.msg_box.show("Registration successful. \nPlease check your email for the activation link.")
                    else:
                        self.msg_box.show(result["message"])
                elif command_type == "user_connected":
                    self.lobby.add_player(result["message"])
                elif command_type == "user_disconnected":
                    guid = result["message"]
                    self.lobby.remove_player(guid)

            except Exception as e:
                print(f"Error receiving command: {e}")
                self.msg_box.show("Login failed")
                self.waiting_for_match = False
                connection.close()
                return
                
    def on_login_success(self):
        self.login_result = True
        #self.msg_box.show("Login successful")
        print("Login successful")
        self.display_Name_popup.show(self.main_menu.menu_container.rect.bottom + 20)
    
    def token_failed_message_ok(self, button):
        self.msg_box.ok_callback = None
        self.login_result = False
        self.login_popup.show(self.main_menu.menu_container.rect.bottom + 20)


    def start_game(self, connection):
        team_builder = TeamBuilder(1, False, False, self.screen)
        selected_team1, selected_team2 = team_builder.run()
        game = StrategyGame(selected_team1, selected_team2, False, False, self.screen)
        game.game_loop()


    def init_multiplayer(self):
        token = None
        if self.fake_user:
            self.email = self.fake_user["email"]
            self.password = self.fake_user["password"]
        else:
            if "token" in user_settings:
                token = user_settings["token"]
            if "email" in user_settings: 
                self.email = user_settings["email"]
            if "password" in user_settings: # Don't store password in user_settings, for debugging purposes;p
                self.password = user_settings["password"]

        self.login_popup.email_field.set_text(self.email)
        self.login_popup.password_field.set_text(self.password)

        try:
            self.connection = Connection(host=server_ip, port=server_port)._last_instance
            self.connection.connect_to_server()
            if token:
                self.connection.send_command("token", "system", data=token)
            else:
                self.login_popup.show(self.main_menu.menu_container.rect.bottom + 20)
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
            UITextBox.mouse_over_textbox = False
            UIButton.mouse_over_button = False

            events_list = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running =  False
                    return
                self.handle_event(event)
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
                        elif(selected_menu_item == "Quit"):       
                            self.running =  False
                            return
                        self.main_menu.selected_menu_item = None                                                         
                        

            if self.waiting_for_match:
                pass


            self.draw(self.screen)

            
            if UITextBox.mouse_over_textbox:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            elif UIButton.mouse_over_button:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)



            pygame.display.flip()

class UILoginPopup(UIPopupBase):
    def __init__(self, x, y, width, height, screen):
        super().__init__(x, y, "LOGIN", screen, ok_callback=self.login_button_clicked)
        self.return_result = None
        self.connection = Connection._last_instance
        self.screen = screen
        self.rect = pygame.Rect(x, y, width, height)#

        # Add labels
        self.email_label = UILabel(10, 20, "Email:", font_size=30, text_color=(255,255,255))
        self.password_label = UILabel(10, 110, "Password:", font_size=30, text_color=(255,255,255))
        input_width = 300
        # Shift text fields down to make more room for labels
        self.email_field = UITextBox(10, 50, input_width, 40, font_size=30)
        self.password_field = UITextBox(10, 140, input_width, 40, font_size=30, is_password_field=True)
        
        self.email_error_label = UILabel(10, self.email_field.rect.bottom, "", font_size=20, text_color=(255, 0, 0))
        #self.password_strength_label = UILabel(10, self.password_field.rect.bottom, "", font_size=20, text_color=(255, 0, 0))
        self.password_strength_bar = UIProgressBar(10, self.password_field.rect.bottom + 5, input_width, 10, max_squares_per_row=5, max_value=5)
        self.password_error_label = UILabel(10, self.password_strength_bar.rect.bottom, "", font_size=20, text_color=(255, 0, 0))

        self.ok_button.text="LoginRegister"
        self.ok_button.set_image(f"{base_path}\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Icons\\Login.png")
        # Add the Cancel button to the container in the __init__ method
        self.inner_container.add_element(self.password_strength_bar)
        self.inner_container.add_element(self.email_error_label)
        self.inner_container.add_element(self.password_error_label)
        self.inner_container.add_element(self.email_label)
        self.inner_container.add_element(self.password_label)
        self.inner_container.add_element(self.email_field)
        self.inner_container.add_element(self.password_field)
        self.inner_container.adjust_to_content()
        self.adjust_to_content()

    def cancel_button_clicked(self, button):
        self.cancel_login()

    def cancel_login(self):
        self.hide()  # This will hide the popup
        self.return_result = False 

    def login_button_clicked(self, button):
        self.perform_login()

    def validate_email(self, email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def password_strength(self, password):
        # Initialize variables
        strength = {'score': 0, 'message': 'Very Weak'}

        # Check length
        if len(password) >= 8:
            strength['score'] += 1

        # Check for digits
        if re.search(r"\d", password):
            strength['score'] += 1

        # Check for lowercase
        if re.search(r"[a-z]", password):
            strength['score'] += 1

        # Check for uppercase
        if re.search(r"[A-Z]", password):
            strength['score'] += 1

        # Check for special characters
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            strength['score'] += 1

        # Verify overall score
        if strength['score'] == 5:
            strength['message'] = 'Very Strong'
        elif strength['score'] == 4:
            strength['message'] = 'Strong'
        elif strength['score'] == 3:
            strength['message'] = 'Medium'
        elif strength['score'] == 2:
            strength['message'] = 'Weak'
        else:
            strength['message'] = 'Very Weak'

        return strength

    def draw_password_strength_bar(self):
        strength = self.password_strength(self.password_field.text)
        if(strength["score"] < 3):
            self.password_strength_bar.color1 = (255, 0, 0)
        else:
            self.password_strength_bar.color1 = (0, 255, 0)
        self.password_strength_bar.current_value = strength["score"]
    

    def draw(self, screen):
        self.draw_password_strength_bar()
        super().draw(screen)

    def perform_login(self):
        self.connection = Connection._last_instance        
        email = self.email_field.text
        password = self.password_field.text

        if not self.validate_email(email):
            self.email_error_label.set_text("Invalid email address")  # Update UILabel
            return
        else:
            self.email_error_label.set_text("") 

        strength = self.password_strength(password)
        if strength["score"] < 3:
            self.password_error_label.set_text("Password not strong enough")
            return
        else:
            self.password_error_label.set_text("")             

        # Perform login logic here
        data={"email": email, "password": password}
        self.connection.send_command(command_type="login", receiver="system", data=data)
        self.hide()
        self.return_result = True
    
    def show(self, y):
        super().show(y)
        if MainFrame._instance.is_ai:
            self.perform_login()

        


class DisplayNamePopup(UIPopupBase):
    def __init__(self, x, y, screen=None):
        super().__init__(x, y, screen=screen, padding_header = 0)
        self.connection = Connection._last_instance
        self.name_label = UILabel(0,0, "Display Name:", font_size=25)
        self.name_label.original_y = 100
        self.name_field = UITextBox(0, 30, 350, 40, font_size=30, enable_color_picker=True)
        self.name_field.create_tooltip("Select text and choose color")

        self.inner_container.add_element(self.name_label)
        self.inner_container.add_element(self.name_field)
        self.inner_container.id = "InnerContainer"
        self.adjust_to_content()
        self.id = "DisplayNamePopup"
        

    def ok_button_clicked(self, button):
        self.connection = Connection._last_instance
        display_name = self.name_field.serialize()
        data = {"display_name": display_name,
                "email": user_settings["email"]
                }
        self.connection.send_command(command_type="display_name", receiver="system", data=data)
        self.hide()

    def show(self, position_y=None):
        super().show(position_y)
        if MainFrame._instance.is_ai:
            self.name_field.text = MainFrame._instance.fake_user["display_name"]
            self.ok_button_clicked(None)

main = MainFrame()
main.run()
