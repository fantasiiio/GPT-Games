import pygame
from pygame import Event
import sys
class TreeNode:
    """
    Class to represent a node in a tree data structure.
    
        Attributes:
            value (any): The data stored in this node.
            children (list): The child nodes of this node.
            expanded (bool): Whether this node is expanded to show children.
            visible (bool): Whether this node is visible.
            color (tuple): The RGB color of this node.
            total_width (int): The total width of this node and its children.
            selected (bool): Whether this node is selected.
            path_list (list): The path from the root node to this node.
            data (any): Any additional data associated with this node.
            pos (tuple): The (x, y) position of this node for drawing.
            index (int): The index of this node in its parent's children list.
        
    """
    def __init__(self, value):
        self.value = value
        self.children = []
        self.expanded = False
        self.initial_visibility = True
        self.visible = True # Don't change this directly, use set_visible() instead
        self.color = (255,255,255) 
        self.total_width = 0
        self.selected = False
        self.path_list = []
        self.data = None
        self.pos = (0,0)
        self.index = 0

    def set_visible(self, visible):
        self.visible = visible
        self.initial_visibility = visible

    def add_child(self, child_node):
        self.children.append(child_node)

class TreePlotter:
    """
    Class to visualize a tree data structure.
    
        Handles drawing, panning, zooming, node selection, etc.
    
        Attributes:
            root (TreeNode): The root node of the tree.
            zoom_level (float): The current zoom level.
            canvas_width (int): Width of the canvas in pixels. 
            canvas_height (int): Height of the canvas in pixels.
            node_width (int): Default width of a node in pixels.
            node_height (int): Default height of a node in pixels.
            vertical_spacing (int): Vertical spacing between nodes. 
            horizontal_spacing (int): Horizontal spacing between nodes.
            label_func (callable): Function to call to get a node's label.
            color_func (callable): Function to call to get a node's color.
            select_node_func (callable): Callback when a node is selected.
            update_view_func (callable): Callback to update the view.
            on_event_func (callable): Callback for events.
        
    """
    def __init__(self, root, zoom_level=1.0, canvas_width=1000, canvas_height=1000, clip_rect = None,label_func=None, color_func=None, select_node_func=None, update_view_func=None, on_event_func=None):
        pygame.init()
        self.clip_rect = clip_rect if clip_rect is not None else pygame.Rect(0,0,canvas_width, canvas_height)

        self.show_hidden_nodes = False
        self.on_event_func = on_event_func
        self.update_view_func = update_view_func
        self.click_counter = 0
        self.last_click_time = 0
        self.double_click_flag = False
        self.node_positions = {}
        self.zoom_level = zoom_level
        self.initial_font_size = 10
        self.font_scale = zoom_level
        self.select_node_func = select_node_func
        self.color_func = color_func if color_func is not None else (lambda node: 'white')
        self.root = root
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.node_width = 100
        self.node_height = 70
        self.vertical_spacing = 50
        self.horizontal_spacing = 20
        self.label_func = label_func if label_func is not None else (lambda node: str(node.value))
        self.screen = pygame.display.set_mode((self.canvas_width, self.canvas_height))
        self.font = pygame.font.SysFont(None, self.initial_font_size)
        self.pan_offset = {'x': self.canvas_width / 2, 'y': self.canvas_height / 2}
        self.fonts = {}
        self.selected_node = None
        #self.update_view(None)
        

    def recursive_toggle_visibility(self, node, visible):
        if not node.initial_visibility:  # Only change nodes that were initially not visible
            node.visible = visible
               
        for child in node.children:
            self.recursive_toggle_visibility(child, visible)        

    def center_node(self, center_node, callback_func, event):
        # Store the old screen position of the clicked node
        old_screen_x, old_screen_y = self.world_to_screen(*center_node.pos)


        callback_func(center_node, event)

        # Draw the tree to get the new positions
        self.draw_tree(self.root, self.canvas_width // 2, 0)

        # Get the new screen position of the clicked node
        new_screen_x, new_screen_y = self.world_to_screen(*center_node.pos)

        # Calculate the delta between the old and new positions
        delta_x = old_screen_x - new_screen_x
        delta_y = old_screen_y - new_screen_y

        # Update the pan offset to keep the clicked node in the same screen position
        self.pan_offset['x'] += delta_x / self.zoom_level
        self.pan_offset['y'] += delta_y / self.zoom_level

        # Update the view
        self.update_view(event)

    def toggle_visibility_callback(self,center_node,  event):
        self.show_hidden_nodes = not self.show_hidden_nodes
        self.recursive_toggle_visibility(self.root, self.show_hidden_nodes)

    def toggle_visible_nodes(self, event):
        self.center_node(self.root, self.toggle_visibility_callback, event)

    def unselect_all_tree(self, node = None, exept_node = None):
        if node is None:
            node = self.root
        node.selected = False
        for child in node.children:
            if child != exept_node:
                self.unselect_all_tree(child)    

    def process_single_click(self, event):
        clicked_node = self.find_closest(event.pos[0], event.pos[1])

        # Unselect all nodes except the clicked node
        self.unselect_all_tree(self.root, exept_node=clicked_node)
        self.screen.fill((255, 255, 255))

        if clicked_node is not None:
            clicked_node.selected = not clicked_node.selected
            self.selected_node = clicked_node
            # Call the callback function if provided
            if self.select_node_func:
                self.select_node_func(clicked_node)
        else:
            self.unselect_all_tree(self.root)

        if self.update_view_func:
            self.update_view_func(event)
        self.redraw_tree_from_cache(self.root)  # Draw the tree

        pygame.display.flip()        # self.update_view(event)


    def get_font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.SysFont(None, size)
        return self.fonts[size]
            
    def draw_node(self, node, x, y):
        font_size = int(self.initial_font_size * self.zoom_level)
        self.font = self.get_font(font_size)
        node.pos = (x, y)        
        # self.font = pygame.font.SysFont(None, int(self.initial_font_size * self.zoom_level))
        
        # Apply zoom level to dimensions
        node_width = self.node_width * self.zoom_level
        node_height = self.node_height * self.zoom_level
        arrow_size = 20 * self.zoom_level

        world_x, world_y = self.world_to_screen(x, y)

        start_x = world_x - node_width // 2
        start_y = world_y - node_height // 2
        end_x = start_x + node_width
        end_y = start_y + node_height
        
        if not node.visible or start_x > self.clip_rect.bottomright[0] or end_x < self.clip_rect.x or start_y > self.clip_rect.bottomright[1] or end_y < self.clip_rect.y:
            return x, y  # Skip drawing if the node is outside of the screen


        label = self.label_func(node)
        color = pygame.Color(self.color_func(node))

         # Draw the filled rectangle
        if color != (255,255,255):
            pygame.draw.rect(self.screen, color, (start_x, start_y, node_width, node_height), 0)

        # If the node is selected, draw an outline
        outline_color = (0, 0, 0)  # Black by default
        if node.selected:
            outline_color = (255, 0, 0)  # Red if selected

        outline_width = 5 * self.zoom_level if node.selected else 1


        # Draw the rectangle outline with the appropriate color
        pygame.draw.rect(self.screen, outline_color, (start_x, start_y, node_width, node_height), int(outline_width))
        
        if(5 * self.zoom_level) > 1:
            text_surface = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text_surface, (world_x - text_surface.get_width() // 2, world_y - text_surface.get_height() // 2))

        # Draw up/down arrow for nodes with children
        if node.children:
            if not node.expanded:
                # Draw up arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [
                    (world_x, end_y - arrow_size),
                    (world_x - arrow_size / 2, end_y),
                    (world_x + arrow_size / 2, end_y)
                ])
            else:
                # Draw down arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [
                    (world_x, end_y),
                    (world_x - arrow_size / 2, end_y - arrow_size),
                    (world_x + arrow_size / 2, end_y - arrow_size)
                ])
                
        self.node_positions[node] = (x, y)
        return x, y

    def get_children_width(self, node):
        total_width = 0
        visible_children_count = 0  # Track the number of visible children
        
        # Check if the node has children
        if not node.children:
            return self.node_width  # Return the width of a single node if it has no children

        # Loop through all children to calculate their widths and count visible children
        for child in node.children:
            if child.visible:  # Only count visible nodes
                visible_children_count += 1  # Increment the count of visible children

                if child.expanded and child.children:
                    # If the child node is expanded and has children,
                    # recursively calculate its width
                    child_width = self.get_children_width(child)
                else:
                    # If the child node is not expanded or has no children,
                    # its width is just the node_width
                    child_width = self.node_width

                # Add the child width to the total width
                total_width += child_width

        # Add spacing between children
        total_width += self.horizontal_spacing * (max(visible_children_count - 1, 0))

        return total_width


    def world_to_screen(self, x, y):
        return (x + self.pan_offset['x']) * self.zoom_level, (y + self.pan_offset['y']) * self.zoom_level

    def screen_to_world(self, x, y):
        return (x / self.zoom_level - self.pan_offset['x']), (y / self.zoom_level - self.pan_offset['y'])

    def liang_barsky(self, x1, y1, x2, y2, x_min, y_min, x_max, y_max):
        # Initialize parameters t0 and t1
        t0, t1 = 0.0, 1.0

        dx = x2 - x1
        dy = y2 - y1

        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]

        for i in range(4):
            if p[i] == 0:
                # Line is parallel to the clipping window boundary
                if q[i] < 0:
                    return None  # Line is outside the window, reject
            else:
                t = q[i] / p[i]
                if p[i] < 0:
                    # Line is entering the window
                    t0 = max(t0, t)
                else:
                    # Line is leaving the window
                    t1 = min(t1, t)

        if t0 <= t1:
            # Compute the clipped line segment endpoints
            x1_clip = x1 + t0 * dx
            y1_clip = y1 + t0 * dy
            x2_clip = x1 + t1 * dx
            y2_clip = y1 + t1 * dy
            return x1_clip, y1_clip, x2_clip, y2_clip
        else:
            return None  # Line is outside the window, reject

    # # Example usage:
    # clipped_line = liang_barsky(0, 0, 10, 10, 2, 2, 8, 8)
    # if clipped_line:
    #     x1_clip, y1_clip, x2_clip, y2_clip = clipped_line
    #     print(f"Clipped line coordinates: ({x1_clip}, {y1_clip}) to ({x2_clip}, {y2_clip})")
    # else:
    #     print("Line is outside the clipping window.")

    def draw_line_clipped(self, surface, color, start_pos, end_pos, arrow_length=10, arrow_width=5):
        # Existing code for line clipping and drawing
        rect_top_left_x, rect_top_left_y = self.clip_rect.x, self.clip_rect.y
        rect_bottom_right_x, rect_bottom_right_y = self.clip_rect.bottomright[0], self.clip_rect.bottomright[1]
        start_x, start_y = start_pos
        end_x, end_y = end_pos
        screen_start_x, screen_start_y = self.world_to_screen(start_x, start_y)
        screen_end_x, screen_end_y = self.world_to_screen(end_x, end_y)
        visible_line = self.liang_barsky(screen_start_x, screen_start_y, screen_end_x, screen_end_y, rect_top_left_x, rect_top_left_y, rect_bottom_right_x, rect_bottom_right_y)
        
        if visible_line:
            clipped_x1, clipped_y1, clipped_x2, clipped_y2 = visible_line
            pygame.draw.line(surface, color, (clipped_x1, clipped_y1), (clipped_x2, clipped_y2))

            # Calculate normalized direction vector
            dx = clipped_x2 - clipped_x1
            dy = clipped_y2 - clipped_y1
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length == 0:
                return  # Avoid division by zero

            dx /= length
            dy /= length

            # Calculate arrowhead points
            arrow_length *= self.zoom_level
            arrow_width *= self.zoom_level
            arrow_x1 = clipped_x2 - arrow_length * dx + arrow_width * dy
            arrow_y1 = clipped_y2 - arrow_length * dy - arrow_width * dx
            arrow_x2 = clipped_x2 - arrow_length * dx - arrow_width * dy
            arrow_y2 = clipped_y2 - arrow_length * dy + arrow_width * dx

            # Draw the arrowhead
            pygame.draw.polygon(surface, color, [(clipped_x2, clipped_y2), (arrow_x1, arrow_y1), (arrow_x2, arrow_y2)])



    def redraw_tree_from_cache(self, node):
        if not node.visible:
            return  # Skip invisible nodes
        
        # Redraw the node using the cached position
        self.draw_node(node, *node.pos)
        
        # Draw lines to children if the node is expanded
        if node.expanded:
            for child in node.children:
                if child.visible:
                    # Adjust starting and ending points to consider the size of nodes
                    start_x = node.pos[0]
                    start_y = node.pos[1] + self.node_height // 2  # bottom center of the node
                    end_x = child.pos[0]
                    end_y = child.pos[1] - self.node_height // 2  # top center of the child node
                    
                    # Draw a line from this node's adjusted position to each visible child's adjusted position
                    self.draw_line_clipped(self.screen, (0,0,0), (start_x, start_y), (end_x, end_y))
                    
                    # Recursively redraw the child
                    self.redraw_tree_from_cache(child)


    def draw_tree(self, node, x, y):
        current_y = y
        children_positions = []

        # Step 1: Loop through all children to calculate their widths
        children_widths = []
        for child in node.children:
            if (not child.expanded or not child.children) and child.visible:
                children_widths.append(self.node_width)
            elif child.visible and child.children:
                child_width = self.get_children_width(child)
                children_widths.append(child_width)
            else:
                children_widths.append(0)

        # Calculate total width of all children
        visible_children_count = sum(1 for child in node.children if child.visible)
        total_children_width = sum(children_widths) + self.horizontal_spacing * (max(visible_children_count - 1, 0))

        # Initial x-coordinate for the first child
        current_x = x - total_children_width / 2 + self.node_width / 2

        # Step 2: Loop through children again to position them based on their widths
        if node.expanded:
            child_y = current_y + self.vertical_spacing + self.node_height
            for idx, child in enumerate(node.children):
                if not child.visible:
                    continue
                child_center = self.draw_tree(child, current_x, child_y)
                children_positions.append(child_center)
                
                # Adjust the current_x by the width of the current child and half the width of the next child
                if idx < len(children_widths) - 1:  # if not the last child
                    current_x += (children_widths[idx] + children_widths[idx + 1]) / 2 + self.horizontal_spacing

        # Draw the parent node at the adjusted x-coordinate.
        parent_center_x = (children_positions[0][0] + children_positions[-1][0]) / 2 if children_positions else x
        parent_center = self.draw_node(node, parent_center_x, current_y)

        if node.expanded:
            for child_center in children_positions:
                self.draw_line_clipped(self.screen, (0,0,0), (parent_center[0], parent_center[1] + self.node_height // 2),
                                        (child_center[0], child_center[1] - self.node_height // 2))

        return parent_center


    def start_pan(self, event):
        self.panning = True
        self.pan_start_x, self.pan_start_y = event.pos

    def pan(self, event):
        dx = event.pos[0] - self.pan_start_x
        dy = event.pos[1] - self.pan_start_y
        self.pan_offset['x'] += dx  / self.zoom_level
        self.pan_offset['y'] += dy  / self.zoom_level
        self.pan_start_x, self.pan_start_y = event.pos
        self.update_view(event)

    def zoom(self, event):
        scale_factor = 1.1
        zoom_factor = 1 / scale_factor if event.y < 0 else scale_factor

        # Get the current mouse position in screen coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Convert to world coordinates before zooming
        mouse_pos_before_x = (mouse_x / self.zoom_level - self.pan_offset['x'])
        mouse_pos_before_y = (mouse_y / self.zoom_level - self.pan_offset['y'])

        # Update the zoom level
        self.zoom_level *= zoom_factor

        # Convert to world coordinates after zooming
        mouse_pos_after_x = (mouse_x / self.zoom_level - self.pan_offset['x'])
        mouse_pos_after_y = (mouse_y / self.zoom_level - self.pan_offset['y'])

        # Update the pan offset to keep the mouse position fixed in world coordinates
        self.pan_offset['x'] = self.pan_offset['x'] - (mouse_pos_before_x - mouse_pos_after_x)
        self.pan_offset['y'] = self.pan_offset['y'] - (mouse_pos_before_y - mouse_pos_after_y)
        self.update_view(event)

    def update_view(self, event):   
        self.screen.fill((255, 255, 255))
        self.redraw_tree_from_cache(self.root)  # Draw the tree

        if self.update_view_func:
            self.update_view_func(event)

        pygame.display.flip()

        
    def node_double_click(self, event):
        clicked_node = self.find_closest(event.pos[0], event.pos[1])
        if clicked_node is None:
            return

        # Store the old screen position of the clicked node
        old_screen_x, old_screen_y = self.world_to_screen(*clicked_node.pos)

        # Expand or collapse the node
        if pygame.key.get_mods() & pygame.KMOD_SHIFT:
            self.expand_all(not clicked_node.expanded, clicked_node)
        else:
            self.toggle_expand(clicked_node)

        # Draw the tree to get the new positions
        self.draw_tree(self.root, self.canvas_width // 2, 0)

        # Get the new screen position of the clicked node
        new_screen_x, new_screen_y = self.world_to_screen(*clicked_node.pos)

        # Calculate the delta between the old and new positions
        delta_x = old_screen_x - new_screen_x
        delta_y = old_screen_y - new_screen_y

        # Update the pan offset to keep the clicked node in the same screen position
        self.pan_offset['x'] += delta_x / self.zoom_level
        self.pan_offset['y'] += delta_y / self.zoom_level

        # Update the view
        self.update_view(event)

    def find_closest(self, x, y):
        screen_x, screen_y = self.screen_to_world(x, y)
        for node, (node_x, node_y) in self.node_positions.items():
            if abs(node_x - screen_x) < self.node_width // 2 and abs(node_y - screen_y) < self.node_height // 2:
                return node
        return None
    
    def toggle_expand(self, node):
        if node is None:
            return
        node.expanded = not node.expanded 

    def expand_all(self, expanded, node = None):
        if node.children:
            node.expanded = expanded

        for child in node.children:
            self.expand_all(expanded, child)
                


    def main_loop(self):
        mouse_font = pygame.font.SysFont(None, 20)
        mouse_position_surface = mouse_font.render("0,0", True, (0, 0, 0))
        self.panning = False
        running = True
        while running:

            for event in pygame.event.get():           

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                    self.click_counter += 1
                    if self.click_counter == 1:
                        pygame.time.set_timer(pygame.USEREVENT, 300)
                    elif self.click_counter == 2:
                        self.node_double_click(event)
                        self.click_counter = 0
                        pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop the timer

                if event.type == pygame.USEREVENT:
                    if self.click_counter == 1:
                        x, y = pygame.mouse.get_pos()
                        event_data = {'button': 1,
                                'pos': (x, y)}
                        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, event_data)
                        self.process_single_click(event)
                        pygame.time.set_timer(pygame.USEREVENT, 0)
                    self.click_counter = 0


                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    # sys.exit()
                                
                if event.type == pygame.MOUSEWHEEL:
                    self.zoom(event)                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle mouse button
                    self.start_pan(event)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:  # Middle mouse button
                    self.panning = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.panning:
                        self.pan(event)
                    mouse_x, mouse_y = event.pos
                    world_mouse_x = (mouse_x - self.pan_offset['x']) / self.zoom_level
                    world_mouse_y = (mouse_y - self.pan_offset['y']) / self.zoom_level
                    mouse_position_text = f"X: {int(world_mouse_x)}, Y: {int(world_mouse_y)}"
                    mouse_position_surface = mouse_font.render(mouse_position_text, True, (0, 0, 0))
                
                if self.on_event_func:
                    self.on_event_func(event)


                    

def generate_tree(depth, num_children, value_prefix="Node"):
    def create_node(level, value_prefix):
        # Base case: if the maximum depth is reached, return None
        if level > depth:
            return None

        # Create a node with a value based on its level and index
        value = f"{value_prefix} {level}"
        node = TreeNode(value)

        # Recursively add children to the current node
        for i in range(num_children):
            child_node = create_node(level + 1, f"{value_prefix} {level}.{i}")
            if child_node:
                node.add_child(child_node)

        return node

    return create_node(1, value_prefix)

def generate_tree(depth, num_children):
    def create_node(level, path = []):
        # Base case: if the maximum depth is reached, return None
        if level > depth:
            return None

        # Create a node with a value based on its level and index
        value = f"Level-{path[-1] if path else 0}\n{' '.join(map(str, path))}"
        node = TreeNode(value)

        # Recursively add children to the current node
        for i in range(num_children):
            child_node = create_node(level + 1, path + [i])
            if child_node:
                node.add_child(child_node)

        return node

    return create_node(1)

# root_node = generate_tree(13,2)
# mcts_tree = TreePlotter(root_node, canvas_width=1000, canvas_height=1000)
# # mcts_tree.expand_all(True, root_node)
# mcts_tree.update_view(None)
# mcts_tree.main_loop()
