import pygame
from config import *

class FocusManager:
    def __init__(self):
        self.focus_group = []
        self.current_focus_index = 0

    def add(self, element):
        self.focus_group.append(element)

    def remove(self, element):
        self.focus_group.remove(element)

    def next(self):
        if self.focus_group:
            self.current_focus_index = (self.current_focus_index + 1) % len(self.focus_group)
            self.set_focus(self.focus_group[self.current_focus_index])

    def set_focus(self, element):
        for elem in self.focus_group:
            elem.is_focused = False
        element.is_focused = True


class UIElement:
    global_id = 1
    def __init__(self, x, y, width, height, parent = None,image=None, color=(200, 200, 200), border_size=10, id=None, padding=0):
        self.padding = padding
        self.elements = []  # List to hold child UI elements        
        self.id = self.generate_id() if not id else id
        self.image = None if not image else pygame.image.load(f"{image}")  # Replace with the path to your button image
        self.color = color
        self.border_size = border_size
        self.original_y = 0
        self.item_offset_y = 0
        self.caret_height = 0
        self.parent = parent
        self.checked = False
        self.disabled = False
        self.hovered = False
        self.selected = False

        if parent:
            self.rect = pygame.Rect(x + parent.rect.x, y + parent.rect.y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)


    def handle_event(self, event):
        pass

    def set_parent(self, parent):
        self.parent = parent
        self.rect.x += parent.rect.x
        self.rect.y += parent.rect.y
        if self.parent:
            self.rect.x += self.parent.padding
            self.rect.y += self.parent.padding
            for element in self.elements:
                element.set_parent(self)

    def generate_id(self):
            id = UIElement.global_id 
            UIElement.global_id += 1
            return id  

    def get_rgba(self, color, default_alpha=100):
        if len(color) == 3:
            return (*color, default_alpha)
        return color

    def draw(self, screen):
        if self.image:
            self.draw_9_slice(screen)
        else:
            transparent_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.color
            transparent_surface.fill(self.get_rgba(self.color))
            screen.blit(transparent_surface, self.rect.topleft)            
            #pygame.draw.rect(screen, self.color, self.rect)

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




class UITextBox(UIElement):
    def __init__(self, x, y, width, height, text='', font_size=20, text_color=(255, 255, 255), cursor_color=(255, 255, 255), parent=None, image=None, border_size=10, end_edit_callback=None, is_password_field=False):
        super().__init__(x, y, width, height, parent, image=image, border_size=border_size)
        self.is_password_field = is_password_field 
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.cursor_color = cursor_color
        self.cursor_pos = len(text)
        self.cursor_visible = True
        self.last_cursor_toggle_time = 0
        self.cursor_toggle_interval = 500
        self.is_focused = False
        self.end_edit_callback = end_edit_callback

    def draw(self, screen, show_cursor=True):
        super().draw(screen)
        display_text = self.text if not self.is_password_field else '*' * len(self.text)  # Display '*' if it's a password field
        text_surface = self.font.render(display_text, True, self.text_color)
        text_rect = text_surface.get_rect(topleft=(self.rect.x + 10, self.rect.y + 10))
        screen.blit(text_surface, text_rect)

        if show_cursor:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_cursor_toggle_time > self.cursor_toggle_interval:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle_time = current_time

            if self.cursor_visible and self.is_focused:
                cursor_x_pos = text_rect.x + text_rect.width
                pygame.draw.line(screen, self.cursor_color, (cursor_x_pos, text_rect.y), (cursor_x_pos, text_rect.y + text_rect.height), 2)
        

    def set_focus(self, focus_manager):
        try:
            index = focus_manager.focus_group.index(self)
            focus_manager.current_focus_index = index
        except ValueError:
            # This textbox is not in the list of focusable elements
            pass

    def set_text(self, text):
        self.text = text
        self.cursor_pos = len(text)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_focused = True
                self.set_focus(self.focus_manager)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                self.is_focused = False
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                if self.end_edit_callback:
                    self.end_edit_callback(self.text)
    


        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if not self.is_focused:
            return

        if self.is_focused:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter key
                    self.is_focused = False
                    if self.end_edit_callback:
                        self.end_edit_callback(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    if self.cursor_pos > 0:
                        self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                        self.cursor_pos -= 1                        
                elif event.key == pygame.K_LEFT:
                    self.cursor_pos = max(0, self.cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                elif event.key == pygame.K_TAB:
                    pass  
                else:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += len(event.unicode)                    
        

class UIColorPicker(UIElement):
    def __init__(self, x, y, width, height, color_clicked_callback=None, parent=None, image=None, border_size=10, padding=0):
        super().__init__(x, y, width, height, parent=parent, image=image, border_size=border_size, padding=padding)
        self.color_clicked_callback = color_clicked_callback        
        self.surface = pygame.Surface((width, height))
        self.is_visible = False
        self.ignore_next_click = False

        # Fill color picker with blended colors
        for x in range(width):
            for y in range(height):
                R = int(x / (width - 1) * 255)
                G = int(y / (height - 1) * 255)
                B = 255 - int((R + G) / 2)
                self.surface.set_at((x, y), (R, G, B))

        self.common_colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255),
            (128, 0, 128), (0, 128, 128)
        ]

        self.grayscale_colors = [
            (0, 0, 0), (32, 32, 32), (64, 64, 64),
            (96, 96, 96), (128, 128, 128), (160, 160, 160),
            (192, 192, 192), (255, 255, 255)
        ]


    def draw(self, screen):
        if self.is_visible:
            rect = screen.get_clip()
            screen.set_clip(None)            
            screen.blit(self.surface, (self.rect.x, self.rect.y))

           # Additional code for grayscale and common colors
            column_width = 20  # Width of each column
            y_start = self.rect.y  # Y-coordinate where the columns start
            
            for i, color in enumerate(self.grayscale_colors):
                pygame.draw.rect(screen, color, (self.rect.x + self.rect.width, y_start + i * column_width, column_width, column_width))
            
            for i, color in enumerate(self.common_colors):
                pygame.draw.rect(screen, color, (self.rect.x + self.rect.width + column_width, y_start + i * column_width, column_width, column_width))

            screen.set_clip(rect)

    def handle_event(self, event):
        if not self.is_visible:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
                self.handle_mouse_click(event)

        return None


    def handle_mouse_click(self, event):
        if self.ignore_next_click:
            self.ignore_next_click = False
            return

        x, y = event.pos

        # Check if the click is within the color picker area
        surface_width, surface_height = self.surface.get_size()
        if 0 <= x - self.rect.x < surface_width and 0 <= y - self.rect.y < surface_height:
            self.currentColor = self.surface.get_at((x - self.rect.x, y - self.rect.y))
            if self.color_clicked_callback:
                self.color_clicked_callback(self.currentColor)
        else:
            self.handle_click_in_additional_columns(x, y)

    def handle_click_in_additional_columns(self, x, y):
        column_width = 20
        y_start = self.rect.y

        if self.rect.x + self.rect.width <= x <= self.rect.x + self.rect.width + 2 * column_width:
            # Determine which column was clicked
            column_clicked = (x - self.rect.x - self.rect.width) // column_width
            color_index = (y - y_start) // column_width

            if column_clicked == 0:
                if 0 <= color_index < len(self.grayscale_colors):
                    self.currentColor = self.grayscale_colors[color_index]
            elif column_clicked == 1:
                if 0 <= color_index < len(self.common_colors):
                    self.currentColor = self.common_colors[color_index]

            if self.color_clicked_callback:
                self.color_clicked_callback(self.currentColor)
        else:
            self.is_visible = False

