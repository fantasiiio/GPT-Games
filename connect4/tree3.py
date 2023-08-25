import pygame
import sys

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
    def __init__(self, root, zoom_level=1.0, canvas_width=1000, canvas_height=1000, label_func=None, color_func=None, select_node_func=None):
        pygame.init()
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
        self.pan_offset = {'x': 0, 'y': 0}

    def draw_node(self, node, x, y):
        self.font = pygame.font.SysFont(None, int(self.initial_font_size * self.zoom_level))
        x = x * self.zoom_level
        y = y * self.zoom_level
        node_width = self.node_width * self.zoom_level
        node_height = self.node_height * self.zoom_level
        
        start_x = x - node_width // 2 + self.pan_offset['x']
        start_y = y - node_height // 2 + self.pan_offset['y']
        end_x = x + node_width // 2 + self.pan_offset['x']
        end_y = y + node_height // 2 + self.pan_offset['y']
        
        label = self.label_func(node)
        color = pygame.Color(self.color_func(node))

        outline_width = 3 if node.selected else 1
        pygame.draw.rect(self.screen, color, (start_x, start_y, end_x, end_y), border_radius=5)
        if node.selected:
            pygame.draw.rect(self.screen, (0, 0, 0), (start_x, start_y, end_x, end_y), outline_width, border_radius=5)

        text_surface = self.font.render(label, True, (0, 0, 0))
        self.screen.blit(text_surface, (x - text_surface.get_width() // 2, y - text_surface.get_height() // 2))

        # Draw up/down arrow for nodes with children
        if node.children:
            arrow_size = 20  # Adjust as needed
            if not node.expanded:
                # Draw up arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [
                    (x, end_y - arrow_size),
                    (x - arrow_size / 2, end_y),
                    (x + arrow_size / 2, end_y)
                ])
            else:
                # Draw down arrow
                pygame.draw.polygon(self.screen, (0, 0, 0), [
                    (x, end_y),
                    (x - arrow_size / 2, end_y - arrow_size),
                    (x + arrow_size / 2, end_y - arrow_size)
                ])

        return x, y



                    
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
                self.canvas.create_line(parent_center[0], parent_center[1] + self.node_height // 2,
                                        child_center[0], child_center[1] - self.node_height // 2)

        return parent_center


    def start_pan(self, event):
        self.panning = True
        self.pan_start_x, self.pan_start_y = event.pos

    def pan(self, event):
        dx = event.pos[0] - self.pan_start_x
        dy = event.pos[0] - self.pan_start_y
        self.pan_offset['x'] += dx
        self.pan_offset['y'] += dy
        self.pan_start_x, self.pan_start_y = event.pos

    def zoom(self, event):
        scale_factor = 1.1
        zoom_factor = 1 / scale_factor if event.y < 0 else scale_factor
        self.zoom_level *= zoom_factor

    def main_loop(self):
        while True:
            self.panning = False
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEWHEEL:
                        self.zoom(event)                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 2:  # Middle mouse button
                        self.start_pan(event)
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 2:  # Middle mouse button
                        self.panning = False
                    elif event.type == pygame.MOUSEMOTION and self.panning:
                        self.pan(event)

                    self.screen.fill((255, 255, 255))  # Fill the background with white
                    self.draw_tree(self.root, self.canvas_width // 2, 0)  # Draw the tree
                    pygame.display.flip()  # Update the display
                    
                    # Event handling
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()


# Main function
def main():
    # Create a sample tree
    root = TreeNode('Root')
    child1 = TreeNode('Child 1')
    child2 = TreeNode('Child 2')
    root.add_child(child1)
    root.add_child(child2)
    
    plotter = TreePlotter(root)
    plotter.main_loop()

if __name__ == "__main__":
    main()
