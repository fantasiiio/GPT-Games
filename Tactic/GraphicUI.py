'''
AstroUI is a Python library for creating user interfaces (UIs) in Pygame. It is designed to be easy to use and flexible, allowing you to quickly implement UIs for your games.

- **UIElement**: 
    - Base class for all user interface (UI) elements in the framework. 
    - Provides fundamental attributes and methods that all UI elements leverage.
    - Includes positioning elements on the screen, drawing the elements onto the Pygame window, and handling user interactions with these elements.
    - Supports 9-slice scaling for images, allowing the UI element to maintain the aspect ratio of the image's corners when scaling.
    - Can be configured with a dictionary object, which maps class names to property names for flexible UI design.

- **FocusManager**:
    - Manages keyboard focus among multiple `UITextBox` elements.
    - Ensures that at any given time, keyboard interactions are only processed by one `UITextBox`.
    - Particularly useful for forms and other UI structures where multiple text input fields are present.

- **UIButton**:
    - Represents a clickable button in the UI.
    - Supports displaying either a text label or an image.
    - Executes a callback function when clicked, providing hover state handling to change its appearance when the mouse cursor is over it.
    - Can be disabled, preventing it from responding to clicks.
    - Allows for a wide range of visual button styles, from text labels to intricate graphics.

- **UITextBox**:
    - Represents a text field that users can type into.
    - Displays the user's input and has the ability to call a callback function when the text content changes.
    - Useful for interactive forms and other user input scenarios.

- **UIContainer**:
    - A container class capable of holding multiple `UIElement` instances.
    - Responsible for relaying events (like mouse clicks or keyboard inputs) to its child elements and orchestrating the drawing of these elements on the screen.

- **UIColorPicker**:
    - A specialized UI element that allows users to select a color from a gradient of options.
    - Useful for customization interfaces where users can choose colors.

- **UIList**:
    - Represents a list of selectable rows.
    - Each row can consist of multiple columns, and each cell in the list can contain different types of controls.
    - Manages keyboard focus between items, handles scrolling if the number of items exceeds the visible space, and displays a scrollbar for easier navigation when the list is scrollable.
    - Supports hover states to highlight the item currently under the cursor.

- **UIHeader**:
    - Typically used to display a title or section heading in the UI.
    - Aids in structuring and organizing the UI.

- **UIManager**:
    - Manages multiple `UIContainer` instances.
    - Provides the ability to create and manage separate screens or views in a game.
    - Essential for games with multiple screens or states.

- **UIPopupBase**:
    - A base class for popup windows in the UI.
    - Provides fundamental functionality such as showing and hiding the popup.
    - Includes a header for displaying a title or message.
    - Contains a dedicated `UIContainer` that can host a variety of UI elements.
    - Includes 'OK' and 'Cancel' buttons, which can be linked with specific callback functions to perform actions when clicked.

- **UILabel**:
    - Represents a static text label in the UI.
    - Capable of displaying a static text string.
    - Typically used for non-interactive text display in the UI.

- **UIProgressBar**:
    - Represents a progress bar.
    - Can visually display a progress value, which can be updated dynamically.
    - Useful in scenarios where you need to show progress or loading status to the user.

Each of these classes can be configured with the `ui_settings` dictionary, which maps class names to dictionaries of property names and values, allowing for flexible configuration of UI elements.
 '''

from collections import OrderedDict
import pygame
from config import *

class Sentinel:
    def __bool__(self):
        return False
UNSET = Sentinel()  # Sentinel object to signify unset attributes
AUTO = Sentinel()  # Sentinel object to signify automatic attribute value

class Anchor:
    LEFT = 1
    RIGHT = 2
    TOP = 4
    BOTTOM = 8

    def __init__(self, control, target=None, flags=0):
        self.control = control
        self.target = target
        self.flags = flags

    def apply(self):
        target_rect = self.target.rect if self.target else self.control.parent.rect

        if self.flags & self.LEFT:
            dx = target_rect.x - self.control.rect.x
            self.control.move_by_offset(dx, 0)
        if self.flags & self.RIGHT:
            dx = target_rect.right - self.control.rect.right
            self.control.move_by_offset(dx, 0)
        if self.flags & self.TOP:
            dy = target_rect.y - self.control.rect.y
            self.control.move_by_offset(0, dy)
        if self.flags & self.BOTTOM:
            dy = target_rect.bottom - self.control.rect.bottom
            self.control.move_by_offset(0, dy)