class UIColoredTextBox(UITextBox):
    def __init__(self, x, y, width, height, text='', font_size=20, text_color=(255, 255, 255),
                 cursor_color=(255, 255, 255), parent=None, image=None, border_size=10, end_edit_callback=None):
        super().__init__(x, y, width, height, text, font_size=font_size, text_color=text_color,
                         cursor_color=cursor_color, parent=parent, image=image, border_size=border_size, end_edit_callback=end_edit_callback)
        self.colored_text = [(char, text_color) for char in text]
        self.current_color = text_color

        button_height = 30  # Or any other size you'd like
        button_width = 50
        self.color_picker_button = UIButton(x + width - button_width, 0, button_width, button_height, None, callback=self.pick_color, image=image, border_size=border_size, color=text_color)
        button_height = self.color_picker_button.rect.height
        self.color_picker_button.rect.y = (self.rect.height /2  - button_height/ 2)

        color_picker_x = x + width - button_width + button_width + 5  # 5 pixels to the right of the button
        color_picker_y = 0  # same vertical level as the button
        self.color_picker = UIColorPicker(color_picker_x, color_picker_y, 256, 256, color_clicked_callback=self.update_color, image=image, border_size=border_size, padding=10)
        self.color_picker.is_visible = False  # Initially set to invisible
        self.elements.append(self.color_picker_button)
        self.color_list = [{'index': 0, 'color': self.current_color}]
        # self.set_position(x, y)

    def serialize(self):
        state = {
            'text': self.colored_text,
            'colors': self.color_list
        }
        return json.dumps(state)

    def deserialize(self, state_string):
        state = json.loads(state_string)
        self.colored_text = state['text']
        self.color_list = state['color_list']

    def set_position(self, x, y):
        position_delta_x = x - self.rect.x
        position_delta_y = y - self.rect.y
        self.rect.x = x
        self.rect.y = y

        for element in self.elements:
            element.rect.x += position_delta_x
            element.rect.y += position_delta_y

        # Re-center the button vertically
        button_height = self.color_picker_button.rect.height
        self.color_picker_button.rect.y = self.rect.y + (self.rect.height /2  - button_height/ 2)


    def set_parent(self, parent):
        super().set_parent(parent)
        #self.color_picker_button.set_parent(self)

    def remove_char(self):
        if self.cursor_pos > 0:
            if self.colored_text[self.cursor_pos - 1][0] == ']':
                # Remove the entire tag
                while self.cursor_pos > 0:
                    del self.colored_text[self.cursor_pos - 1]
                    self.cursor_pos -= 1
                    if self.colored_text[self.cursor_pos - 1][0] == '[':
                        del self.colored_text[self.cursor_pos - 1]
                        self.cursor_pos -= 1
                        break
            else:
                del self.colored_text[self.cursor_pos - 1]
                self.cursor_pos -= 1

    def skip_tags(self, direction=1):
        while self.cursor_pos >= 0 and self.cursor_pos < len(self.colored_text):
            char, _ = self.colored_text[self.cursor_pos]
            if char == '[' or char == ']':
                self.cursor_pos += direction
            else:
                break

    def pick_color(self, button):
        self.color_picker.is_visible = not self.color_picker.is_visible
        if self.color_picker.is_visible:
            # Update the position of color_picker to be beside the button
            self.color_picker.rect.x = self.color_picker_button.rect.x + self.color_picker_button.rect.width + 5
            self.color_picker.rect.y = self.color_picker_button.rect.y + self.color_picker.rect.height / 2 + self.color_picker_button.rect.height / 2
            self.color_picker.ignore_next_click = True

    def add_char(self, char):
            self.colored_text.insert(self.cursor_pos, char)
            self.cursor_pos += 1
            for color_change in self.color_list:
                if color_change['index'] >= self.cursor_pos:
                    color_change['index'] += 1

    def remove_char(self):
        if self.cursor_pos > 0:
            del self.colored_text[self.cursor_pos - 1]
            self.cursor_pos -= 1
            for color_change in self.color_list:
                if color_change['index'] >= self.cursor_pos:
                    color_change['index'] -= 1

    def update_color(self, color):
        for color_change in self.color_list:
            if color_change['index'] == self.cursor_pos:
                color_change['color'] = color
                self.update_button_color()
                return
        self.color_list.append({'index': self.cursor_pos, 'color': color})
        self.color_list = sorted(self.color_list, key=lambda x: x['index'])
        self.update_button_color()


    def draw(self, screen):
        super().draw(screen, False)
        current_color = self.current_color
        x_offset = 0
        cursor_x_offset = 0  # Initialize x offset for the cursor

        for i, char in enumerate(self.colored_text):
            # Update color if the index matches a color change point
            for color_change in self.color_list:
                if color_change['index'] == i:
                    current_color = color_change['color']

            char_surface = self.font.render(char, True, current_color)
            char_rect = char_surface.get_rect(topleft=(self.rect.x + 10 + x_offset, self.rect.y + 10))
            screen.blit(char_surface, char_rect)
            x_offset += char_surface.get_width()

            # Update the cursor_x_offset if we're at the cursor's position
            if i == self.cursor_pos - 1:
                cursor_x_offset = x_offset

        current_time = pygame.time.get_ticks()
        if current_time - self.last_cursor_toggle_time > self.cursor_toggle_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle_time = current_time

        if self.cursor_visible and self.is_focused:
            # Draw the cursor
            cursor_color = self.cursor_color
            cursor_rect = pygame.Rect(self.rect.x + 10 + cursor_x_offset, self.rect.y + 10, 2, self.font.size("A")[1])
            pygame.draw.rect(screen, cursor_color, cursor_rect)

        self.color_picker_button.draw(screen)
        if self.color_picker.is_visible:
            self.color_picker.draw(screen)


    def handle_event(self, event):        
        self.color_picker_button.handle_event(event)

        if event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.remove_char()
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                self.update_button_color()
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.colored_text), self.cursor_pos + 1)
                self.update_button_color()
            elif event.unicode:  # Check if the event produces a unicode character
                self.add_char(event.unicode)  # Add the character
            else:
                super().handle_event(event)
        else:
            super().handle_event(event)

        picked_color = self.color_picker.handle_event(event)
        if picked_color:
            self.current_color = picked_color

    def update_button_color(self):
        for color_change in self.color_list:
            if color_change['index'] == self.cursor_pos:
                self.color_picker_button.color = color_change['color']
                break

    def add_element(self, element):
        element.set_parent(self)
        self.elements.append(element)
        element.original_y = element.rect.y  # Store the original y-position
        element.focus_manager = self.focus_manager
        if isinstance(element, UITextBox):  # Add only UITextBox elements to the focus manager
            self.focus_manager.add(element)                        



