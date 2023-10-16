from collections import OrderedDict
import pygame
from config import *
from UIConfig import *

class Sentinel:
    def __bool__(self):
        return False
UNSET = Sentinel()  # Sentinel object to signify unset attributes

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


    def handle_cursor(self, event, textboxes):
        for textbox in textboxes:
            if textbox.rect.collidepoint(event.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
                return
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)        


class UIElement:
    global_id = 1
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, parent=UNSET,image=UNSET, color=UNSET, border_size=UNSET, id=UNSET, padding=UNSET):
        self.padding = padding if padding is not UNSET else 0
        self.elements = []      
        self.id = self.generate_id() if id is not UNSET else id
        self.image = None if not image else pygame.image.load(f"{image}")  # Replace with the path to your button image
        self.no_image_color = color if color is not UNSET else (255, 255, 255)
        self.border_size = border_size if border_size is not UNSET else 0
        self.original_y = y if y is not UNSET else 0
        self.item_offset_y = 0
        self.caret_height = 0
        self.parent = parent if parent is not UNSET else None
        self.checked = False
        self.disabled = False
        self.hovered = False
        self.selected = False
        width = width if width is not UNSET else 0
        height = height if height is not UNSET else 0
        x = x if x is not UNSET else 0
        y = y if y is not UNSET else 0

        if parent:
            self.rect = pygame.Rect(x + parent.rect.x, y + parent.rect.y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)

    def get_unique_ordered_classes(self, classes):
        return list(OrderedDict.fromkeys(classes).keys())

    def apply_ui_settings(self):
        def get_all_bases(cls):
            bases = list(cls.__bases__)
            for base in bases:
                bases.extend(get_all_bases(base))
            return bases

        # Get the name of the object's class and all its base classes
        all_classes = [self.__class__] + get_all_bases(self.__class__)
        
        # Eliminate duplicate classes by converting the list to a set and back to a list
        all_classes = self.get_unique_ordered_classes(all_classes)

        # Loop over all classes and apply settings
        for base_class in all_classes:
            class_name = base_class.__name__
            if class_name in ui_settings:
                for property_name, default_value in ui_settings[class_name].items():
                    current_value = getattr(self, property_name, UNSET)
                    if current_value is UNSET:
                        setattr(self, property_name, default_value)

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

    def get_rgba(self, color, default_alpha=255):
        if len(color) == 3:
            return (*color, default_alpha)
        return color

    def draw(self, screen):
        if self.image:
            self.draw_9_slice(screen)
        else:
            transparent_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            transparent_surface.fill(self.get_rgba(self.no_image_color))
            screen.blit(transparent_surface, self.rect.topleft)            

    def draw_9_slice(self, screen):
        border = self.border_size
        source_inner_width = self.image.get_width() - 2*border
        source_inner_height = self.image.get_height() - 2*border

        dest_inner_width = max(self.rect.width - 2*border,0)
        dest_inner_height = max(self.rect.height - 2*border,0)

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
    mouse_over_textbox = False
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
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            UITextBox.mouse_over_textbox = True
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
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.is_focused = True
                    self.set_focus(self.focus_manager)
                else:
                    self.is_focused = False
                    if self.end_edit_callback:
                        self.end_edit_callback(self.text)
    

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
    def __init__(self, x, y, width, height, color_clicked_callback=UNSET, parent=UNSET, image=UNSET, border_size=10, padding=0):
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

