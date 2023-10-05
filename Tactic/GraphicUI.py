import pygame

class UIElement:
    global_id = 1
    def __init__(self, x, y, width, height, parent = None,image=None, color=(200, 200, 200), border_size=10, id=None, padding=0):
        self.padding = padding
        self.id = self.generate_id() if not id else id
        self.image = None if not image else pygame.image.load(image)  # Replace with the path to your button image
        self.color = color
        self.border_size = border_size
        self.original_y = 0
        self.item_offset_y = 0
        self.caret_height = 0
        self.parent = parent
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

    def generate_id(self):
            id = UIElement.global_id 
            UIElement.global_id += 1
            return id  

    def draw(self, screen):
        if self.image:
            self.draw_9_slice(screen)
        else:
            transparent_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            transparent_surface.fill((*self.color, 100))  # Assuming self.color is an (R, G, B) tuple
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
    def __init__(self, x, y, width, height, text='', font_size=20, text_color=(255, 255, 255), cursor_color=(255, 255, 255), parent=None, image=None, border_size=10, end_edit_callback=None):
        super().__init__(x, y, width, height, parent, image=image, border_size=border_size)
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

    def draw(self, screen):
        super().draw(screen)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(topleft=(self.rect.x + 10, self.rect.y + 10))
        screen.blit(text_surface, text_rect)

        if self.cursor_visible and self.is_focused:
            cursor_x_pos = text_rect.x + text_rect.width
            pygame.draw.line(screen, self.cursor_color, (cursor_x_pos, text_rect.y), (cursor_x_pos, text_rect.y + text_rect.height), 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_focused = True
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
                else:
                    self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                    self.cursor_pos += len(event.unicode)
        

        current_time = pygame.time.get_ticks()
        if current_time - self.last_cursor_toggle_time > self.cursor_toggle_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle_time = current_time


class UIImage(UIElement):
    def __init__(self, x, y, image=None, parent=None,color=(100, 100, 100), border_size=0, move_to_bounding_pos=False, callback=None):
        super().__init__(x, y, 0,0, parent, image, color, border_size)
        self.move_to_bounding_pos = move_to_bounding_pos
        self.callback = callback
        if image:
            self.image = pygame.image.load(image)
            self.bounding_rect = self.get_bounding_rectangle()
            rect = self.image.get_rect()
            self.rect.width = rect.width
            self.rect.height = rect.height
            if self.parent:
                self.rect.x += self.parent.border_size
                self.rect.y += self.parent.border_size

            if move_to_bounding_pos:
                self.rect.x -= self.bounding_rect.x
                self.rect.y -= self.bounding_rect.y


    def world_to_local(self, pos):
        pos[0] -= self.parent.rect.x
        pos[1] -= self.parent.rect.y
        if self.parent:
            pos[0] += self.parent.border_size
            pos[1] += self.parent.border_size

        if self.move_to_bounding_pos:
            pos[0] -= self.bounding_offset[0]
            pos[1] -= self.bounding_offset[1]  
        return pos

    def local_to_world(self, pos):
        pos[0] += self.parent.rect.x
        pos[1] += self.parent.rect.y
        if self.parent:
            pos[0] -= self.parent.border_size
            pos[1] -= self.parent.border_size

        if self.move_to_bounding_pos:
            pos[0] += self.bounding_offset[0]
            pos[1] += self.bounding_offset[1]  
        return pos

    def set_parent(self, parent):
        super().set_parent(parent)
        if self.parent:
            self.rect.x += self.parent.border_size
            self.rect.y += self.parent.border_size        
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
    def __init__(self, x, y, text,  parent=None, font_size=20, text_color=(255, 255, 255), font=None, outline_width=0, outline_color=(0,0,0)):
        super().__init__(x, y, None, parent, text_color) 
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
    def __init__(self, x, y, width, height, text, font_size = 20, image=None, parent=None,color=(100, 100, 100), border_size=10, text_color=(255, 255, 255), hover_text_color=(255, 255, 0), callback=None):
        super().__init__(x, y, width, height, parent, image, color, border_size)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.text_color = text_color
        self.normal_text_color = text_color
        self.hover_text_color = hover_text_color
        self.callback = callback
        self.is_hovered = False
        self.enabled = True

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
        element.set_parent(self)
        self.elements.append(element)


    def remove_element(self, element):
        if element in self.elements:
            self.elements.remove(element)

    def handle_event(self, event):
        for element in self.elements:
            element.handle_event(event)

    def draw(self, screen):
        super().draw(screen)
        for element in self.elements:
            element.draw(screen)


class UIMessageBox(UIPanel):
    def __init__(self,message, x, y, width=400, height=300, ok_callback=None):
        super().__init__(x, y, width, height)
        self.message_label = UILabel(10, 10, message, font_size=20)
        self.rect.width = self.message_label.rect.width + 20
        self.rect.height = self.message_label.rect.height + 20
        self.width = self.rect.width
        self.height = self.rect.height
        self.ok_button = UIButton(10, self.rect.height - 5, self.message_label.rect.width + 20, self.message_label.rect.height + 20, "OK", callback=self._on_ok_pressed)
        self.ok_callback = ok_callback

        # Add these elements to the panel
        self.add_element(self.message_label)
        self.add_element(self.ok_button)

    def _on_ok_pressed(self, btn):
        if self.ok_callback:
            self.ok_callback()
        self.hide()  # Hide the MessageBox

    def show(self):
        # Override UIPanel's show function to do additional setup
        super().show()
        # Additional setup code can go here

    def hide(self):
        # Override UIPanel's hide function to do additional cleanup
        super().hide()
        # Additional cleanup code can go here


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
        self.checked = False
        self.disabled = False
        self.hovered = False
        self.selected = False

    def draw(self, surface):
        icon_offset = 30  # The space reserved for the icon, whether it exists or not

        if self.icon and self.checked:
            # Draw the icon at the left-most part of the ListItem
            icon_rect = self.icon.get_rect()
            # Vertically align the icon by adjusting the y-coordinate
            icon_rect.midleft = (self.rect.x + 10, self.rect.centery)
        
            surface.blit(self.icon, icon_rect)

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


class UIList(UIElement):
    def __init__(self, x, y, width, height, rows = [], text_color=(255, 255, 255),item_height = 50, item_selected_callback=None, image=None, border_size=10, padding=10):
        super().__init__(x, y, width, height, None, image, (0, 0, 0), border_size, padding=padding)
        self.item_selected_callback = item_selected_callback
        self.rect = pygame.Rect(x, y, width, height)
        self.selected_item = None
        self.rows = rows
        self.text_color = text_color
        self.item_height = item_height  # Height of each item
        self.font = pygame.font.Font(None, 36)
        self._rebuild_ui()
        self.hovered_item = None
        self.read_only = False
        self.scroll_position = 0  # The scroll position, starting at 0
        self.scrollbar_width = 20  # Width of the scrollbar
        self.caret_height = 50  # Initial height of the scrollbar caret
        self.dragging_caret = False
        self.item_offset_y = 0
        self.mouse_offset = 0
        self.mouse_button_down = False

    def set_read_only(self, read_only):
        self.read_only = read_only

    def reset_all(self):
        for row in self.rows:
            for item in row:
                item.checked = False
                item.disabled = False
                item.hovered = False
                item.selected = False

    def add_row(self, row_items):
        # Append the row to self.rows
        self.rows.append(row_items)     

    def add_item(self, text, icon=None, color=(255, 255, 255), id=None):
        new_item = ListItem(0, len(self.rows) * self.item_height, self.rect.width, self.item_height, text, color, self.font, icon, id=id)
        new_item.original_y = len(self.rows) * self.item_height
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

        # Handle events for each item in each row
        for row in self.rows:
            for item in row:
                item.handle_event(event)                

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
        if self.rect.collidepoint(mouse_pos):  # Only update hovered_item if the mouse is over the list
            for row in self.rows:
                for item in row:
                    item.rect.y = (item.original_y - self.item_offset_y + self.caret_height / 2)
                    if not over_scroll_bar and item.rect.collidepoint(mouse_pos):
                        self.hovered_item = item
                        break



    def draw(self, screen):
        # screen.fill((0, 0, 0))
        super().draw(screen)
        
        clip_rect = pygame.Rect(self.rect.x + self.padding, 
                                self.rect.y + self.padding, 
                                self.rect.width - 2 * self.padding, 
                                self.rect.height - 2 * self.padding)

        screen.set_clip(clip_rect)


        for row in self.rows:
            for item in row:
                item.draw(screen)
                item.hovered = item == self.hovered_item

                pygame.draw.line(screen, (150, 150, 150), (item.rect.x, item.rect.bottom), 
                                (item.rect.x + self.rect.width, item.rect.bottom), 2)

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
        # Rest of class definition


class UIGridList(UIList):
    def __init__(self, x, y, width, height, num_columns, column_widths, image=None, border_size=10, padding=10):
        super().__init__(x, y, width, height, image=image, border_size=border_size, padding=padding)
        self.num_columns = num_columns
        self.column_widths = column_widths
        self.rows = []  # Each row is a list of UIElements
        self.selected_row = None

    def add_grid_row(self, elements):
        if len(elements) != self.num_columns:
            print("Warning: Number of elements doesn't match the number of columns.")
            return

        # Position the elements correctly based on the column widths
        x_offset = 0
        for i, elem in enumerate(elements):
            elem.rect.x = self.rect.x + x_offset
            elem.rect.y = self.rect.y + len(self.rows) * elem.rect.height  # Stack vertically
            x_offset += self.column_widths[i]

        #self.add_row(elements) 

    def handle_event(self, event):
        super().handle_event(event)

    def draw(self, screen):
        super().draw(screen)


class ScrollBar(UIElement):
    def __init__(self, x, y, width, height, parent_panel, image=None, color=(50, 50, 50), border_size=10):
        super().__init__(x, y, width, height, parent=parent_panel, image=image, color=color, border_size=border_size)
        self.parent_panel = parent_panel
        self.handle = ScrollHandle(0, 0, 20, 20, self)  # Initialize ScrollHandle within this ScrollBar

    def draw(self, screen):
        super().draw(screen)  # Draw the scrollbar background
        self.handle.draw(screen)  # Draw the handle

    def handle_event(self, event):
        self.handle.handle_event(event)  # Let the handle process events


class ScrollHandle(UIElement):
    def __init__(self, x, y, width, height, parent_scrollbar, image=None, color=(150, 150, 150), border_size=10):
        super().__init__(x, y, width, height, parent=parent_scrollbar, image=image, color=color, border_size=border_size)
        self.parent_scrollbar = parent_scrollbar
        self.is_dragging = False
        self.drag_offset = 0

    def draw(self, screen):
        handle_height = self.rect.height  # This can be modified later if needed to adjust the handle's size based on content size
        handle_pos = (self.rect.x, self.rect.y + (self.parent_scrollbar.parent_panel.scroll_pos / (self.parent_scrollbar.parent_panel.content_height - self.parent_scrollbar.parent_panel.rect.height)) * (self.parent_scrollbar.parent_panel.rect.height - handle_height))
        pygame.draw.rect(screen, self.color, (handle_pos[0], handle_pos[1], self.rect.width, handle_height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
                _, mouse_y = event.pos
                self.drag_offset = mouse_y - self.rect.y

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            _, mouse_y = event.pos
            new_y = mouse_y - self.rect.y - self.drag_offset
            self.rect.y = max(min(new_y, self.parent_scrollbar.rect.bottom - self.rect.height), self.parent_scrollbar.rect.top)
            print(f"{new_y},{self.rect.y}")
            relative_scroll = new_y / (self.parent_scrollbar.rect.height - self.rect.height)
            self.parent_scrollbar.parent_panel.scroll_pos = relative_scroll * (self.parent_scrollbar.parent_panel. content_height - self.parent_scrollbar.parent_panel.rect.height)
            self.parent_scrollbar.parent_panel.scroll_pos = max(min(self.parent_scrollbar.parent_panel.scroll_pos, self.parent_scrollbar.parent_panel.content_height - self.parent_scrollbar.parent_panel.rect.height), 0)

# Adjust the ScrollableUIPanel to use the new ScrollBar class
class ScrollableUIPanel(UIPanel):
    def __init__(self, x, y, width, height, image=None, color=(100, 100, 100), border_size=10):
        super().__init__(x, y, width, height, image, color, border_size)
        
        self.scroll_pos = 0  
        self.scroll_speed = 10  
        
        scrollbar_width = 20
        self.scrollbar = ScrollBar( width - scrollbar_width, 0, scrollbar_width, height, self)

    def handle_event(self, event):
        super().handle_event(event)
        if self.content_height > self.rect.height:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    self.scroll_pos = max(self.scroll_pos - self.scroll_speed, 0)
                elif event.button == 5:
                    self.scroll_pos = min(self.scroll_pos + self.scroll_speed, self.content_height - self.rect.height)
        self.scrollbar.handle_event(event)

# This setup separates the logic and visual aspects of the scrollbar and its handle. It also provides a clearer structure and organization for the code

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

# import pygame
# from pygame.locals import QUIT, MOUSEBUTTONUP

# # Assuming UIButton class is defined above...

# pygame.init()

# # Constants
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
# BACKGROUND_COLOR = (50, 50, 50)

# # Callback function for the button
# def button_callback(button):
#     print(f"Button {button.text} pressed!")

# # Initialization
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))          
# pygame.display.set_caption("UIButton Example")
# clock = pygame.time.Clock()

# font = pygame.font.Font(None, 36)

# # Create a panel and a button
# panel = UIPanel(150, 150, 500, 300, image="panel.png", border_size=10)
# for i in range(10):
#     button = UIButton(20, 20 + i*80, 200, 60, f"Button {i}", font, image="Box03.png", callback=button_callback, border_size=22)
#     panel.add_element(button)

# running = True
# while running:
#     screen.fill((60, 60, 60))  # Fill background
    
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         panel.handle_event(event)  # Pass events to the panel which will pass them to its children

#     vertical_gradient(screen, (100, 100, 100), (50, 50, 50))  # Draw a gradient background
#     panel.draw(screen)  # Draw the panel and its child elements

#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()
