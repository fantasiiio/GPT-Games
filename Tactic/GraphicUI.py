import pygame

class UIElement:
    def __init__(self, x, y, width, height, parent = None,image=None, color=(200, 200, 200), border_size=10):
        self.image = None if not image else pygame.image.load(image)  # Replace with the path to your button image
        self.color = color
        self.border_size = border_size
        self.parent = parent
        if parent:
            self.rect = pygame.Rect(x + parent.rect.x, y + parent.rect.x, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)

    def set_parent(self, parent):
        self.parent = parent
        self.rect.x += parent.rect.x
        self.rect.y += parent.rect.y

    def draw(self, screen):
        if self.image:
            self.draw_9_slice(screen)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    def draw_9_slice(self, screen):
        border = self.border_size
        source_inner_width = self.image.get_width() - 2*border
        source_inner_height = self.image.get_height() - 2*border

        dest_inner_width = self.rect.width - 2*border
        dest_inner_height = self.rect.height - 2*border

        # Corners
        screen.blit(self.image.subsurface((0, 0, border, border)), (self.rect.x, self.rect.y))
        screen.blit(self.image.subsurface((self.image.get_width()-border, 0, border, border)), (self.rect.x + self.rect.width - border, self.rect.y))
        screen.blit(self.image.subsurface((0, self.image.get_height()-border, border, border)), (self.rect.x, self.rect.y + self.rect.height - border))
        screen.blit(self.image.subsurface((self.image.get_width()-border, self.image.get_height()-border, border, border)), (self.rect.x + self.rect.width - border, self.rect.y + self.rect.height - border))

        # Edges
        # Top
        screen.blit(pygame.transform.scale(self.image.subsurface((border, 0, source_inner_width, border)), (dest_inner_width, border)), (self.rect.x + border, self.rect.y))
        # Bottom
        screen.blit(pygame.transform.scale(self.image.subsurface((border, self.image.get_height()-border, source_inner_width, border)), (dest_inner_width, border)), (self.rect.x + border, self.rect.y + self.rect.height - border))
        # Left
        screen.blit(pygame.transform.scale(self.image.subsurface((0, border, border, source_inner_height)), (border, dest_inner_height)), (self.rect.x, self.rect.y + border))
        # Right
        screen.blit(pygame.transform.scale(self.image.subsurface((self.image.get_width()-border, border, border, source_inner_height)), (border, dest_inner_height)), (self.rect.x + self.rect.width - border, self.rect.y + border))

        # Center
        screen.blit(pygame.transform.scale(self.image.subsurface((border, border, source_inner_width, source_inner_height)), (dest_inner_width, dest_inner_height)), (self.rect.x + border, self.rect.y + border))


class UIButton(UIElement):
    def __init__(self, x, y, width, height, text, font, image=None, parent=None,color=(100, 100, 100), border_size=10, text_color=(0,0,0), hover_text_color=(255, 255, 255), callback=None):
        super().__init__(x, y, width, height, parent, image, color, border_size)
        self.text = text
        self.font = font
        self.text_color = text_color
        self.normal_text_color = text_color
        self.hover_text_color = hover_text_color
        self.callback = callback
        self.is_hovered = False

    def draw(self, screen):
        super().draw(screen)
        
        # Draw the button text
        if not self.font:
            return
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, (text_rect.topleft[0], text_rect.topleft[1]))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the button was clicked
            if self.rect.collidepoint(event.pos):
                # If there's a callback, call it
                if self.callback:
                    self.callback()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.is_mouse_is_over(event.pos):
                if not self.is_hovered:  # If the button was not already hovered
                    self.is_hovered = True
                    self.on_hover()
            else:
                if self.is_hovered:  # If the button was hovered previously
                    self.is_hovered = False
                    self.on_unhover()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Adjust the mouse position for the parent's position (and scroll position, if applicable)
            if self.is_mouse_is_over(event.pos):
                if self.callback:
                    self.callback(self)

    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
        # if self.parent:
        #     adjusted_mouse_pos[0] -= self.parent.rect.x
        #     adjusted_mouse_pos[1] -= self.parent.rect.y
            
        #     # If the parent is scrollable, adjust for its scroll position
        #     if isinstance(self.parent, ScrollableUIPanel):
        #         adjusted_mouse_pos[1] += self.parent.scroll_pos
        
        collide = self.rect.collidepoint(adjusted_mouse_pos)
        return collide

    def on_hover(self):
        if not self.font:
            self.color = self.normal_text_color
        else:
            self.text_color = self.hover_text_color  # Changing text to white for example
            self.text_surface = self.font.render(self.text, True, self.text_color)

    def on_unhover(self):
        if not self.font:
            self.color = self.normal_text_color
        else:
            # Resetting any changes made during hovering
            self.text_color = self.normal_text_color  # Changing text back to black
            self.text_surface = self.font.render(self.text, True, self.text_color)