class UIColoredTextBox(UIElement):
    mouse_over_textbox = False    
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, text=UNSET, font_size=UNSET, text_color=UNSET,
                 cursor_color=UNSET, parent=UNSET, image=UNSET, border_size=UNSET, end_edit_callback=UNSET, is_password_field=UNSET, color=UNSET, enable_color_picker=UNSET):
        self.enable_color_picker = enable_color_picker
        self.text = text if text else ''
        self.font_size = font_size
        self.text_color = text_color
        self.end_edit_callback = end_edit_callback
        self.is_hovered = False
        self.enabled = True
        self.image = image
        self.border_size = border_size
        self.no_image_color = color
        self.parent = parent
        self.width = width
        self.height = height
        self.cursor_color = cursor_color

        self.apply_ui_settings()

        super().__init__(x, y, self.width, self.height, self.parent, self.image, self.no_image_color, self.border_size)     
        
        self.last_cursor_toggle_time = 0
        self.cursor_toggle_interval = 500
        self.cursor_visible = True
        self.end_edit_callback = end_edit_callback

        self.current_color = self.text_color
        self.font = pygame.font.Font(None, font_size)
        self.is_focused = False

        button_height = 30  # Or any other size you'd like
        button_width = 50
        self.color_picker_button = UIButton(width - button_width, 0, button_width, button_height, None, callback=self.pick_color, image=None, border_size=border_size, color=text_color)
        button_height = self.color_picker_button.rect.height
        self.color_picker_button.rect.y = (self.rect.height /2  - button_height/ 2)

        color_picker_x = x + width - button_width + button_width + 5  # 5 pixels to the right of the button
        color_picker_y = 0  # same vertical level as the button
        self.color_picker = UIColorPicker(color_picker_x, color_picker_y, 256, 256, color_clicked_callback=self.update_color, image=image, border_size=border_size, padding=10)
        self.color_picker.is_visible = False  # Initially set to invisible
        self.elements.append(self.color_picker_button)
        self.color_list = [{'index': 0, 'color': self.current_color}]
        self.is_password_field = is_password_field
        # self.set_position(x, y)

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

    def serialize(self):
        state = {
            'text': self.text,
            'colors': self.color_list
        }
        return json.dumps(state)

    def deserialize(self, state_string):
        state = json.loads(state_string)
        self.text = state['text']
        self.color_list = state['color_list']


    def set_parent(self, parent):
        super().set_parent(parent)
        #self.color_picker_button.set_parent(self)

    def pick_color(self, button):
        self.color_picker.is_visible = not self.color_picker.is_visible
        if self.color_picker.is_visible:
            # Update the position of color_picker to be beside the button
            self.color_picker.rect.x = self.color_picker_button.rect.x + self.color_picker_button.rect.width + 5
            self.color_picker.rect.y = self.color_picker_button.rect.y + self.color_picker.rect.height / 2 + self.color_picker_button.rect.height / 2
            self.color_picker.ignore_next_click = True

    def insert_char(self, char):
        self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos += 1

    def add_char(self, char):
            self.insert_char(char)
            for color_change in self.color_list:
                if color_change['index'] >= self.cursor_pos:
                    color_change['index'] += 1

    def remove_char(self):
        if self.cursor_pos > 0:
            self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
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
        super().draw(screen)
        display_text = self.text if not self.is_password_field else '*' * len(self.text)  # Display '*' if it's a password field
        # Handling mouse-over state from UITextBox
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            UIColoredTextBox.mouse_over_textbox = True

        current_color = self.current_color
        x_offset = 0
        cursor_x_offset = 0  # Initialize x offset for the cursor

        for i, char in enumerate(display_text):
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

        if self.enable_color_picker:
            self.color_picker_button.rect.right = self.rect.right
            self.color_picker_button.rect.y = self.rect.y + self.rect.height / 2 - self.color_picker_button.rect.height / 2
            self.color_picker_button.draw(screen)
            if self.color_picker.is_visible:
                self.color_picker.draw(screen)


    def handle_event(self, event):
        self.color_picker_button.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1:                
                # Check if the click is on the color_picker_button
                if self.color_picker_button.rect.collidepoint(x, y):
                    return
                if self.rect.collidepoint(x, y):
                    # Mouse clicked inside the text box, now find the closest character
                    x_offset = 0  # Initialize x_offset
                    closest_char_index = 0  # Initialize closest character index
                    for i, char in enumerate(self.text):
                        char_surface = self.font.render(char, True, (0, 0, 0))  # Dummy color, we just need the dimensions
                        char_width = char_surface.get_width()
                        
                        if x_offset + char_width > x - self.rect.x - 10:  # 10 is the x-padding you set when drawing text
                            break
                        
                        x_offset += char_width
                        closest_char_index = i + 1  # 1-indexed
                        
                    self.cursor_pos = closest_char_index
                    self.update_button_color()

                    self.is_focused = True
                    self.set_focus(self.focus_manager)
                else:
                    self.is_focused = False
                    if self.end_edit_callback:
                        self.end_edit_callback(self.text)                    
                
        if event.type == pygame.KEYDOWN and self.is_focused:
            if event.key == pygame.K_BACKSPACE:
                self.remove_char()
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
                self.update_button_color()
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
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
                self.color_picker_button.no_image_color = color_change['color']
                break

    def add_element(self, element):
        element.set_parent(self)
        self.elements.append(element)
        element.original_y = element.rect.y  # Store the original y-position
        element.focus_manager = self.focus_manager
        if isinstance(element, UITextBox):  # Add only UITextBox elements to the focus manager
            self.focus_manager.add(element)                        