class UIManager:
    screen = None
    is_active = True
    ui_settings = None
    def __init__(self):
        self.containers = []  # List of containers, in order of Z-position (back to front)
        self.child_managers = []  # List of child managers, in order of Z-position (back to front)



    def show(self):
        self.is_active = True
    
    def hide(self):
        self.is_active = False

    def add_container(self, container):
        self.containers.append(container)

    def remove_container(self, container):
        if container in self.containers:
            self.containers.remove(container)

    def add_child_manager(self, manager):
        self.child_managers.append(manager)

    def remove_child_manager(self, manager):
        if manager in self.child_managers:
            self.child_managers.remove(manager)

    def bring_to_front(self, container):
        if container in self.containers:
            self.containers.remove(container)
            self.containers.append(container)

    def send_to_back(self, container):
        if container in self.containers:
            self.containers.remove(container)
            self.containers.insert(0, container)

    def bring_manager_to_front(self, manager):
        if manager in self.managers:
            self.managers.remove(manager)
            self.managers.append(manager)

    def send_manager_to_back(self, manager):
        if manager in self.managers:
            self.managers.remove(manager)
            self.managers.insert(0, manager)

    def handle_event(self, event):
        if not self.is_active:
            return

        # If no child manager handled the event, give it to the containers
        for container in reversed(self.containers):
            if container.is_visible and container.handle_event(event):
                    return True

        # First, give the event to the child managers
        for manager in reversed(self.child_managers):
            if manager.is_active and manager.handle_event(event):
                return True


        return False  # If no child manager or container handled the event, return False

    def draw(self, screen):
        if not self.is_active:
            return
        for manager in self.child_managers:
            manager.draw(screen)
        # Draw the containers first, then the child managers
        for container in self.containers:
            if container.is_visible:
                container.draw(screen)

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
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, parent=UNSET,image=UNSET, color=UNSET, border_size=UNSET, id=UNSET, padding=UNSET, border_width=UNSET, border_color=UNSET):
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
        self.border_width = border_width
        self.border_color = border_color
        width = width if width is not UNSET and width is not AUTO else 0
        height = height if height is not UNSET and height is not AUTO else 0
        x = x if x is not UNSET and x is not AUTO else 0
        y = y if y is not UNSET and y is not AUTO else 0
        self.focus_manager = None
        if parent:
            self.rect = pygame.Rect(x + parent.rect.x, y + parent.rect.y, width, height)
        else:
            self.rect = pygame.Rect(x, y, width, height)
        self.anchors = []
        self.tooltip = None

    def create_tooltip(self, text):
        self.tooltip = UITooltip(attach_control=self, text=text)

        pass

    def add_anchor(self, target=None, flags=0):
        anchor = Anchor(self, target, flags)
        self.anchors.append(anchor)

    def update_anchor(self):
        for anchor in self.anchors:
            anchor.apply()

    def move_by_offset(self, x_offset, y_offset):
        self.rect.x += x_offset
        self.rect.y += y_offset

    def set_focus_manager(self, focus_manager):
        self.focus_manager = focus_manager

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
            if class_name in UIManager.ui_settings:
                for property_name, default_value in UIManager.ui_settings[class_name].items():
                    current_value = getattr(self, property_name, UNSET)
                    if current_value is UNSET:
                        setattr(self, property_name, default_value)

    def handle_event(self, event):
        if not self.tooltip:
            return False
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.tooltip.visible = True
                return True
            else:
                self.tooltip.visible = False
                return False


    def set_parent(self, parent):
        self.parent = parent
        self.rect.x += parent.rect.x
        self.rect.y += parent.rect.y
        if self.parent:
            self.rect.x += self.parent.padding
            self.rect.y += self.parent.padding
            for element in self.elements:
                if not element.parent:
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
            if self.border_width:
                pygame.draw.rect(transparent_surface, self.get_rgba(self.no_image_color), self.rect, self.border_width)
                screen.blit(transparent_surface, self.rect.topleft)

        if self.tooltip:
            self.tooltip.draw(screen)

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

class UIColorPicker(UIElement):
    def __init__(self, x, y, width, height, color_clicked_callback=UNSET, parent=UNSET, image=UNSET, border_size=10, padding=0):
        super().__init__(x, y, width, height, parent=parent, image=image, border_size=border_size, padding=padding)
        self.color_clicked_callback = color_clicked_callback        
        self.surface = pygame.Surface((width, height))
        self.is_visible = False
        self.ignore_next_click = False
        # Create the color value textbox
        self.color_value_textbox = UITextBox(self.rect.x, self.rect.y + self.rect.height, self.rect.width, 30, font_size=20, enable_color_picker=False)
        self.color_value_textbox.set_text("#000000")        

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

    def set_focus_manager(self, focus_manager):
        self.color_value_textbox.set_focus_manager(focus_manager)
        super().set_focus_manager(focus_manager)
    

    def set_parent(self, parent):
        super().set_parent(parent)
        self.color_value_textbox.set_parent(parent)       

    def draw(self, screen):
        if self.is_visible:

            rect = screen.get_clip()
            screen.set_clip(None)            
            screen.blit(self.surface, (self.rect.x, self.rect.y))

           # Additional code for grayscale and common colors
            column_width = 20  # Width of each column
            y_start = self.rect.y  # Y-coordinate where the columns start
            self.color_value_textbox.rect.x = self.rect.x
            self.color_value_textbox.rect.y = self.rect.y + self.rect.height
            for i, color in enumerate(self.grayscale_colors):
                pygame.draw.rect(screen, color, (self.rect.x + self.rect.width, y_start + i * column_width, column_width, column_width))
            
            for i, color in enumerate(self.common_colors):
                pygame.draw.rect(screen, color, (self.rect.x + self.rect.width + column_width, y_start + i * column_width, column_width, column_width))
            
            self.color_value_textbox.draw(screen)

            screen.set_clip(rect)

    def handle_event(self, event):
        super().handle_event(event)
        if not self.is_visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_click(event)
            return True
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:
                self.handle_mouse_click(event)
                return True
        self.color_value_textbox.handle_event(event)

        return False

    def update_hex_color(self):
        r, g, b = self.currentColor[:3]
        self.color_value_textbox.set_text('#%02x%02x%02x' % (r, g, b))       

    def set_color(self, color):
        self.currentColor = color
        self.update_hex_color()

    def handle_mouse_click(self, event):
        if self.ignore_next_click:
            self.ignore_next_click = False
            return

        x, y = event.pos

        # Check if the click is within the color_value_textbox
        if self.color_value_textbox.rect.collidepoint(x, y):
            return

        # Check if the click is within the color picker area
        surface_width, surface_height = self.surface.get_size()
        
        if 0 <= x - self.rect.x < surface_width and 0 <= y - self.rect.y < surface_height:
            self.currentColor = self.surface.get_at((x - self.rect.x, y - self.rect.y))
            if self.color_clicked_callback:
                self.color_clicked_callback(self.currentColor)
            self.update_hex_color()
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