class UIImage(UIElement):
    def __init__(self, x, y, image=None, parent=None,color=(100, 100, 100), border_size=0, move_to_bounding_pos=False, callback=None, padding=0):
        super().__init__(x, y, 0,0, parent, image, color, border_size, padding=padding)
        self.move_to_bounding_pos = move_to_bounding_pos
        self.callback = callback
        if image:
            self.image = pygame.image.load(image)
            self.bounding_rect = self.get_bounding_rectangle()
            rect = self.image.get_rect()
            self.rect.width = rect.width
            self.rect.height = rect.height
            if self.parent:
                self.rect.x += self.parent.padding
                self.rect.y += self.parent.padding

            if move_to_bounding_pos:
                self.rect.x -= self.bounding_rect.x
                self.rect.y -= self.bounding_rect.y


    def world_to_local(self, pos):
        pos[0] -= self.parent.rect.x
        pos[1] -= self.parent.rect.y
        if self.parent:
            pos[0] += self.parent.padding
            pos[1] += self.parent.padding

        if self.move_to_bounding_pos:
            pos[0] -= self.bounding_offset[0]
            pos[1] -= self.bounding_offset[1]  
        return pos

    def local_to_world(self, pos):
        pos[0] += self.parent.rect.x
        pos[1] += self.parent.rect.y
        if self.parent:
            pos[0] -= self.parent.padding
            pos[1] -= self.parent.padding

        if self.move_to_bounding_pos:
            pos[0] += self.bounding_offset[0]
            pos[1] += self.bounding_offset[1]  
        return pos

    def set_parent(self, parent):
        super().set_parent(parent)
      
        if self.move_to_bounding_pos:
            self.rect.x -= self.bounding_rect.x
            self.rect.y -= self.bounding_rect.y      

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Adjust the mouse position for the parent's position (and scroll position, if applicable)
            if self.is_mouse_is_over(event.pos):
                if self.callback:
                    self.callback(self)

    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
        collide = self.rect.collidepoint(adjusted_mouse_pos)
        return collide
    
    def get_bounding_rectangle(self):
        # Initialization
        width, height = self.image.get_size()
        x1, y1, x2, y2 = width, height, 0, 0

        # Lock the surface for direct pixel access
        self.image.lock()

        for y in range(height):
            for x in range(width):
                # Get the alpha value of the pixel
                _, _, _, alpha = self.image.get_at((x, y))
                
                # If the pixel is not transparent
                if alpha > 0:
                    x1 = min(x1, x)
                    y1 = min(y1, y)
                    x2 = max(x2, x)
                    y2 = max(y2, y)

        # Unlock the surface
        self.image.unlock()

        # If no bounding rectangle is found (empty or fully transparent sprite)
        if x2 < x1 or y2 < y1:
            return None

        # Return as a pygame.Rect object
        return pygame.Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1)                        

