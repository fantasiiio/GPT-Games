import pygame
from GraphicUI import *
import json

class GuiGameScreenEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        
        # UIContainer to hold all elements
        self.container = UIContainer(0, 0, 800, 600)
        
        # Selected element
        self.selected_element = None
        
    def add_element(self, element):
        self.container.add_element(element)
        
    def delete_element(self, element):
        if element in self.container.elements:
            self.container.remove_element(element)
        
    def move_element(self, element, dx, dy):
        if element in self.container.elements:
            element.rect.x += dx
            element.rect.y += dy
            
    def save_layout(self, filename):
        layout = []
        for element in self.container.elements:
            # Serialize the element properties into a dictionary
            element_dict = {"class": type(element).__name__,
                            "x": element.rect.x,
                            "y": element.rect.y,
                            "width": element.rect.width,
                            "height": element.rect.height}
            layout.append(element_dict)
            
        with open(filename, "w") as file:
            json.dump(layout, file)
            
    def load_layout(self, filename):
        self.container.elements = []
        
        with open(filename, "r") as file:
            layout = json.load(file)
            
        for element_dict in layout:
            # Create an instance of the element class and add to the container
            if element_dict["class"] == "UIButton":
                element = UIButton(element_dict["x"], element_dict["y"], element_dict["width"], element_dict["height"])
            elif element_dict["class"] == "UITextBox":
                element = UITextBox(element_dict["x"], element_dict["y"], element_dict["width"], element_dict["height"])
            # Add other UIElement subclasses as needed
            self.container.add_element(element)
            
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for element in self.container.elements:
                        if element.rect.collidepoint(event.pos):
                            self.selected_element = element
                            break
                elif event.type == pygame.MOUSEMOTION and self.selected_element is not None:
                    self.selected_element.rect.x += event.rel[0]
                    self.selected_element.rect.y += event.rel[1]
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.selected_element = None
                        
                if event.type == pygame.KEYDOWN:
                    # Move selected element with arrow keys
                    if self.selected_element:
                        if event.key == pygame.K_UP:
                            self.move_element(self.selected_element, 0, -1)
                        elif event.key == pygame.K_DOWN:
                            self.move_element(self.selected_element, 0, 1)
                        elif event.key == pygame.K_LEFT:
                            self.move_element(self.selected_element, -1, 0)
                        elif event.key == pygame.K_RIGHT:
                            self.move_element(self.selected_element, 1, 0)
                        
                    # Add a button with B key
                    if event.key == pygame.K_b:
                        button = UIButton(0, 0, 100, 30, "Button")
                        self.container.add_element(button)
                        
                    # Save layout with S key
                    if event.key == pygame.K_s:
                        self.save_layout("layout.json")
                        
                    # Load layout with L key
                    if event.key == pygame.K_l:
                        self.load_layout("layout.json")
                        
                    # Delete selected element with Delete key
                    if event.key == pygame.K_DELETE:
                        if self.selected_element:
                            self.container.remove_element(self.selected_element)
                            self.selected_element = None
                
                # Pass the event to the container
                self.container.handle_event(event)
            
            # Draw the container and its elements
            self.container.draw(self.screen)
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    editor = GuiGameScreenEditor()
    editor.run()

    import pygame
from GraphicUI import *