class UIImage(UIElement):
    def __init__(self, x=UNSET, y=UNSET, image=UNSET, parent=UNSET, border_size=UNSET, move_to_bounding_pos=UNSET, callback=UNSET, padding=UNSET, backgroung_image=UNSET):
        self.padding = padding
        self.border_size = border_size
        self.color = (0,0,0,0)
        self.parent = parent
        self.apply_ui_settings()


        super().__init__(x, y, 0,0, self.parent, backgroung_image, self.color, self.border_size, padding=self.padding)

        self.move_to_bounding_pos = move_to_bounding_pos
        self.callback = callback
        if image:
            self.diplay_image = pygame.image.load(image)
            self.bounding_rect = self.get_bounding_rectangle()
            rect = self.diplay_image.get_rect()
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
        screen.blit(self.diplay_image, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_mouse_is_over(event.pos):
                if self.callback:
                    self.callback(self)

    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
        collide = self.rect.collidepoint(adjusted_mouse_pos)
        return collide
    
    def get_bounding_rectangle(self):
        # Initialization
        width, height = self.diplay_image.get_size()
        x1, y1, x2, y2 = width, height, 0, 0

        # Lock the surface for direct pixel access
        self.diplay_image.lock()

        for y in range(height):
            for x in range(width):
                # Get the alpha value of the pixel
                _, _, _, alpha = self.diplay_image.get_at((x, y))
                
                # If the pixel is not transparent
                if alpha > 0:
                    x1 = min(x1, x)
                    y1 = min(y1, y)
                    x2 = max(x2, x)
                    y2 = max(y2, y)

        # Unlock the surface
        self.diplay_image.unlock()

        # If no bounding rectangle is found (empty or fully transparent sprite)
        if x2 < x1 or y2 < y1:
            return None

        # Return as a pygame.Rect object
        return pygame.Rect(x1, y1, x2 - x1 + 1, y2 - y1 + 1)                        

class UILabel(UIImage):
    def __init__(self, x=UNSET, y=UNSET, text=UNSET, parent=UNSET, font_size=UNSET, text_color=UNSET, outline_width=UNSET, outline_color=UNSET, padding=UNSET, font_path=UNSET):
        self.outline_width = outline_width
        self.outline_color = outline_color
        self.text = text
        self.text_color = text_color
        self.font_size = font_size
        self.padding = padding
        self.font_path = font_path

        super().__init__(x, y, None, parent, self.text_color, padding=self.padding) 

        self.font = pygame.font.Font(self.font_path, self.font_size)
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
    mouse_over_button = False
    def __init__(self, x, y, width=UNSET, height=UNSET, text=UNSET, font_size=UNSET, image=UNSET, parent=UNSET,color=UNSET, border_size=UNSET, text_color=UNSET, hover_text_color=UNSET, callback=UNSET, trigger_key=UNSET, padding = UNSET, button_image=UNSET, font_path=UNSET, hover_image=UNSET):
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.hover_text_color = hover_text_color
        self.callback = callback
        self.is_hovered = False
        self.enabled = True
        self.trigger_key = trigger_key
        self.image = image
        self.border_size = border_size
        self.no_image_color = color
        self.parent = parent
        self.width = width
        self.height = height
        self.padding = padding
        self.text_surface = None
        self.button_image = button_image
        self.font_path = font_path
        self.content_offset_x = 0
        self.content_offset_y = 0
        self.hover_image = hover_image
        

        self.apply_ui_settings()

        super().__init__(x, y, self.width, self.height, self.parent, self.image, self.no_image_color, self.border_size, padding=self.padding)


        if self.button_image:
            self.button_image = pygame.image.load(self.button_image)

        self.hover_image_offset_x = 0
        self.hover_image_offset_y = 0
        if self.hover_image and self.image:
            self.hover_image = pygame.image.load(self.hover_image)
            # Calculate the position difference between the two images
            normal_width, normal_height = self.image.get_size()
            hover_width, hover_height = self.hover_image.get_size()

            self.hover_image_offset_x = (hover_width - normal_width) // 2
            self.hover_image_offset_y = (hover_height - normal_height) // 2


        self.font = pygame.font.Font(None, self.font_size)
        self.normal_text_color = self.text_color
        self.normal_hover_image = self.image

    def set_image(self, image_path):
        self.button_image = pygame.image.load(image_path)
        self.adjust()

    def draw(self, screen):
        super().draw(screen)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            UIButton.mouse_over_button = True

        if self.button_image:
            if self.is_hovered and self.hover_image:
                screen.blit(self.button_image, (self.rect.x + self.content_offset_x + self.hover_image_offset_x,
                                             self.rect.y + self.content_offset_y + self.hover_image_offset_x))
            else:
                screen.blit(self.button_image, (self.rect.x + self.content_offset_x,
                                self.rect.y + self.content_offset_y))

        else:
            text_color = self.text_color
            if not self.enabled:
                text_color = (100, 100, 100)
            self.text_surface = self.font.render(self.text, True, text_color)
            text_rect = self.text_surface.get_rect(center=self.rect.center)
            screen.blit(self.text_surface, (text_rect.topleft[0] + self.content_offset_x,
                                            text_rect.topleft[1] + self.content_offset_y))


    def adjust(self):
        self.content_offset_x = 0  # Initialize content offset for X
        self.content_offset_y = 0  # Initialize content offset for Y
        rect = None
        if self.button_image:
            image_x = self.rect.centerx - self.button_image.get_width() // 2
            image_y = self.rect.centery - self.button_image.get_height() // 2

            # Set the position of the button image's rect
            rect = self.button_image.get_rect()
            self.content_offset_x = (self.rect.width - rect.width) // 2
            self.content_offset_y = (self.rect.height - rect.height) // 2

        else:
            self.text_surface = self.font.render(self.text, True, (0, 0, 0))
            rect = self.text_surface.get_rect(center=self.rect.center)  # Center the text within the button

            # Adjust the content offset for centering within the button
            self.content_offset_x = (self.rect.width - rect.width) // 2
            self.content_offset_y = (self.rect.height - rect.height) // 2

        # self.rect.width = rect.width + 2 * self.padding
        # self.rect.height = rect.height + 2 * self.padding

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
            if event.button == 1:
                if self.is_mouse_is_over(event.pos):
                    if self.callback:
                        self.callback(self)

    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
        collide = self.rect.collidepoint(adjusted_mouse_pos)
        return collide

    def on_hover(self):        
        if self.hover_image and self.image:
            self.image = self.hover_image
            self.rect.x -= self.hover_image_offset_x
            self.rect.y -= self.hover_image_offset_y
            self.rect.width += self.hover_image_offset_x * 2
            self.rect.height += self.hover_image_offset_y * 2
            self.border_size += self.hover_image_offset_x

        if not self.button_image:
            self.text_color = self.hover_text_color  # Changing text to white for example
            self.text_surface = self.font.render(self.text, True, self.text_color)

    def on_unhover(self):
        if self.hover_image and self.image:
            self.image = self.normal_hover_image
            self.rect.x += self.hover_image_offset_x
            self.rect.y += self.hover_image_offset_y
            self.rect.width -= self.hover_image_offset_x * 2
            self.rect.height -= self.hover_image_offset_y * 2
            self.border_size -= self.hover_image_offset_x

        if not self.button_image:
            # Resetting any changes made during hovering
            self.text_color = self.normal_text_color  # Changing text back to black
            self.text_surface = self.font.render(self.text, True, self.text_color)

class UIContainer(UIElement):
    def __init__(self, x, y, width=UNSET, height=UNSET, image=UNSET, color=UNSET, border_size=UNSET, padding=UNSET, scrollable=False):
        self.no_image_color = color
        self.is_hovered = False
        self.enabled = True
        self.image = image
        self.border_size = border_size
        self.width = width
        self.height = height
        self.parent = None
        self.padding = padding
        self.min_width = width
        self.min_height = height
        self.apply_ui_settings()
        self.can_handle_events = True 

        super().__init__(x, y, self.width, self.height, None, self.image, self.no_image_color, self.border_size, padding=self.padding)
        self.focus_manager = FocusManager()
        self.scrollable = scrollable
        
        # Initialize Scrollbar Variables
        self.scroll_position = 0  # Scroll position
        self.caret_height = 50  # Initial height of scrollbar
        self.dragging_caret = False  # True if the caret is being dragged
        self.mouse_offset = 0  # Offset from top of caret to mouse        

    def get_max_height(self):
        for element in self.elements:
            if element.rect.bottom > self.rect.bottom:
                return element.rect.bottom - self.rect.top

    def move_by_offset(self, offset_x, offset_y):
        self.rect.x += offset_x
        self.rect.y += offset_y
        self.original_y = self.rect.y
        for element in self.elements:
            element.rect.x += offset_x
            element.rect.y += offset_y 
            element.original_y = element.rect.y       

    def center_on_screen(self, screen_width, screen_height, position_y=UNSET):
        # Calculate the new x and y coordinates for centering the UIMessageBox
        new_x = (screen_width - self.rect.width) // 2
        new_y = (screen_height - self.rect.height) // 2 if position_y == UNSET else position_y
        
        # Calculate the offsets needed to move the child elements
        x_offset = new_x - self.rect.x
        y_offset = new_y - self.rect.y
        
        # Update the x and y coordinates of the UIMessageBox
        self.rect.x = new_x
        self.rect.y = new_y
        self.original_x = self.rect.x
        self.original_y = self.rect.y
        # Update the positions of child elements as well
        for element in self.elements:
            if hasattr(element, 'move_by_offset'):
                element.move_by_offset(x_offset, y_offset)
            else:
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

    def set_position(self, x, y):
        position_delta_x = x - self.rect.x
        position_delta_y = y - self.rect.y
        self.rect.x = x
        self.rect.y = y

        for element in self.elements:
            element.rect.x += position_delta_x
            element.rect.y += position_delta_y
            element.original_x = element.rect.x
            element.original_y = element.rect.y            

    def get_bounding_rectangle(self, padding=0):
        if not self.elements:
            return
        min_x = min([element.rect.x for element in self.elements])
        min_y = min([element.rect.y for element in self.elements])
        max_x = max([element.rect.x + element.rect.width for element in self.elements])
        max_y = max([element.rect.y + element.rect.height for element in self.elements])

        rect = pygame.Rect(0,0,0,0)
        rect.x = min_x - padding
        rect.y = min_y - padding
        new_width = max_x - min_x + 2 * padding
        new_height = max_y - min_y + 2 * padding
        rect.width = max(new_width, self.min_width)
        rect.height = max(new_height, self.min_height)
        if new_width < self.min_width:
            for element in self.elements:
                element.rect.x += (self.min_width - new_width) // 2
        if new_height < self.min_height:
            for element in self.elements:
                element.rect.y += (self.min_height - new_height) // 2
        return rect

    def adjust_to_content(self):
        if not self.elements:
            return    
        self.rect = self.get_bounding_rectangle(self.padding)

    def handle_event(self, event):
        if self.can_handle_events:
            mouse_pos = pygame.mouse.get_pos()
            
            # Handle Scrollbar and Caret Events
            scrollbar_rect = pygame.Rect(self.rect.right - 20, self.rect.y + self.scroll_position, 20, self.caret_height)
            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEBUTTONDOWN :
                if self.scrollable:
                    if event.button == 4:  # Scroll up
                        self.scroll_position = max(self.scroll_position - 50, 0)
                    elif event.button == 5:  # Scroll down
                        self.scroll_position = min(self.scroll_position + 50, self.rect.height - self.caret_height) 
                    elif event.button == 0:
                        if scrollbar_rect.collidepoint(mouse_pos):
                            self.dragging_caret = True
                            self.mouse_offset = mouse_pos[1] - self.rect.y - self.scroll_position    
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_caret = False
                elif event.type == pygame.MOUSEMOTION and self.dragging_caret:
                    new_scroll_position = mouse_pos[1] - self.rect.y - self.mouse_offset
                    max_scroll = self.rect.height - self.caret_height
                    self.scroll_position = min(max(0, new_scroll_position), max_scroll)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.focus_manager.next()  

        for element in self.elements:
            # Update the y-position based on the scroll position
            if self.scrollable:
                element.rect.y = element.original_y - self.scroll_position
            element.handle_event(event)


    def draw(self, screen):
        super().draw(screen)
        # Set the clipping region
        # clip_rect = pygame.Rect(self.rect.x + self.padding, 
        #                         self.rect.y + self.padding, 
        #                         self.rect.width - 2 * self.padding, 
        #                         self.rect.height - 2 * self.padding)
        #pygame.draw.rect(screen, (0, 0, 0), clip_rect, 2)
        #screen.set_clip(clip_rect)
        
        for element in self.elements:
            element.draw(screen)
            #pygame.draw.rect(screen, (0, 0, 0), element.rect, 1)

        # Reset the clipping region
        #screen.set_clip(None)
        
        # Draw Scrollbar and Caret
        if self.scrollable:
            if self.needs_scrollbar():        
                pygame.draw.rect(screen, (0, 0, 0), (self.rect.right - 20, self.rect.y, 20, self.rect.height))
                pygame.draw.rect(screen, (100, 100, 100), (self.rect.right - 20, self.rect.y + self.scroll_position, 20, self.caret_height))

class UIMessageBox(UIContainer):
    def __init__(self, message=UNSET, x=UNSET, y=UNSET, width=UNSET, height=UNSET, ok_callback=UNSET, padding=UNSET, image=UNSET, color=UNSET, border_size=UNSET, font_size=UNSET, screen=UNSET):
        super().__init__(x, y, width, height, padding=padding, image=image, color=color, border_size=border_size)
        self.screen = screen
        self.is_visible = False
        self.message_label = UILabel(0, padding, message, font_size=font_size)
        self.ok_button = UIButton(0, self.message_label.rect.bottom + 20, 100, 40, "OK", callback=self.ok_button_pressed, font_size=font_size)
        
        self.ok_callback = ok_callback
        
        self.add_element(self.message_label)
        self.add_element(self.ok_button)

        self.adjust()

    def ok_button_pressed(self, button):
        self.hide()
        if self.ok_callback:
            self.ok_callback(self)
        
    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)
    
    def show(self, message="", ok_callback=UNSET):
        self.message_label.set_text(message)
        self.ok_callback = ok_callback or self.ok_callback 
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
    def __init__(self,x=UNSET, y=UNSET, width=UNSET, height=UNSET, max_squares_per_row=UNSET, image=UNSET, border_size=UNSET, max_value=UNSET, color1=UNSET, color2=UNSET):
        self.max_value = max_value
        self.current_value = 0
        self.color1 = color1
        self.color2 = color2
        self.width = width
        self.square_height = height
        self.max_squares_per_row = max_squares_per_row
        self.x = x
        self.y = y
        self.apply_ui_settings()        
        super().__init__(self.x, self.y, self.width, self.height, image=self.image, border_size=self.border_size)
        self.square_width = width / max_squares_per_row -1


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
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, text=UNSET, color=UNSET, font=UNSET, icon=UNSET, id = UNSET):
        super().__init__(x, y, width, height, None, None, (0, 0, 0), 0, id = id)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = color
        self.icon = icon
        self.font = font
        self.disabled = False
        self.hovered = False
        self.selected = False

    def draw(self, surface):
        icon_offset = 30  # The space reserved for the icon, whether it exists or not

        if self.selected:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        color = self.text_color
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
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, image=UNSET, icon=UNSET, border_size=UNSET, callback=UNSET):
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
    def __init__(self, x, y, width=UNSET, height=UNSET, column_names=UNSET, column_widths=UNSET, font_size=UNSET, image=UNSET, border_size=UNSET, color=UNSET, padding=UNSET, horizontal_align=UNSET, num_columns=UNSET):
        self.font_size = font_size
        self.text_color = color
        self.is_hovered = False
        self.enabled = True
        self.image = image
        self.border_size = border_size
        self.no_image_color = (0,0,0)
        self.width = width
        self.height = height
        self.parent = None
        self.apply_ui_settings()
        self.num_columns = num_columns
        self.padding = padding
        self.horizontal_align = horizontal_align

        self.apply_ui_settings()
        self.font = pygame.font.Font(None, self.font_size)

        super().__init__(x, y, self.width, self.height, image=self.image, color=self.no_image_color, padding=self.padding)
        self.column_names = column_names
        self.column_widths = column_widths if column_widths else [width // self.num_columns] * self.num_columns         
        self.font = pygame.font.Font(None, self.font_size)


    def adjust_width_to_content(self):
        width = 0
        for i, name in enumerate(self.column_names):
            label_surface = self.font.render(name, True, self.text_color)
            label_rect = (label_surface.get_rect())
            width += label_rect.width      
        self.rect.width = width + 2 * self.padding

    def draw(self, screen):
        super().draw(screen)
        x_offset = 0

        for i, name in enumerate(self.column_names):
            label_surface = self.font.render(name, True, self.text_color)
            label_rect = (label_surface.get_rect())

            if self.horizontal_align == 'left':
                label_rect.x = self.rect.x + x_offset + self.padding
            elif self.horizontal_align == 'center':
                label_rect.x = self.rect.x + x_offset + (self.column_widths[i] / 2 - label_rect.width / 2)
            elif self.horizontal_align == 'right':
                label_rect.x = self.rect.x + x_offset + self.column_widths[i] - label_rect.width - self.padding

            label_rect.y = self.rect.y + self.padding
            # pygame.draw.rect(screen, (255, 255, 255), (label_rect.x, label_rect.y, label_rect.width, label_rect.height), 1)
            # pygame.draw.rect(screen, (255, 255, 255), (self.rect.x + x_offset, self.rect.y, self.column_widths[i], self.rect.height), 1)
            screen.blit(label_surface, label_rect)
            x_offset += self.column_widths[i]


class UIList(UIElement):
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, rows = UNSET, text_color=UNSET,item_height = UNSET, item_selected_callback=UNSET, image=UNSET, border_size=UNSET, padding=UNSET,  num_columns=UNSET, column_widths=UNSET, headers=UNSET, header_font_size=UNSET, header_image=UNSET, header_height=UNSET):
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