class UITextBox(UIElement):
    mouse_over_textbox = False    
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, text=UNSET, font_size=UNSET, text_color=UNSET,
                 cursor_color=UNSET, parent=UNSET, image=UNSET, border_size=UNSET, end_edit_callback=UNSET, is_password_field=UNSET, color=UNSET, enable_color_picker=UNSET, selection_color=UNSET, padding=UNSET):
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
        self.enable_color_picker = enable_color_picker
        self.selection_color = selection_color
        self.padding = padding
        self.apply_ui_settings()

        super().__init__(x, y, self.width, self.height, self.parent, self.image, self.no_image_color, self.border_size, padding=self.padding)     
        
        self.last_cursor_toggle_time = 0
        self.cursor_toggle_interval = 500
        self.cursor_visible = True
        self.end_edit_callback = end_edit_callback
        self.selection_start = None
        self.selection_end = None
        self.current_color = self.text_color
        self.font = pygame.font.Font(None, self.font_size)
        self.is_focused = False

        button_height = 30  # Or any other size you'd like
        button_width = 50
        self.color_picker_button = UIButton(width - button_width, 0, button_width, button_height, None, callback=self.pick_color, image=None, border_size=border_size, color=self.text_color)
        button_height = self.color_picker_button.rect.height
        self.color_picker_button.rect.y = (self.rect.height /2  - button_height/ 2)

        color_picker_x = x + width - button_width + button_width + 5  # 5 pixels to the right of the button
        color_picker_y = 0  # same vertical level as the button
        if self.enable_color_picker:
            self.color_picker = UIColorPicker(color_picker_x, color_picker_y, 256, 256, color_clicked_callback=self.set_selection_color, image=image, border_size=border_size, padding=10)
            self.color_picker.set_parent(self)
            self.color_picker.is_visible = False  # Initially set to invisible
        self.elements.append(self.color_picker_button)
        self.color_list = [{'index': 0, 'color': self.current_color}]
        self.is_password_field = is_password_field
        self.cursor_pos = 0
        # self.set_position(x, y)


    def set_selection_color(self, color):
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)

            for i in range(start, end):
                # Remove any existing color change at this index
                self.color_list = [color_change for color_change in self.color_list if color_change['index'] != i]
                # Add the new color
                self.color_list.append({'index': i, 'color': color})

    def set_focus(self, focus_manager):
        try:
            index = focus_manager.focus_group.index(self)
            focus_manager.current_focus_index = index
        except ValueError:
            # This textbox is not in the list of focusable elements
            pass
        
    def set_focus_manager(self, focus_manager):
        self.focus_manager = focus_manager
        if self.enable_color_picker:
            self.color_picker.set_focus_manager(focus_manager)

    def set_text(self, text):
        self.text = text
        self.cursor_pos = len(text)

    def serialize(self):
        # Convert each color in the color_list to a list of RGBA values
        color_list_serializable = [{'index': color_change['index'], 'color': list(color_change['color'])} for color_change in self.color_list]
        state = {
            'text': self.text,
            'colors': color_list_serializable
        }
        return json.dumps(state)
    
    def deserialize(self, state_string):
        if state_string and not state_string.startswith('{'):
            self.text = state_string
        else:
            state = json.loads(state_string)
            self.text = state['text']
            self.color_list = [{'index': change['index'], 'color': pygame.Color(*change['color'])} for change in state['colors']]

    def set_parent(self, parent):
        super().set_parent(parent)
        #self.color_picker_button.set_parent(self)

    def pick_color(self, button):
        self.color_picker.is_visible = not self.color_picker.is_visible
        if self.color_picker.is_visible:
            # Update the position of color_picker to be beside the button
            self.color_picker.rect.x = self.color_picker_button.rect.x + self.color_picker_button.rect.width + 5
            self.color_picker.rect.y = self.color_picker_button.rect.y + self.color_picker.rect.height / 2 + self.color_picker_button.rect.height / 2
            #self.color_picker.ignore_next_click = True

    def insert_char(self, char):
        self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
        self.cursor_pos += 1

    def add_char(self, char):
            self.insert_char(char)
            for color_change in self.color_list:
                if color_change['index'] >= self.cursor_pos:
                    color_change['index'] += 1

    def remove_char(self, mode='backspace'):
        if mode == 'backspace':
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos - 1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif mode == 'delete':
            if self.cursor_pos < len(self.text):
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos + 1:]

        for color_change in self.color_list:
            if mode == 'backspace':
                if color_change['index'] >= self.cursor_pos:
                    color_change['index'] -= 1
            elif mode == 'delete':
                if color_change['index'] > self.cursor_pos:
                    color_change['index'] -= 1


    def update_color(self, color):
        for color_change in self.color_list:
            if color_change['index'] == self.cursor_pos:
                color_change['color'] = list(color)  # convert to list
                self.update_button_color()
                return
        self.color_list.append({'index': self.cursor_pos, 'color': list(color)})  # convert to list
        self.color_list = sorted(self.color_list, key=lambda x: x['index'])
        self.update_button_color()

    def draw(self, screen):
        super().draw(screen)
        display_text = self.text if not self.is_password_field else '*' * len(self.text)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            UITextBox.mouse_over_textbox = True

        current_color = self.current_color
        x_offset = 0
        cursor_x_offset = 0

        if self.selection_start is not None and self.selection_end is not None and self.selection_start != self.selection_end:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            selected_text = self.text[start:end]
            selected_text_width = self.font.size(selected_text)[0]
            selection_x = self.rect.x + 10 + self.font.size(self.text[:start])[0]
            pygame.draw.rect(screen, self.selection_color, pygame.Rect(selection_x, self.rect.y + 10, selected_text_width, self.font.size("A")[1]))

        # Keep track of the last index in color_list
        last_color_index = -1

        for i, char in enumerate(display_text):
            # Update color if index matches a color change point
            for color_change in self.color_list:
                if color_change['index'] == i:
                    current_color = color_change['color']
                    last_color_index = i

            # Reset color back to the original text_color after the color segment
            if i > last_color_index:
                current_color = self.text_color

            char_surface = self.font.render(char, True, current_color)
            char_rect = char_surface.get_rect(topleft=(self.rect.x + self.padding + x_offset, self.rect.y + self.padding))
            screen.blit(char_surface, char_rect)
            x_offset += char_surface.get_width()

            if i == self.cursor_pos - 1:
                cursor_x_offset = x_offset

        current_time = pygame.time.get_ticks()
        if current_time - self.last_cursor_toggle_time > self.cursor_toggle_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle_time = current_time

        if self.cursor_visible and self.is_focused:
            cursor_color = self.cursor_color
            cursor_rect = pygame.Rect(self.rect.x + self.padding + cursor_x_offset, self.rect.y + self.padding, 2, self.font.size("A")[1])
            pygame.draw.rect(screen, cursor_color, cursor_rect)

        if self.enable_color_picker:
            self.color_picker_button.rect.right = self.rect.right
            self.color_picker_button.rect.y = self.rect.y + self.rect.height / 2 - self.color_picker_button.rect.height / 2
            self.color_picker_button.draw(screen)
            if self.color_picker.is_visible:
                self.color_picker.draw(screen)

        #pygame.draw.rect(UIManager.screen, (0,0,0), self.rect ,1)



    def get_mouse_position(self, mouse_pos):
        x, _ = mouse_pos
        x -= (self.rect.x + self.padding)  # Adjust for the textbox's position and padding
        x_offset = 0  # Initialize x_offset

        # Iterate over each character in the text
        for i, char in enumerate(self.text):
            char_surface = self.font.render(char, True, self.current_color)
            char_width = char_surface.get_width()

            # If we've passed the click position, return the current index
            if x_offset + char_width > x:
                return i

            x_offset += char_width

        return len(self.text)


    def replace_selection(self, text):
        if self.selection_start is not None and self.selection_end is not None:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            self.text = self.text[:start] + text + self.text[end:]
            self.cursor_pos = start + len(text)
            self.selection_start = None
            self.selection_end = None

    
    def handle_event(self, event):
        self.color_picker_button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if event.button == 1:
                # Check if the click is on the color_picker_button
                if self.color_picker_button.rect.collidepoint(x, y):
                    return False
                if self.rect.collidepoint(x, y):
                    closest_char_index = self.get_mouse_position(event.pos)
                    self.cursor_pos = closest_char_index
                    self.update_button_color()
                    self.selection_start = None
                    self.selection_end = None
                    # Start the selection
                    self.selection_start = closest_char_index
                    self.selection_end = closest_char_index  # Do not add one here
                    self.is_focused = True
                    self.set_focus(self.focus_manager)
                    return True
                else:
                    self.is_focused = False
                    if self.end_edit_callback:
                        self.end_edit_callback(self.text)
                    return False

        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and self.rect.collidepoint(event.pos):
                closest_char_index = self.get_mouse_position(event.pos)
                self.selection_end = closest_char_index  # Do not add one here
                return True

        if self.is_focused:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT] and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    self.cursor_pos = max(0, min(len(self.text), self.cursor_pos + (1 if event.key == pygame.K_RIGHT else -1)))
                    self.selection_end = self.cursor_pos
                    return True

                else:
                    if event.key == pygame.K_BACKSPACE:
                        if self.selection_start is not None and self.selection_end is not None:
                            self.replace_selection('')
                        else:
                            self.remove_char('backspace')
                        return True

                    elif event.key == pygame.K_DELETE:
                        if self.selection_start is not None and self.selection_end is not None:
                            self.replace_selection('')
                        else:
                            self.remove_char('delete')
                        return True

                    elif event.key == pygame.K_LEFT:
                        self.cursor_pos = max(0, self.cursor_pos - 1)
                        self.update_button_color()
                        return True
                    elif event.key == pygame.K_RIGHT:
                        self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
                        self.update_button_color()
                        return True
                    elif event.unicode:
                        if self.selection_start is not None and self.selection_end is not None:
                            start = min(self.selection_start, self.selection_end)
                            end = max(self.selection_start, self.selection_end)
                            self.text = self.text[:start] + event.unicode + self.text[end:]
                            self.cursor_pos = start + 1
                            self.selection_start = None
                            self.selection_end = None
                        else:
                            self.add_char(event.unicode)
                        return True
        else:
            super().handle_event(event)

        if self.enable_color_picker:
            picked_color = self.color_picker.handle_event(event)
            if picked_color:
                self.set_selection_color(picked_color)

        return False



    def update_button_color(self):
        current_color = self.text_color  # Assuming text_color holds the default color
        
        # Sort the color list based on the index
        sorted_color_list = sorted(self.color_list, key=lambda x: x['index'])
        
        for color_change in sorted_color_list:
            if color_change['index'] <= self.cursor_pos:
                current_color = color_change['color']
            elif color_change['index'] >= self.cursor_pos:
                break  # Exit if we crossed the cursor position

        if self.enable_color_picker:
            self.color_picker_button.no_image_color = current_color
            self.color_picker.set_color(current_color)


    def add_element(self, element):
        element.set_parent(self)
        self.elements.append(element)
        element.original_y = element.rect.y  # Store the original y-position
        element.focus_manager = self.focus_manager
        if isinstance(element, UITextBox):  # Add only UITextBox elements to the focus manager
            self.focus_manager.add(element)                        