class UILabel(UIImage):
    def __init__(self, x, y, text,  parent=None, font_size=20, text_color=(255, 255, 255), font=None, outline_width=0, outline_color=(0,0,0), padding=0):
        super().__init__(x, y, None, parent, text_color, padding=padding) 
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.text = text
        self.font = pygame.font.Font(None, font_size) if not font else font
        self.text_color = text_color
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surface.get_rect(top=self.rect.top, left=self.rect.left)

    def set_text(self, text):
        self.text = text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surface.get_rect(top=self.rect.top, left=self.rect.left)

    def draw(self, screen):
        if not self.font:
            return
        #self.set_parent(self.parent)
        if self.outline_width > 0:
            self.draw_text_with_outline(self.text, screen, self.text_color, self.outline_color, self.outline_width)
        else:
            screen.blit(self.text_surface, (self.rect.topleft[0], self.rect.topleft[1]))

    def draw_text_with_outline(self, text, screen, text_color=(255,255,255), outline_color=(0,0,0), outline_thickness=2, alpha_value=255):
        # Create text surface
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(top=self.rect.top, left=self.rect.left)
        
        # Create outline by drawing text multiple times around the original text
        outline_alpha_color = (*outline_color[:3], alpha_value)
        for i in range(-outline_thickness, outline_thickness+1):
            for j in range(-outline_thickness, outline_thickness+1):
                outline_surface = self.font.render(text, True, outline_alpha_color)
                outline_rect = outline_surface.get_rect(top=self.rect.top+j, left=self.rect.left+i)
                screen.blit(outline_surface, outline_rect)
        
        # Draw the original text
        screen.blit(text_surface, text_rect)    


class UIButton(UIElement):
    def __init__(self, x, y, width, height, text, font_size = 20, image=None, parent=None,color=(100, 100, 100), border_size=10, text_color=(255, 255, 255), hover_text_color=(255, 255, 0), callback=None, trigger_key=None):
        super().__init__(x, y, width, height, parent, image, color, border_size)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.normal_text_color = text_color
        self.hover_text_color = hover_text_color
        self.callback = callback
        self.is_hovered = False
        self.enabled = True
        self.trigger_key = trigger_key


    def draw(self, screen):
        super().draw(screen)
        
        # Draw the button text
        if not self.font:
            return
        text_color = self.text_color
        if not self.enabled:
            text_color = (100, 100, 100)
        text_surface = self.font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, (text_rect.topleft[0], text_rect.topleft[1]))

    def handle_event(self, event):
        if not self.enabled:
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == self.trigger_key:
                if self.callback:
                    self.callback(self)

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
            if self.is_mouse_is_over(event.pos):
                if self.callback:
                    self.callback(self)

    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
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