class UIPopupBase(UIContainer):
    def __init__(self, x=UNSET, y=UNSET, header_text=UNSET, screen=UNSET, header_config=UNSET, ok_callback=UNSET, ok_buttom_image=UNSET, cancel_button_image=UNSET, padding_header=UNSET):
        self.ok_callback = ok_callback
        self.header_text = header_text
        self.show_header = header_text is not UNSET and header_text is not None and header_text != ""
        self.header_height = header_config.header_height if header_config else UNSET
        self.header_width = header_config.header_width if header_config else UNSET
        self.header_offset_x = header_config.header_offset_x if header_config else UNSET
        self.header_offset_y = header_config.header_offset_y if header_config else UNSET
        self.ok_button_image = ok_buttom_image
        self.cancel_button_image = cancel_button_image
        self.padding_header = padding_header

        self.apply_ui_settings()
        super().__init__(x, y,0,0)
        if self.show_header:
            self.header = UIHeader(self.rect.x + self.header_offset_x, self.rect.top - self.header_height + self.header_offset_y, self.header_width, self.header_height, [self.header_text])
            self.add_element(self.header)

        self.return_result = None
        self.is_visible = False
        self.screen = screen

        self.running = False
        # Inner Container to hold custom UI elements
        #inner_container_height = 300
        self.inner_container = UIContainer(0,0, self.width, UNSET,padding=0, image=None, border_size=0)
        self.inner_container.can_handle_events = False
        # OK and Cancel buttons below the inner_container
        button_width = 64
        button_height = 64
        self.ok_button = UIButton(0,0, button_width, button_height, "OK", callback=self.ok_button_clicked, button_image=self.ok_button_image)
        self.cancel_button = UIButton(0,0, button_width, button_height, "Cancel", callback=self.cancel_button_clicked, button_image=self.cancel_button_image)
        self.add_element(self.inner_container) 
        self.add_element(self.ok_button)
        self.add_element(self.cancel_button)
        
    def add_elements_to_inner_container(self, *elements):
            for element in elements:
                self.inner_container.add_element(element)

    def adjust_to_content(self):
        self.inner_container.adjust_to_content()
        self.rect.width = self.inner_container.rect.width + self.padding * 2

        # Center the inner container on the popup
        old_rect = self.inner_container.rect.copy()
        self.inner_container.rect.x = self.rect.x + self.padding
        self.inner_container.rect.y = self.rect.y + self.padding + self.padding_header
        self.inner_container.original_y = self.inner_container.rect.y
        self.inner_container.rect.width = self.rect.width - self.padding * 2
        delta_x =  self.inner_container.rect.x - old_rect.x
        delta_y =  self.inner_container.rect.y - old_rect.y
        for element in self.inner_container.elements:
            element.rect.x += delta_x
            element.rect.y += delta_y

        # Center the OK and Cancel buttons below the inner container
        self.rect.height = self.inner_container.rect.height + self.ok_button.rect.height /2 + 10 + self.padding * 2

        self.ok_button.adjust()
        self.cancel_button.adjust()

        # Calculate positions for the buttons based on the inner container's width
        button_width = self.ok_button.rect.width
        total_width = 2 * button_width + 2 * self.padding

        # Calculate positions for both buttons to be symmetrical
        x_center = self.rect.x + self.rect.width // 2
        ok_button_x = x_center - total_width // 2
        cancel_button_x = x_center + total_width // 2 - button_width

        # Set the positions for both buttons
        self.ok_button.rect.x = ok_button_x
        self.cancel_button.rect.x = cancel_button_x

        # Set the Y position for both buttons
        button_y = self.rect.bottom - self.ok_button.height / 2
        self.ok_button.rect.y = button_y
        self.cancel_button.rect.y = button_y


    def ok_button_clicked(self, button):
        if self.ok_callback:
            self.ok_callback(button)
        self.return_result = True
        self.hide()

    def cancel_button_clicked(self, button):
        self.return_result = False
        self.hide()

    def handle_events(self, events_list):
        events_list = pygame.event.get() if events_list is None else events_list        
        for event in events_list:
            if event.type == pygame.QUIT:
                self.hide()   

            super().handle_event(event)
            # self.inner_container.handle_event(event)
            # self.ok_button.handle_event(event)
            # self.cancel_button.handle_event(event)

    def show(self, position_y=UNSET):
        self.is_visible = True
        self.running = True
        self.center_on_screen(self.screen.get_width(), self.screen.get_height(), position_y)
        self.adjust_to_content()

    def hide(self):
        self.is_visible = False
        self.running = False

    def draw(self, screen):
        if self.is_visible:
            super().draw(screen)

    def run_frame(self, events_list=UNSET):
        self.handle_events(events_list)
        self.draw(self.screen)
        if not self.running:
            return self.return_result            


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