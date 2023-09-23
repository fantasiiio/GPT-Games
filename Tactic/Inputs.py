import pygame

class Inputs:
    def __init__(self):
        self.mouse = self.MouseInput()
        self.keyboard = self.KeyboardInput()

    class MouseInput:
        def __init__(self):
            self.pos = (0, 0)
            self.button = [False, False, False]  # Left, Middle, Right
            self.clicked = [False, False, False]
            self.ignore_next_click = False
        def update(self):
            self.pos = pygame.mouse.get_pos()
            buttons = pygame.mouse.get_pressed()
            for button in range(len(buttons)):
                self.clicked[button] = False
                if not self.ignore_next_click and not self.button[button] and buttons[button]:
                    # Button was just pressed
                    self.clicked[button] = True
                if self.button[button] and not buttons[button]:
                    # Button was just released
                    self.ignore_next_click = False
            self.button = [bool(button) for button in buttons]
            #print(f"{self.clicked[0]},{self.button[0]}")            

    class KeyboardInput:
        def __init__(self):
            self.key = {}
            self.clicked = {}

        def key_pressed(self, key_constant):
            if not key_constant in self.key:
                return False
            return self.key[key_constant]

        def update(self):
            keys = pygame.key.get_pressed()
            all_keys = [attr for attr in dir(pygame) if attr.startswith("K_")]

            for key_attr in all_keys:
                key_constant = getattr(pygame, key_attr)
                self.clicked[key_constant] = False
                if self.key_pressed(key_constant) and keys[key_constant]:
                    # Key was just pressed
                    self.clicked[key_constant] = True
                self.key[key_constant] = keys[key_constant]

    def update(self):
        self.mouse.update()
        self.keyboard.update()