class UIContainer(UIElement):
    def __init__(self, x, y, width, height, image=None, color=(100, 100, 100), border_size=10, padding=10):
        super().__init__(x, y, width, height, None, image, color, border_size, padding=padding)
        self.focus_manager = FocusManager()

        
        # Initialize Scrollbar Variables
        self.scroll_position = 0  # Scroll position
        self.caret_height = 50  # Initial height of scrollbar
        self.dragging_caret = False  # True if the caret is being dragged
        self.mouse_offset = 0  # Offset from top of caret to mouse        

    def center_on_screen(self, screen_width, screen_height):
        # Calculate the new x and y coordinates for centering the UIMessageBox
        new_x = (screen_width - self.rect.width) // 2
        new_y = (screen_height - self.rect.height) // 2
        
        # Calculate the offsets needed to move the child elements
        x_offset = new_x - self.rect.x
        y_offset = new_y - self.rect.y
        
        # Update the x and y coordinates of the UIMessageBox
        self.rect.x = new_x
        self.rect.y = new_y
        
        # Update the positions of child elements as well
        for element in self.elements:
            element.rect.x += x_offset
            element.rect.y += y_offset
            element.original_x = element.rect.x
            element.original_y = element.rect.y

    def needs_scrollbar(self):
        total_height = sum([element.rect.height for element in self.elements])
        return total_height > self.rect.height

    def add_element(self, element):
        element.set_parent(self)
        self.elements.append(element)
        element.original_y = element.rect.y  # Store the original y-position
        element.focus_manager = self.focus_manager
        if isinstance(element, UITextBox):  # Add only UITextBox elements to the focus manager
            self.focus_manager.add(element)

    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)
            if isinstance(element, UITextBox):  # Remove the element from the focus manager as well
                self.focus_manager.remove(element)

    def adjust_to_content(self):
        if not self.elements:
            return
        min_x = min([element.rect.x for element in self.elements])
        min_y = min([element.rect.y for element in self.elements])
        max_x = max([element.rect.x + element.rect.width for element in self.elements])
        max_y = max([element.rect.y + element.rect.height for element in self.elements])

        self.rect.x = min_x - self.padding
        self.rect.y = min_y - self.padding
        self.rect.width = max_x - min_x + 2 * self.padding
        self.rect.height = max_y - min_y + 2 * self.padding

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle Scrollbar and Caret Events
        scrollbar_rect = pygame.Rect(self.rect.right - 20, self.rect.y + self.scroll_position, 20, self.caret_height)
        # Handle mouse wheel scrolling
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_position = max(self.scroll_position - 50, 0)
            elif event.button == 5:  # Scroll down
                self.scroll_position = min(self.scroll_position + 50, self.rect.height - self.caret_height) 

            if scrollbar_rect.collidepoint(mouse_pos):
                self.dragging_caret = True
                self.mouse_offset = mouse_pos[1] - self.rect.y - self.scroll_position    
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_caret = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_caret:
            new_scroll_position = mouse_pos[1] - self.rect.y - self.mouse_offset
            max_scroll = self.rect.height - self.caret_height
            self.scroll_position = min(max(0, new_scroll_position), max_scroll)
        
        for element in self.elements:
            # Update the y-position based on the scroll position
            element.rect.y = element.original_y - self.scroll_position
            element.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.focus_manager.next()  

    def draw(self, screen):
        super().draw(screen)
        
        # Set the clipping region
        clip_rect = pygame.Rect(self.rect.x + self.padding, 
                                self.rect.y + self.padding, 
                                self.rect.width - 2 * self.padding, 
                                self.rect.height - 2 * self.padding)
        screen.set_clip(clip_rect)
        
        for element in self.elements:
            element.draw(screen)
            #pygame.draw.rect(screen, (0, 0, 0), element.rect, 1)

        # Reset the clipping region
        screen.set_clip(None)
        
        # Draw Scrollbar and Caret
        # if self.needs_scrollbar():        
        #     pygame.draw.rect(screen, (0, 0, 0), (self.rect.right - 20, self.rect.y, 20, self.rect.height))
        #     pygame.draw.rect(screen, (100, 100, 100), (self.rect.right - 20, self.rect.y + self.scroll_position, 20, self.caret_height))

class UIMessageBox(UIContainer):
    def __init__(self, message, x, y, width=400, height=300, ok_callback=None, padding=20, image=None, color=(100, 100, 100), border_size=10, font_size=30, screen=None):
        super().__init__(x, y, width, height, padding=padding, image=image, color=color, border_size=border_size)
        self.screen = screen
        self.is_visible = False
        self.message_label = UILabel(0, padding, message, font_size=font_size)
        self.ok_button = UIButton(0, self.message_label.rect.bottom + 20, 100, 40, "OK", callback=self.ok_button_pressed)
        
        self.ok_callback = ok_callback
        
        self.add_element(self.message_label)
        self.add_element(self.ok_button)

        self.adjust()
        # self.center_elements()
        # if self.screen:
        #     self.center_on_screen(self.screen.get_width(), self.screen.get_height())

    def ok_button_pressed(self, button):
        self.hide()
        if self.ok_callback:
            self.ok_callback(self)
        
    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)
    
    def show(self, message=""):
        self.message_label.set_text(message)
        self.adjust()
        self.is_visible = True

    def hide(self):
        self.is_visible = False

    def draw(self, screen):
        if not self.is_visible:
            return
        super().draw(screen)

    def adjust(self):
        self.rect.x = 0
        self.rect.y = 0
        max_width = max(self.message_label.rect.width, self.ok_button.rect.width)
        self.rect.width = max_width + 2 * self.padding
        self.message_label.rect.y = self.padding
        self.ok_button.rect.y = self.message_label.rect.bottom + 20
        
        self.center_elements()

        min_y = self.message_label.rect.y
        max_y = self.ok_button.rect.bottom
        
        total_height = max_y - min_y
        
        self.rect.height = total_height + 2 * self.padding
        self.ok_button.original_y = self.ok_button.rect.y

        if self.screen:
            self.center_on_screen(self.screen.get_width(), self.screen.get_height())  

    def center_elements(self):
        for element in self.elements:
            element.rect.x = (self.rect.width - element.rect.width) // 2



class UIProgressBar(UIElement):
    def __init__(self,x, y, width, height, max_squares_per_row, image=None, border_size=10, max_value = 100, color1=(0,255,0), color2=(150,150,150)):
        super().__init__(x, y, width, height, image=image, border_size=border_size)
        self.max_value = max_value
        self.current_value = 0
        self.color1 = color1
        self.color2 = color2
        self.width = width
        self.square_width = width / max_squares_per_row
        self.square_width -= 1 
        self.square_height = height - 10
        self.max_squares_per_row = max_squares_per_row
        pass

    def draw(self, screen):
        for i in range(self.max_value):
            row = i // self.max_squares_per_row
            col = i % self.max_squares_per_row
            
            square_x = self.rect.x + col * (self.square_width + 1)
            square_y = self.rect.y + row * (self.square_width + 1)
            
            if i < self.current_value:
                pygame.draw.rect(screen, self.color1, (square_x, square_y, self.square_width, self.square_height))
            else:
                pygame.draw.rect(screen, self.color2, (square_x, square_y, self.square_width, self.square_height))         