class UIPanel(UIElement):
    def __init__(self, x, y, width, height, image=None, color=(100, 100, 100), border_size=10):
        super().__init__(x, y, width, height, None, image, color, border_size)
        self.elements = []  # List to hold child UI elements

    def add_element(self, element):
        """Add a UI element to the panel."""
        # Adjust the position of the element relative to the panel
        # element.rect.x += self.rect.x
        # element.rect.y += self.rect.y
        element.set_parent(self)  # Set the element's parent to this panel
        self.elements.append(element)
        self.content_height = self.get_elements_height()

    def remove_element(self, element):
        """Remove a UI element from the panel."""
        if element in self.elements:
            self.elements.remove(element)
            self.content_height = self.get_elements_height()

    def draw(self, screen):
        super().draw(screen)  # Draw the panel itself

        # Draw child elements
        for element in self.elements:
            element.draw(screen)

    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)

    def get_elements_height(self):
        """Get the total height of all child elements."""
        return sum([element.rect.height for element in self.elements])

class ScrollHandle():
    def __init__(self, x, y, width, height, parent_panel, image=None, color=(50, 50, 50), border_size=10):
        self.rect = pygame.Rect(x, y, width, height)
        #super().__init__(x, y, width, height, "", None, image, color, border_size)
        self.parent = parent_panel
        

    def draw(self, screen):
        # Adjust the scrollbar handle size based on the content size
        handle_height = self.rect.height#self.rect.height * (self.rect.height / self.parent_panel.content_height)
        handle_pos = (self.rect.x, self.rect.y + (self.parent.scroll_pos / self.parent.content_height) * self.rect.height)
        
        # Draw the scrollbar background
        #super().draw(screen)
        
        # Draw the scrollbar handle
        pygame.draw.rect(screen, (150, 150, 150), (handle_pos[0], handle_pos[1], self.rect.width, handle_height))

    def handle_event(self, event):
        pass


class ScrollableUIPanel(UIPanel):
    def __init__(self, x, y, width, height, image=None, color=(100, 100, 100), border_size=10):
        super().__init__(x, y, width, height, image, color, border_size)
        
        self.scroll_pos = 0  
        self.scroll_speed = 10  
        
        # Create the embedded scrollbar
        scrollbar_width = 20
        self.scrollbar = ScrollHandle(self.rect.right - scrollbar_width, y, scrollbar_width, 20, self)

    def handle_event(self, event):
        super().handle_event(event)
        # Handle scrolling events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_pos = max(self.scroll_pos - self.scroll_speed, 0)
            elif event.button == 5:
                self.scroll_pos = min(self.scroll_pos + self.scroll_speed, self.content_height - self.rect.height)
        
        # Handle scrollbar events (like dragging) - this can be expanded upon
        self.scrollbar.handle_event(event)

    def draw(self, screen):
        super().draw(screen)
        self.scrollbar.draw(screen)


def vertical_gradient(screen, top_color, bottom_color):
    """Draw a vertical gradient from top_color to bottom_color on the given screen."""
    for y in range(screen.get_height()):
        ratio = y / screen.get_height()
        interpolated_color = (
            int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio),
            int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio),
            int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        )
        pygame.draw.line(screen, interpolated_color, (0, y), (screen.get_width(), y))

import pygame
from pygame.locals import QUIT, MOUSEBUTTONUP

# Assuming UIButton class is defined above...

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (50, 50, 50)

# Callback function for the button
def button_callback(button):
    print(f"Button {button.text} pressed!")

# Initialization
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))          
pygame.display.set_caption("UIButton Example")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

# Create a panel and a button
panel = ScrollableUIPanel(150, 150, 500, 300, image="panel.png", border_size=10)
for i in range(10):
    button = UIButton(20, 20 + i*80, 200, 60, f"Button {i}", font, image="Box03.png", callback=button_callback, border_size=22)
    panel.add_element(button)

running = True
while running:
    screen.fill((60, 60, 60))  # Fill background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        panel.handle_event(event)  # Pass events to the panel which will pass them to its children

    vertical_gradient(screen, (100, 100, 100), (50, 50, 50))  # Draw a gradient background
    panel.draw(screen)  # Draw the panel and its child elements

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