class UIImage(UIElement):
    def __init__(self, x=UNSET, y=UNSET, image_file=UNSET, parent=UNSET, border_size=UNSET, move_to_bounding_pos=UNSET, callback=UNSET, padding=UNSET, backgroung_image=UNSET, image=UNSET):
        self.padding = padding
        self.border_size = border_size
        self.color = (0,0,0,0)
        self.parent = parent
        self.apply_ui_settings()


        super().__init__(x, y, 0,0, self.parent, backgroung_image, self.color, self.border_size, padding=self.padding)

        self.move_to_bounding_pos = move_to_bounding_pos
        self.callback = callback
        self.diplay_image = None
        if image_file or image:
            if image_file:
                self.diplay_image = pygame.image.load(image_file)
            elif image:
                self.diplay_image = image
            if move_to_bounding_pos:
                self.bounding_rect = self.get_bounding_rectangle()
            else:
                self.bounding_rect = self.rect
            rect = self.diplay_image.get_rect()
            self.rect.width = rect.width
            self.rect.height = rect.height
            if self.parent:
                self.rect.x += self.parent.padding
                self.rect.y += self.parent.padding

            if move_to_bounding_pos:
                self.rect.x -= self.bounding_rect.x
                self.rect.y -= self.bounding_rect.y

    def scale_image_to_width(self, width):
        # Get the aspect ratio of the original image
        original_width, original_height = self.diplay_image.get_size()
        aspect_ratio = original_height / original_width

        # Calculate the new height based on the aspect ratio and desired width
        new_height = int(width * aspect_ratio)

        # Scale the image
        scaled_image = pygame.transform.scale(self.diplay_image, (width, new_height))
        self.rect.width = width
        self.rect.height = new_height
        self.diplay_image = scaled_image

    def scale_image_to_height(self, height):
        # Get the aspect ratio of the original image
        original_width, original_height = self.diplay_image.get_size()
        aspect_ratio = original_height / original_width

        # Calculate the new height based on the aspect ratio and desired width
        new_width = int(height / aspect_ratio)

        # Scale the image
        scaled_image = pygame.transform.scale(self.diplay_image, (new_width, height))
        self.rect.width = new_width
        self.rect.height = height
        self.diplay_image = scaled_image        


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
        super().draw(screen)
        if self.diplay_image:
            screen.blit(self.diplay_image, (self.rect.x, self.rect.y))

    def handle_event(self, event):
        super().handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_mouse_is_over(event.pos):
                if self.callback:
                    self.callback(self)
                return True

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

        super().__init__(x, y, None, parent, None, padding=self.padding) 
        
        self.color_list = [{'index': 0, 'color': self.text_color}]
        self.font = pygame.font.Font(self.font_path, self.font_size)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surface.get_rect(top=self.rect.top, left=self.rect.left)

    def deserialize(self, state_string):
        if state_string and not state_string.startswith('{'):
            self.text = state_string
        else:
            state = json.loads(state_string)
            self.text = state['text']
            self.color_list = [{'index': change['index'], 'color': pygame.Color(*change['color'])} for change in state['colors']]

    def set_text(self, text):
        self.text = text
        self.color_list = [{'index': 0, 'color': self.text_color}]  # Initialize with default text color
        char_surface = self.font.render(text, True, self.text_color)
        self.rect = char_surface.get_rect()


    def draw(self, screen):
        if not self.font:
            return

        if self.outline_width > 0:
            self.draw_text_with_outline(screen)
        else:
            self.draw_text(screen)

    def draw_text(self, screen):
        x_offset = 0
        current_color = self.text_color  # Initialize with default text color 
        last_color_index = -1  
        
        for i, char in enumerate(self.text):
            for color_change in self.color_list:
                if color_change['index'] == i:
                    current_color = color_change['color']
                    last_color_index = i

            if i > last_color_index:
                current_color = self.text_color

            char_surface = self.font.render(char, True, current_color)
            char_rect = char_surface.get_rect(topleft=(self.rect.x + self.padding + x_offset, self.rect.y + self.padding))
            screen.blit(char_surface, char_rect)
            x_offset += char_surface.get_width()

    def draw_text_with_outline(self, screen):
        x_offset = 0
        current_color = self.text_color
        last_color_index = -1  

        for i, char in enumerate(self.text):
            for color_change in self.color_list:
                if color_change['index'] == i:
                    current_color = color_change['color']
                    last_color_index = i

            if i > last_color_index:
                current_color = self.text_color

            char_surface = self.font.render(char, True, current_color)
            char_rect = char_surface.get_rect(topleft=(self.rect.x + self.padding + x_offset, self.rect.y + self.padding))

            # Draw outline
            outline_alpha_color = (*self.outline_color[:3], 255)
            outline_surface = self.font.render(char, True, outline_alpha_color)

            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    outline_rect = char_rect.move(dx, dy)
                    screen.blit(outline_surface, outline_rect)

            # Draw the actual character
            screen.blit(char_surface, char_rect)
            x_offset += char_surface.get_width()
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

    def reset_hover(self):
        self.on_unhover()

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
        if self.hovered:
            return
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
        super().handle_event(event)

        if not self.enabled:
            return False  

        if event.type == pygame.KEYDOWN:
            if event.key == self.trigger_key:
                if self.callback:
                    self.callback(self)
                    return True 

        if event.type == pygame.MOUSEMOTION:
            if self.is_mouse_is_over(event.pos):
                if not self.is_hovered: 
                    self.on_hover()
                return True 
            else:
                if self.is_hovered:
                    self.on_unhover()
                return False 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.is_mouse_is_over(event.pos):
                    if self.callback:
                        self.callback(self)
                        return True 

        return False 


    def is_mouse_is_over(self, mouse_pos):
        adjusted_mouse_pos = list(mouse_pos)
        
        collide = self.rect.collidepoint(adjusted_mouse_pos)
        return collide

    def on_hover(self):        
        if self.hover_image and self.image and not self.is_hovered:
            self.is_hovered = True
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
        if self.hover_image and self.image and self.is_hovered:
            self.is_hovered = False
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
        self.is_visible = True

        super().__init__(x, y, self.width, self.height, None, self.image, self.no_image_color, self.border_size, padding=self.padding)
        self.focus_manager = FocusManager()
        self.scrollable = scrollable
        
        # Initialize Scrollbar Variables
        self.scroll_position = 0  # Scroll position
        self.caret_height = 50  # Initial height of scrollbar
        self.dragging_caret = False  # True if the caret is being dragged
        self.mouse_offset = 0  # Offset from top of caret to mouse        

    def set_focus_manager(self, focus_manager):
        self.focus_manager = focus_manager
        for element in self.elements:
            element.set_focus_manager(focus_manager)
        

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
        element.set_focus_manager(self.focus_manager)
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
            # super().handle_event(event)

            mouse_pos = pygame.mouse.get_pos()

            # Handle Scrollbar and Caret Events
            scrollbar_rect = pygame.Rect(self.rect.right - 20, self.rect.y + self.scroll_position, 20, self.caret_height)
            # Handle mouse wheel scrolling
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.scrollable:
                    if event.button == 4:  # Scroll up
                        self.scroll_position = max(self.scroll_position - 50, 0)
                        return True
                    elif event.button == 5:  # Scroll down
                        self.scroll_position = min(self.scroll_position + 50, self.rect.height - self.caret_height)
                        return True
                    elif event.button == 0:
                        if scrollbar_rect.collidepoint(mouse_pos):
                            self.dragging_caret = True
                            self.mouse_offset = mouse_pos[1] - self.rect.y - self.scroll_position
                            return True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging_caret = False
                    return True
                elif event.type == pygame.MOUSEMOTION and self.dragging_caret:
                    new_scroll_position = mouse_pos[1] - self.rect.y - self.mouse_offset
                    max_scroll = self.rect.height - self.caret_height
                    self.scroll_position = min(max(0, new_scroll_position), max_scroll)
                    return True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.focus_manager.next()
                    return True

        handled = False
        for element in self.elements:
            # Update the y-position based on the scroll position
            if self.scrollable:
                element.rect.y = element.original_y - self.scroll_position
            if element.handle_event(event):
                handled = True

        return handled


    def draw(self, screen):
        super().draw(screen)
        # Set the clipping region
        # clip_rect = pygame.Rect(self.rect.x + self.padding, 
        #                         self.rect.y + self.padding, 
        #                         self.rect.width - 2 * self.padding, 
        #                         self.rect.height - 2 * self.padding)
        # pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        # screen.set_clip(clip_rect)
        
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