class ListItem(UIElement):
    def __init__(self, x, y, width, height, text, color, font, icon=None, id = None):
        super().__init__(x, y, width, height, None, None, (0, 0, 0), 0, id = id)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.icon = icon
        self.font = font
        self.disabled = False
        self.hovered = False
        self.selected = False

    def draw(self, surface):
        icon_offset = 30  # The space reserved for the icon, whether it exists or not

        if self.selected:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        color = self.color
        if self.hovered:
            color = (255, 255, 0)

        if self.disabled:
            color = (150, 150, 150)

        # Draw the text next to the icon
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect()

        # Vertically align the text by adjusting the y-coordinate
        text_rect.midleft = (icon_offset + self.rect.x + 10, self.rect.centery)
        
        surface.blit(text_surface, text_rect)


class UICheckBox(UIElement):
    def __init__(self, x, y, width, height, image=None, icon=None, border_size=10, callback=None):
        super().__init__(x, y, width, height, None, image, (0, 0, 0), border_size)
        if icon:
            self.icon = pygame.image.load(icon)
        #self.icon = self.icon = icon
        self.checked = False
        self.callback = callback

    def draw(self, surface):
        super().draw(surface)
        if self.icon and self.checked:
            icon_rect = self.icon.get_rect()
            icon_rect.midleft = (self.rect.x + 10, self.rect.centery)        
            surface.blit(self.icon, icon_rect)

class UIHeader(UIElement):
    def __init__(self, x, y, width, height, column_names, column_widths, font, image=None, color=(255, 255, 255), padding=10, horizontal_align='center'):
        super().__init__(x, y, width, height, image=image, color=color, padding=padding)
        self.column_names = column_names
        self.column_widths = column_widths
        self.font = font
        self.horizontal_align = horizontal_align

    def draw(self, screen):
        super().draw(screen)
        x_offset = 0

        for i, name in enumerate(self.column_names):
            label_surface = self.font.render(name, True, self.color)
            label_rect = (label_surface.get_rect())

            if self.horizontal_align == 'left':
                label_rect.x = self.rect.x + x_offset + self.padding
            elif self.horizontal_align == 'center':
                label_rect.x = self.rect.x + x_offset + (self.column_widths[i] / 2 - label_rect.width / 2)
            elif self.horizontal_align == 'right':
                label_rect.x = self.rect.x + x_offset + self.column_widths[i] - label_rect.width - self.padding

            label_rect.y = self.rect.y + self.padding
            screen.blit(label_surface, label_rect)
            x_offset += self.column_widths[i]


