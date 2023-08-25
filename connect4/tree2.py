import pygame

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []
        self.expanded = False
        self.initial_visibility = True
        self.visible = True
        self.color = 'white'
        self.total_width = 0
        self.selected = False
        self.path_list = []
        self.data = None

    def set_visible(self, visible):
        self.visible = visible
        self.initial_visibility = visible

    def add_child(self, child_node):
        self.children.append(child_node)

class TreePlotter:
    def __init__(self, root, zoom_level=1.0, window_width=800, window_height=600, label_func=None, color_func=None, select_node_func=None):
        pygame.init()
        pygame.font.init()
        self.zoom_level = zoom_level
        self.initial_font_size = 10
        self.font_scale = zoom_level
        self.last_click_time = 0
        self.double_click_flag = False
        self.select_node_func = select_node_func
        self.color_func = color_func if color_func is not None else (lambda node: 'white')
        self.root = root
        self.window_width = window_width
        self.window_height = window_height
        self.node_width = 100
        self.node_height = 70
        self.vertical_spacing = 50
        self.horizontal_spacing = 20
        self.label_func = label_func if label_func is not None else (lambda node: str(node.value))
        self.selected_node = None
        self.screen = pygame.display.set_mode((window_width, window_height))
        self.clock = pygame.time.Clock()
        self.mouse_position_label = pygame.font.SysFont(None, 20)
        self.show_visible_var = False

        self.show_visible_check_rect = pygame.Rect(window_width - 150, window_height - 50, 20, 20)
    
    def node_click(self, event):
        current_time = pygame.time.get_ticks()

        # Check if the last click was within 300 milliseconds (can adjust this value)
        if current_time - self.last_click_time < 400:
            self.double_click_flag = True
            return  # Do not process this click since it's part of a double-click

        # Reset the last click time
        self.last_click_time = current_time

        # Delay the processing of the single click to check for a subsequent click
        pygame.time.set_timer(pygame.USEREVENT, 400)
        self.process_single_click(event)

    def process_single_click(self, event):
        # If a double-click event has occurred, reset the flag and return
        if self.double_click_flag:
            self.double_click_flag = False
            return
        
        node_rects = self.draw_tree(self.root, 0, 0)
        clicked_node = None
        for rect, node in node_rects.items():
            if rect.collidepoint(event.pos):
                clicked_node = node
                break
        
        if clicked_node is not None:
            for node in self.canvas_nodes.values():
                if node != clicked_node:
                    node.selected = False

            clicked_node.selected = not clicked_node.selected
            self.selected_node = clicked_node
            # Call the callback function if provided
            if self.select_node_func:
                self.select_node_func(clicked_node)
        else:
            for node in self.canvas_nodes.values():
                node.selected = False

        # Refresh the visuals
        self.screen.fill((255, 255, 255))
        self.draw_tree(self.root, 0, 0)
        pygame.display.flip()

    def draw_node(self, node, x, y):
        label = self.label_func(node)
        color = self.color_func(node)
        
        # Adjusting the starting and ending points to center the rectangle on (x, y)
        start_x = x - self.node_width // 2
        start_y = y - self.node_height // 2
        end_x = x + self.node_width // 2
        end_y = y + self.node_height // 2

        outline_width = 3 if node.selected else 1
        rect = pygame.Rect(start_x, start_y, self.node_width, self.node_height)
        pygame.draw.rect(self.screen, color, rect, outline_width)
        text_surface = self.mouse_position_label.render(label, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

        # Draw the up/down arrow for nodes with children
        if node.children:
            arrow_size = 20  # Adjust as needed
            if not node.expanded:
                # Draw the up arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [(x, end_y - arrow_size), (x - arrow_size / 2, end_y), (x + arrow_size / 2, end_y)])
            else:
                # Draw the down arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [(x, end_y), (x - arrow_size / 2, end_y - arrow_size), (x + arrow_size / 2, end_y - arrow_size)])

        return rect

    def draw_tree(self, node, x, y):
        current_y = y
        children_rects = {}

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
                child_rect = self.draw_tree(child, current_x, child_y)
                children_rects[child_rect] = child
                
                # Adjust the current_x by the width of the current child and half the width of the next child
                if idx < len(children_widths) - 1:  # if not the last child
                    current_x += (children_widths[idx] + children_widths[idx + 1]) / 2 + self.horizontal_spacing

        # Draw the parent node at the adjusted x-coordinate.
        parent_rect = self.draw_node(node, current_x, current_y)

        if node.expanded:
            for child_rect in children_rects.keys():
                pygame.draw.line(self.screen, (0, 0, 0), (parent_rect.centerx, parent_rect.bottom), (child_rect.centerx, child_rect.top))

        return children_rects

    def start(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.node_click(event)
                    elif event.button == 2:
                        self.start_pan(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:
                        self.stop_pan(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.update_mouse_position(event)
                elif event.type == pygame.MOUSEWHEEL:
                    self.zoom(event)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.toggle_visible_nodes()

            pygame.display.flip()
            self.clock.tick(30)



def init_tree():
    root_node = TreeNode(1)
    root_node.data = {
        'Item 1': [1,2],
        'Item 2': [1,3,3],
        'Item 3': [0,0,0,0],
        'Item 4': [1,2,1,1,1]
    }
    child1 = TreeNode(2)
    child1.data = {
        'Item 1': [1],
        'Item 2': [0,0],
    }
    child2 = TreeNode(3)
    child3 = TreeNode(4)
    child4 = TreeNode(5)
    for i in range(10, 20):
        tree_node = TreeNode(i)
        tree_node.set_visible(False)
        child1.add_child(tree_node) 
    for i in range(20, 30):
        tree_node = TreeNode(i)
        tree_node.set_visible(True)
        child2.add_child(tree_node) 
    for i in range(30, 40):
        child3.add_child(TreeNode(i))
    for i in range(40, 50):
        tree_node = TreeNode(i)
        if i == 40:
            tree_node.set_visible(True)
        else:
            tree_node.set_visible(False)
        child1.children[0].add_child(tree_node)    

    root_node.add_child(child1)
    root_node.add_child(child2)
    root_node.add_child(child3)
    root_node.add_child(child4)
    return root_node
    
# Usage
root_node = init_tree()
mcts_tree = TreePlotter(root_node)
mcts_tree.start()