class UITooltip(UIContainer):
    def __init__(self, attach_control=UNSET,x=UNSET, y=UNSET, width=UNSET, height=UNSET, image=UNSET, color=UNSET, border_size=UNSET, padding=UNSET, text=UNSET, font_size=UNSET, text_color=UNSET, font_path=UNSET, screen=UNSET):
        self.attach_control = attach_control
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.font_path = font_path
        self.screen = screen
        super().__init__(attach_control.rect.x, y, width, height, image=image, color=color, border_size=border_size, padding=padding)

        self.message_label = UILabel(0, 0, self.text, font_size=self.font_size, text_color=self.text_color, font_path=self.font_path)
        self.add_element(self.message_label)
        #self.is_visible = False

    def draw(self, screen):
        if not self.is_visible:
            return
        else:
            return super().draw(screen)
    
    def show(self, text=UNSET):
        if text:
            self.message_label.set_text(text)
        self.adjust()
        self.is_visible = True

    def hide(self):
        self.is_visible = False

    def adjust(self):
        super().adjust_to_content()
        self.rect.x = self.attach_control.rect.right + 20
        self.rect.y = self.attach_control.rect.y - self.rect.height /2

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.visible = True
            else:
                self.visible = False     


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
        handled = super().handle_event(event)

        for element in self.elements:
            if element.handle_event(event):
                handled = True

        return handled
    
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
        self.height = height       
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
    def __init__(self, x, y, width=UNSET, height=AUTO, column_names=UNSET, column_widths=UNSET, font_size=UNSET, image=UNSET, border_size=UNSET, text_color=UNSET, padding=UNSET, horizontal_align=UNSET, num_columns=UNSET):
        self.font_size = font_size
        self.text_color = text_color
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


        super().__init__(x, y, self.width, self.height, image=self.image, color=self.no_image_color, padding=self.padding, border_size=self.border_size)
        self.column_names = column_names
        if height == AUTO:
            self.adjust_height_to_content()
        self.column_widths = column_widths if column_widths else [width // self.num_columns] * self.num_columns         
        self.font = pygame.font.Font(None, self.font_size)


    def adjust_height_to_content(self):
        height = 0
        for i, name in enumerate(self.column_names):
            label_surface = self.font.render(name, True, self.text_color)
            label_rect = (label_surface.get_rect())
            height = max(height, label_rect.height)      
        self.rect.height = height + 2 * self.padding

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


class UIScrollBar(UIElement):
    def __init__(self, x, y, width, height, image=UNSET, border_size=UNSET, padding=UNSET, caret_image=UNSET, content_height=UNSET):
        self.scroll_position = 0
        self.dragging_caret = False
        self.mouse_offset = 0
        self.caret_height = None
        self.scrollbar_width = None
        self.padding = padding
        self.item_offset_y = 0
        self.caret_image = caret_image  # Placeholder for a potential image
        self.image = image
        self.border_size = border_size
        self.content_height = height if not content_height else content_height
        self.list_observer = None

        self.apply_ui_settings()
        super().__init__(x, y, width, height, image=self.image, color=self.color, border_size=self.border_size, padding=self.padding)

        if self.image:
            self.scrollbar_width = self.image.get_width()
            self.rect.x -= self.scrollbar_width
            self.rect.width += self.scrollbar_width

        if self.caret_image:
            self.caret_image = pygame.image.load(self.caret_image)
            self.caret_height = self.caret_image.get_height()


    def get_scroll_offset(self):
        return self.item_offset_y

    def on_scroll_update(self):
        self.height_ratio = (self.content_height-self.rect.height+100) / self.rect.height
        self.item_offset_y = self.scroll_position * self.height_ratio - self.parent.padding
        if self.list_observer:
            self.list_observer.on_scroll_update()

    def handle_event(self, event):
        handled = super().handle_event(event)

        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._handle_mouse_down(event, mouse_pos):
                handled = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self._handle_mouse_up(event):
                handled = True
        elif event.type == pygame.MOUSEMOTION:
            if self._handle_mouse_motion(event, mouse_pos):
                handled = True

        return handled


    def _handle_mouse_down(self, event, mouse_pos):
        scroll_increment = 10

        if event.button == 4:  # Scroll up
            self.scroll_position = max(0, self.scroll_position - scroll_increment)
            self.on_scroll_update()  # Call the update method here
        elif event.button == 5:  # Scroll down
            self.scroll_position = min(self.rect.height - self.caret_height, self.scroll_position + scroll_increment)
            self.on_scroll_update()  # Call the update method here

        elif event.button == 1:
            scrollbar_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y + self.scroll_position, self.scrollbar_width, self.caret_height)
            if scrollbar_rect.collidepoint(mouse_pos):
                self.dragging_caret = True
                self.mouse_offset = mouse_pos[1] - self.rect.y - self.scroll_position

    def _handle_mouse_up(self, event):
        self.dragging_caret = False
        #self.on_scroll_update()

    def _handle_mouse_motion(self, event, mouse_pos):
        if self.dragging_caret:
            new_scroll_position = mouse_pos[1] - self.rect.y - self.mouse_offset
            max_scroll = self.rect.height - self.caret_height - self.padding * 2
            self.scroll_position = min(max(-self.padding, new_scroll_position), max_scroll)
            #self.item_offset_y = self.scroll_position * self.height_ratio + 50
            self.on_scroll_update()

    def draw(self, screen):
        super().draw(screen)
        # Draw caret
        if self.caret_image:
            caret_rect = self.caret_image.get_rect()
            screen.blit(self.caret_image, (self.rect.x, self.rect.y + self.scroll_position))
        else:
            caret_rect = pygame.Rect(self.rect.right - self.scrollbar_width, self.rect.y + self.scroll_position, self.scrollbar_width, self.caret_height)
            pygame.draw.rect(screen, (100, 100, 100), caret_rect)