class UIList(UIElement):
    def __init__(self, x, y, width, height, rows = [], text_color=(255, 255, 255),item_height = 50, item_selected_callback=None, image=None, border_size=10, padding=10,  num_columns=1, column_widths=None, headers=None, header_font_size=20, header_image=None, header_height=50):
        super().__init__(x, y, width, height - header_height, None, image, (0, 0, 0), border_size, padding=padding)
        self.headers = headers if headers else []

        self.num_columns = num_columns
        self.column_widths = column_widths if column_widths else [width // num_columns] * num_columns         
        self.item_selected_callback = item_selected_callback
        self.rect = pygame.Rect(x, y, width, height)
        self.selected_item = None
        self.rows = [] if not rows else rows
        self.text_color = text_color
        self.item_height = item_height  # Height of each item
        self.font = pygame.font.Font(None, header_font_size)
        if self.headers:
            self.header = UIHeader(x, y- header_height, width, header_height, self.headers, self.column_widths, self.font, color = text_color, image=header_image if header_image else image)
        else:
            self.header = None
        #self._rebuild_ui()
        self.hovered_item = None
        self.read_only = False
        self.scroll_position = 0  # The scroll position, starting at 0
        self.scrollbar_width = 20  # Width of the scrollbar
        self.caret_height = 50  # Initial height of the scrollbar caret
        self.dragging_caret = False
        self.item_offset_y = 0
        self.mouse_offset = 0
        self.mouse_button_down = False
        self.total_width = sum(self.column_widths)
        self.screen = None

    def set_read_only(self, read_only):
        self.read_only = read_only

    def reset_all(self):
        for row in self.rows:
            for item in row:
                item.checked = False
                item.disabled = False
                item.hovered = False
                item.selected = False

    def add_row(self, elements):
        if len(elements) != self.num_columns:
            print("Warning: Number of elements doesn't match the number of columns.")
            return

        # Position the elements correctly based on the column widths
        x_offset = 0
        y_offset = len(self.rows) * self.item_height  # Stack vertically

        for i, elem in enumerate(elements):
            elem.rect.x = self.rect.x + x_offset
            elem.rect.y = self.rect.y + y_offset  # Same y-coordinate for all elements in the row
            x_offset += self.column_widths[i]  # Increment x-coordinate based on column width
            elem.set_parent(self)  # Set the parent to adjust position accordingly
        
        self.rows.append(elements)  # Add the row to the list

    def add_item(self, text, icon=None, color=(255, 255, 255), id=None):
        new_item = ListItem(0, self.num_columns * self.item_height, self.rect.width, self.item_height, text, color, self.font, icon, id=id)
        new_item.set_parent(self)
        new_item.original_y = self.num_columns * self.item_height
        new_row = [new_item]  
        self.rows.append(new_row)

    def get_selected_item(self):
        return self.selected_item

    def _rebuild_ui(self):
        for index, row in enumerate(self.rows):
            for item in row:
                list_item = ListItem(0, index * self.item_height, self.rect.width, self.item_height, item.text, item.color, self.font, item.icon)
                list_item.id = item  
                self.rows[index][0] = list_item

    def _item_selected(self, list_item):
        self.selected_item = list_item.id
        for row in self.rows:
            for item in row:
                item.selected = item.id == self.selected_item
                if self.item_selected_callback:
                    self.item_selected_callback(item)  

    def remove_item(self, id):
        for index, row in enumerate(self.rows):
            if row[0].id == id:
                del self.rows[index]
                break

    def check_item(self, id, checked=True):
        for row in self.rows:
            if row[0].id == id:
                row[0].checked = checked

    def select_item(self, id):
        for row in self.rows:
            if row[0].id == id:
                self._item_selected(row[0])

    def enable_item(self, id, enabled=True):
        for row in self.rows:
            if row[0].id == id:
                row[0].disabled = not enabled

    def get_item_by_id(self, id):
        for row in self.rows:
            if row[0].id == id:
                return row[0]
        return None
    

    def handle_event(self, event):
        if self.read_only:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + self.padding, mouse_pos[1])

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self._handle_mouse_down(event, mouse_pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event)

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event, mouse_pos)

        
        # Update item positions based on scroll
        height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
        self.item_offset_y = self.scroll_position * height_ratio

        row_y_offset = 0  # Initialize row offset

        for row in self.rows:
            x_offset = 0  # Initialize x offset for each row
            for i, item in enumerate(row):
                item.rect.x = self.rect.x + x_offset + self.padding  # Update x based on column position

                # Calculate the bottom-aligned y-coordinate for each item
                aligned_bottom_y = self.rect.y + row_y_offset - self.item_offset_y + self.item_height - item.rect.height  

                # Update y based on row position, scroll and alignment
                item.rect.y = aligned_bottom_y 

                x_offset += self.column_widths[i]  # Increment x-coordinate based on column width
                item.handle_event(event)  # Call handle_event for each UIElement

            row_y_offset += self.item_height  # Increment row y-coordinate based on item height and padding

    def _handle_mouse_down(self, event, mouse_pos):
        # Handle mouse wheel scrolling
        if event.button == 4:  # Scroll up 
            self.scroll_position = max(self.scroll_position - self.item_height, 0)
            max_scroll = self.rect.height - self.caret_height - self.padding * 2
            height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
            self.scroll_position = min(max(0, self.scroll_position), max_scroll)
            self.item_offset_y = self.scroll_position * height_ratio
            # Update row items
            for row in self.rows:
                for item in row:
                    item.rect.y = item.original_y - self.item_offset_y            
        elif event.button == 5:  # Scroll down
            max_scroll = self.rect.height - self.caret_height - self.padding * 2  
            self.scroll_position = min(self.scroll_position + self.item_height, max_scroll)
            max_scroll = self.rect.height - self.caret_height - self.padding * 2
            height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
            self.scroll_position = min(max(0, self.scroll_position), max_scroll)
            self.item_offset_y = self.scroll_position * height_ratio  
            #item.rect.y = (item.original_y - self.item_offset_y + self.caret_height / 2)         
            # Update row items
            for row in self.rows:
                for item in row:
                    item.rect.y = item.original_y - self.item_offset_y  

        for row in self.rows:
            for item in row:
                item.rect.y = (item.original_y - self.item_offset_y + self.caret_height / 2)                     

        if event.button == 1:
            # Update row items
            # Handle scrollbar drag
            scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y + self.scroll_position, self.scrollbar_width, self.caret_height)
            if scrollbar_rect.collidepoint(mouse_pos):
                self.dragging_caret = True
                self.mouse_offset = mouse_pos[1] - self.rect.y - self.scroll_position
                return  
            else:
                self.dragging_caret = False

            for row in self.rows:
                for item in row:
                    item.selected = item.id == self.selected_item

                    # Check if the mouse is over an item
                    if item.rect.collidepoint(mouse_pos) and not item.disabled:
                        self.selected_row = row
                        self._item_selected(item)
                        if self.item_selected_callback:
                            self.item_selected_callback(item)                  



    def _handle_mouse_up(self, event):
        self.dragging_caret = False
        height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
        self.item_offset_y = self.scroll_position * height_ratio

    def _handle_mouse_motion(self, event, mouse_pos):

        # Existing logic for dragging caret and updating hover state
        if self.dragging_caret:
            new_scroll_position = mouse_pos[1] - self.rect.y - self.mouse_offset
            max_scroll = self.rect.height - self.caret_height - self.padding * 2
            height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
            self.scroll_position = min(max(0, new_scroll_position), max_scroll)
            self.item_offset_y = self.scroll_position * height_ratio


        over_scroll_bar = False
        scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y + self.scroll_position, self.scrollbar_width, self.caret_height)
        if scrollbar_rect.collidepoint(mouse_pos):
            over_scroll_bar = True  


        self.hovered_item = None
        #if self.rect.collidepoint(mouse_pos):  # Only update hovered_item if the mouse is over the list
        for row in self.rows:
            for item in row:
                #item.rect.y = (item.original_y - self.item_offset_y + 100)
                if not over_scroll_bar and item.rect.collidepoint(mouse_pos):
                    self.hovered_item = item
                    break



    def draw(self, screen):
        # screen.fill((0, 0, 0))
        super().draw(screen)

        if self.header:
            self.header.draw(screen)      
        self.screen = screen
        clip_rect = pygame.Rect(self.rect.x + self.padding, 
                                self.rect.y + self.padding, 
                                self.rect.width - 2 * self.padding, 
                                self.rect.height - 2 * self.padding)

        screen.set_clip(clip_rect)

        first_item = None
        row_index = 0
        for row in self.rows:
            for item in row:
                if not first_item:
                    first_item = item
                item.draw(screen)
                item.hovered = item == self.hovered_item
                #pygame.draw.rect(screen, (0, 150, 0), item.rect, 2)

            height_ratio = ((len(self.rows) + 2) * self.item_height) / self.rect.height
            self.item_offset_y = self.scroll_position * height_ratio + self.rect.y
            pygame.draw.line(screen, (150, 150, 150), (first_item.rect.x, self.rect.y -self.item_offset_y+(row_index*(self.item_height)) + self.item_height*2), 
                            (first_item.rect.x + self.total_width, self.rect.y -self.item_offset_y+(row_index*(self.item_height)) + self.item_height*2), 2)
            
            row_index+=1

        screen.set_clip(None)  # Remove clipping region

        if len(self.rows) == 0:
            total_height = 0
        else:
            total_height = len(self.rows) * self.item_height
            self.caret_height = max(10, int((self.rect.height / total_height) * self.rect.height))

        max_scroll = total_height - self.rect.height
        self.scroll_position = min(max(0, self.scroll_position), max_scroll)

        pygame.draw.rect(screen, (0, 0, 0), 
                        (self.rect.right - self.scrollbar_width - self.padding, 
                        self.rect.y + self.padding, 
                        self.scrollbar_width, 
                        self.rect.height - 2 * self.padding))

        pygame.draw.rect(screen, (100, 100, 100), 
                        (self.rect.right - self.scrollbar_width - self.padding, 
                        self.rect.y + self.scroll_position + self.padding, 
                        self.scrollbar_width, 
                        self.caret_height))
        


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


