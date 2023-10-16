from GraphicUI import UIContainer, UILabel
import pygame
from config import base_path



class Instructions:
    def __init__(self, file_path =  f"{base_path}\\data\\instructions.md", init_pygame=True, full_screen=False, screen=None):
        self.init_graphics(init_pygame, full_screen, screen, 1000, 1000)

        self.file_path = file_path
        self.container = UIContainer(0, 0, self.screen_width, self.screen_height, color=(50, 50, 50))
        self.init_instructions()

    def read_md_file(self):
        with open(self.file_path, 'r') as f:
            lines = f.readlines()
        return lines

    def parse_md_to_container(self):
        lines = self.read_md_file()
        y_offset = 10  # Starting y-position for the first label
        for line in lines:
            font_size = 30  # Default font size
            text_color = (255, 255, 255)  # Default text color (white)
            
            # Handle headers
            if line.startswith("### "):
                font_size = 40
                line = line[4:].strip()
            elif line.startswith("## "):
                font_size = 50
                line = line[3:].strip()
            elif line.startswith("# "):
                font_size = 60
                line = line[2:].strip()

            line = self.wrap_text_to_pixel_width(line, pygame.font.SysFont(None, font_size), self.screen_width - 60)            
                
            # Create a UILabel and add it to the container
            label = UILabel(10, y_offset, line, self.container, font_size=font_size, text_color=text_color)
            self.container.add_element(label)
            
            y_offset += label.rect.height + 10

    def init_instructions(self):
        self.parse_md_to_container()

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

    def wrap_text_to_pixel_width(self, text, font, max_width):
        paragraphs = text.split('\n')
        wrapped_paragraphs = []

        for paragraph in paragraphs:
            words = paragraph.split(' ')
            lines = []
            current_line = []
            current_line_width = 0

            for word in words:
                word_width, _ = font.size(word)
                space_width, _ = font.size(' ')

                if current_line_width + word_width + (len(current_line) - 1) * space_width > max_width:
                    lines.append(' '.join(current_line))
                    current_line = []
                    current_line_width = 0

                current_line.append(word)
                current_line_width += word_width

            lines.append(' '.join(current_line))

            # Add tab only to lines after the first one in each paragraph
            wrapped_paragraph = '\n'.join(lines)
            wrapped_paragraphs.append(wrapped_paragraph)

        wrapped_text = '\n'.join(wrapped_paragraphs)
        return wrapped_text
        
    def simulate_tab(self, text, tab_size=4):
        return text.replace("\t", " " * tab_size)            

    def run_frame(self, events_list):
        events_list = pygame.event.get() if events_list is None else events_list        
        for event in events_list:
            if event.type == pygame.QUIT:
                running = False
            self.container.handle_event(event)
        
        self.container.draw(self.screen)
        pygame.display.flip()


    def run(self):
        self.running = True
        while self.running:
            self.run_frame()


# Run the game
if __name__ == "__main__":
    instructions = Instructions()
    instructions.run()