class UIListRow:
    def __init__(self, items, data=None):
        self.items = items
        self.data = data

class UIList(UIElement):
    def __init__(self, x=UNSET, y=UNSET, width=UNSET, height=UNSET, rows = UNSET, text_color=UNSET,item_height = UNSET, item_selected_callback=UNSET, image=UNSET, border_size=UNSET, padding=UNSET,  num_columns=UNSET, column_widths=UNSET, headers=UNSET, header_font_size=UNSET, header_image=UNSET, header_height=UNSET, header_border_size=UNSET, scrollbar_width=UNSET, scrollbar_bg_image=UNSET,scrollbar_bg_border=UNSET, scrollbar_cursor_image=UNSET, scrollbar_cursor_border=UNSET, enable_scrollbar=UNSET):
        self.headers = headers if headers else []

        self.num_columns = num_columns

        self.rows = [] if not rows else rows
        self.item_height = item_height  # Height of each item
        self.text_color = text_color    
        self.header_image = header_image
        self.header_font_size = header_font_size
        self.image = image
        self.padding = padding
        self.border_size = border_size
        self.header_height = header_height
        self.header_border_size = header_border_size
        self.width = width
        self.height = height
        self.scrollbar_width = scrollbar_width
        self.scrollbar_bg_image = scrollbar_bg_image
        self.scrollbar_cursor_image = scrollbar_cursor_image
        self.scrollbar_bg_border = scrollbar_bg_border
        self.scrollbar_cursor_border = scrollbar_cursor_border
        self.enable_scrollbar = enable_scrollbar
        #self._rebuild_ui()

        self.scrollbar_width = scrollbar_width

        self.apply_ui_settings()
        super().__init__(x , y, self.width, self.height, None, self.image, (0, 0, 0), self.border_size, padding=self.padding)
        

        self.column_widths = column_widths if column_widths else [self.width // self.num_columns] * self.num_columns         
        self.total_width = sum(self.column_widths)
        self.hovered_item = None
        self.read_only = False
        self.scroll_position = 0  # The scroll position, starting at 0
        self.caret_height = 50  # Initial height of the scrollbar caret

        if self.enable_scrollbar:
            self.scrollbar = UIScrollBar(0, y + self.padding, 0, height - self.padding * 2, image=self.scrollbar_bg_image, border_size=self.scrollbar_bg_border, caret_image=self.scrollbar_cursor_image)        
            self.scrollbar.parent = self
            self.scrollbar.list_observer = self
            self.scrollbar.on_scroll_update()             


        self.dragging_caret = False
        self.item_offset_y = 0
        self.mouse_offset = 0
        self.mouse_button_down = False
        self.screen = None
        self.item_selected_callback = item_selected_callback
        self.selected_item = None
        if self.headers:
            self.header = UIHeader(0,0,0,AUTO, self.headers, self.column_widths,font_size=self.header_font_size, text_color = self.text_color, image=self.header_image, border_size=self.header_border_size)
            self.header.rect.width = self.total_width + self.padding * 2 + self.scrollbar.rect.width
            self.header.rect.x = self.rect.x
            self.header.rect.y = self.rect.y - self.header.rect.height + 15
            self.header.rect = self.header.rect
            if self.width == AUTO:
                self.rect.width = self.header.rect.width
        else:
            self.header = None

        self.scrollbar.rect.x = x + self.rect.width - self.scrollbar.rect.width - self.padding
    
    def find_row_index_by_data(self, property_name, property_value):
        for index, row in enumerate(self.rows):
            if row.data and property_name in row.data and row.data[property_name] == property_value:
                return index
        return None

    def adjust_width_to_content(self):
        self.rect.width = self.total_width + self.scrollbar.rect.width + self.padding * 2

    def on_scroll_update(self):
        pass

    def move_by_offset(self, x_offset, y_offset):
        super().move_by_offset(x_offset, y_offset)
        for row in self.rows:
            for item in row.items:
                item.move_by_offset(x_offset, y_offset)

        if self.header:
            self.header.move_by_offset(x_offset, y_offset)
        if self.enable_scrollbar:
            self.scrollbar.move_by_offset(x_offset, y_offset)

    def set_read_only(self, read_only):
        self.read_only = read_only

    def reset_all(self):
        for row in self.rows:
            for item in row.items:
                item.checked = False
                item.disabled = False
                item.hovered = False
                item.selected = False

    def add_row(self, elements, data=None):
        row = UIListRow(elements, data)
        self.rows.append(row)
        if len(elements) != self.num_columns:
            print("Warning: Number of elements doesn't match the number of columns.")
            return

        # Position the elements correctly based on the column widths
        x_offset = 0
        y_offset = len(self.rows) * self.item_height  # Stack vertically

        for i, elem in enumerate(elements):
            elem.rect.x = x_offset
            # Bottom align the item in the list row
            elem.rect.y = y_offset + (self.item_height - elem.rect.height)
            elem.original_y = elem.rect.y  # Store the original y-coordinate
            x_offset += self.column_widths[i]  # Increment x-coordinate based on column width
            elem.set_parent(self)  # Set the parent to adjust position accordingly
        
        #self.rows.append(elements)  # Add the row to the list

        self.scrollbar.content_height = (len(self.rows) + 2) * self.item_height

    def clear_rows(self):
        self.rows = []
        self.scrollbar.content_height = 0

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
            for item in row.items:
                list_item = ListItem(0, index * self.item_height, self.rect.width, self.item_height, item.text, item.color, self.font, item.icon)
                list_item.id = item  
                self.rows[index][0] = list_item

    def _item_selected(self, list_item):
        self.selected_item = list_item.id
        for row in self.rows:
            for item in row.items:
                item.selected = item.id == self.selected_item
                if self.item_selected_callback:
                    self.item_selected_callback(item)  

    def remove_item(self, id):
        for index, row in enumerate(self.rows):
            if row[0].id == id:
                del self.rows[index]
                self.scrollbar.content_height = (len(self.rows) + 2) * self.item_height                
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
        handled = super().handle_event(event)

        if self.enable_scrollbar:
            if self.scrollbar.handle_event(event):
                handled = True
            self.item_offset_y = self.scrollbar.item_offset_y

        for row in self.rows:
            for item in row.items:
                if item.handle_event(event):
                    handled = True

        return handled


    def draw(self, screen):
        if self.header:
            self.header.draw(screen)

        super().draw(screen)
        if self.enable_scrollbar:
            # Get the current offset from the scrollbar
            scrollbar_offset = self.scrollbar.get_scroll_offset()
        else:
            scrollbar_offset = 0

        rect = pygame.Rect(self.rect.x + self.padding, 
                            self.rect.y + self.padding, 
                            self.rect.x + self.rect.width - self.padding, 
                            self.rect.height - 2 * self.padding)
        screen.set_clip(rect)
        # Draw each item in the list

        for row in self.rows:
            col_index = 0
            for item in row.items:
                # Apply the scrollbar's offset to the item's position
                adjusted_y = self.rect.y + item.original_y + scrollbar_offset + self.padding

                # Only draw the item if it falls within the visible area of the list
                # if adjusted_y + item.rect.height >= self.rect.y and adjusted_y <= self.rect.y + self.rect.height:
                item.rect.y = adjusted_y  # Update the item's y-coordinate
                item.draw(screen)

                # pygame.draw.rect(screen, (255,255,255), item.rect,1)
                col_index += 1
            
            # Draw line only if its y-coordinate is within the visible area
            line_bottom = item.rect.bottom
            # if line_bottom >= self.rect.y + self.padding and line_bottom <= self.rect.y + self.rect.height - self.padding:
            pygame.draw.line(screen, (200, 200, 200), (self.rect.x + self.padding, line_bottom), (self.rect.x + self.rect.width - self.padding - self.scrollbar.rect.width, line_bottom), 1)


        screen.set_clip(None)            

        if self.enable_scrollbar:
            # Draw the scrollbar
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
        handled = False

        for event in events_list:
            if event.type == pygame.QUIT:
                self.hide()
                handled = True

            if super().handle_event(event):
                handled = True

        return handled


    def show(self, position_y=UNSET):
        self.ok_button.reset_hover()
        self.cancel_button.reset_hover()
        self.is_visible = True
        self.center_on_screen(self.screen.get_width(), self.screen.get_height(), position_y)
        self.adjust_to_content()

    def hide(self):
        self.is_visible = False

    def draw(self, screen):
        if self.is_visible:
            super().draw(screen)          