"""
PyGame UI Framework

Provides reusable UI elements and containers for building interfaces with PyGame.

Components:

- FocusManager: Handles focus between UIElements like text fields. 
              Tracks current focused element.

- UIElement: Base class for interactive UI elements.
             Has event handling, drawing, positioning code.
             
- UITextBox: Text input box that supports cursor, text insertion/deletion, 
             keyboard focus. Blinks cursor when focused.
             
- ColorPicker: Widget to select a color. Renders gradient and returns 
               clicked color.
               
- UIColoredTextBox: Extends UITextBox with support for colored text.
                    Allows coloring ranges of text.
                    
- UIButton: Clickable button with hover state handling. Calls a
            callback function when clicked.
            
- UIContainer: Groups UIElements together. Useful for windows, panels etc.
               Draws children and passes events to them.
               
- UIMessageBox: Popup dialog with a message and OK button.

- UIProgressBar: Renders a progress bar out of colored squares.

- ListItem: Displays a selectable row item with icon, text, states.

- UICheckBox: Clickable box with a checkmark icon when enabled.

- UIHeader: Renders column headings for lists.

- UIList: Vertical list of selectable rows. Handles scrolling, selection,
           keyboard focus between items.
           
Usage:

1. Create UIElement instances and add to a UIContainer.

2. Draw the UIContainer on the screen. 

3. Pass PyGame events from main loop to container to propagate to children.

4. Call individual element event handlers for additional behavior.

Provides building blocks for complex interfaces without repeating boilerplate 
event handling, drawing, focus logic etc.
"""


import pygame


# # Screen constants
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600

# # Helper function to create some buttons
# def create_buttons(container):
#   btn_names = ["Btn 1", "Btn 2", "Btn 3"]
  
#   for name in btn_names:
#     btn = UIButton(20, 20, 120, 40, name, callback=button_clicked)
#     container.add_element(btn)

# # Callback when a button is clicked  
# def button_clicked(button):
#   print(f"{button.text} clicked!")

# # Callback when an item is selected  
# def item_selected(item):
#   print(f"{item.text} selected!")
  
# # Main program  

# pygame.init()
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# # Root container
# container = UIContainer(20, 20, SCREEN_WIDTH-40, SCREEN_HEIGHT-40)

# # Buttons
# create_buttons(container)

# # Text box
# textbox = UITextBox(20, 80, 300, 40) 
# container.add_element(textbox)

# # Colored text box  
# color_textbox = UITextBox(20, 140, 300, 40)
# container.add_element(color_textbox)

# # Progress bar
# progress = UIProgressBar(20, 200, 300, 40, 10)
# container.add_element(progress)

# # Image
# image = UIImage(350, 20, "assets\\UI\\Button01.png")
# container.add_element(image) 

# # List
# mylist = UIList(350, 80, 300, 220, item_selected_callback=item_selected)
# mylist.add_item("Item 1")
# mylist.add_item("Item 2")
# container.add_element(mylist)

# # Checkbox
# checkbox = UICheckBox(350, 320, 30, 30, icon="assets\\UI\\checkbox.png")
# container.add_element(checkbox)

# # Message box
# msgbox = UIMessageBox("Hello World!", 300, 300, ok_callback=print)

# running = True
# while running:

#   # Draw and handle events
#   container.draw(screen)
  
#   for event in pygame.event.get():
#     if event.type == pygame.QUIT:
#       running = False
      
#     container.handle_event(event)
    
#     if event.type == pygame.MOUSEBUTTONDOWN:
#       msgbox.center_on_screen(SCREEN_WIDTH, SCREEN_HEIGHT)
      
#   pygame.display.update()
  
# pygame.quit()