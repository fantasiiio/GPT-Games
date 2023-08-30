import random
import pygame
import pygame_gui
from tree3 import TreeNode, TreePlotter

testing = True

selection_list_clicked = pygame.USEREVENT + 1
testing = False

class MCTSTree:
    def __init__(self, root_node=None):
        pygame.init()
        self.show_hidden_nodes = False
        # Constants
        self.WIDTH, self.HEIGHT = 1000, 1000
        self.PANEL_WIDTH = 200

        # Create screen and clock
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('MCTS Tree with Panel')
        self.clock = pygame.time.Clock()

        # Initialize pygame_gui manager
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        

        # Create list box
        list_box_rect = pygame.Rect(self.WIDTH - self.PANEL_WIDTH + 10, 10, self.PANEL_WIDTH - 20, self.HEIGHT - 20)
        self.list_box = pygame_gui.elements.UISelectionList(relative_rect=list_box_rect,
                                                            item_list=[],
                                                            manager=self.manager)

        # Create toggle button for showing/hiding nodes
        toggle_button_rect = pygame.Rect(self.WIDTH - self.PANEL_WIDTH + 30, self.HEIGHT - 50, 150, 20)
        self.toggle_button = pygame_gui.elements.UIButton(relative_rect=toggle_button_rect,
                                                        text='Show Hidden Nodes',
                                                        manager=self.manager)

        self.root_node = root_node
        self.plotter = TreePlotter(self.root_node, 0.5, canvas_width=self.WIDTH, canvas_height=self.HEIGHT, 
                                   label_func=self.custom_label, color_func=self.custom_color, select_node_func=self.node_selected, update_view_func=self.update_view, on_event_func=self.on_event)
        
        self.plotter.screen = self.screen  # pass the screen object to your TreePlotter

    def on_event(self, event):
        self.manager.process_events(event)
        self.manager.update(0)

        if event.type ==  pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.toggle_button:
                self.plotter.toggle_visible_nodes(event)

        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.list_box:
                    selected_list = [item for item in self.list_box.item_list if item['selected']]
                    if selected_list:
                        selected_item = selected_list[0]
                        self.on_select_list_item(selected_item)

    def update_view(self, event):
        self.manager.draw_ui(self.screen)       
        pygame.display.update()


    def node_selected(self, node): 
        if not node.data:
            return
        
        # Update the list box with new items.
        self.list_box.set_item_list([str(item) for item in node.data])
        
        # Attach the node object as 'data' to each item.
        for i, item in enumerate(self.list_box.item_list):
            item['data'] = node.data[i]

    testing = False
    if testing:
        def custom_label(self, node):
            return f"{node.value}"

        def custom_color(self, node):
            return 'white'
    else:
        def custom_label(self, node):
            return f"c{node.value.last_move} W:{node.value.win_count[1]},{node.value.win_count[2]} t:{node.value.win_count[2]-node.value.win_count[1]} \nQ: {int(node.value.Q[1])},{int(node.value.Q[2])} N: {node.value.N[1]},{node.value.N[2]}\nD: {node.value.depth} P: {node.value.player}\nR: {node.value.reward[1]:.1f}, {node.value.reward[2]:.1f} RT: {node.value.total_reward[1]:.1f}, {node.value.total_reward[2]:.1f}"


    def custom_color(self, node):
        
        if node.value._is_terminal:
            if node.value.winner == 1:
                return (0, 0, 255)  # Blue
            elif node.value.winner == 2:
                return (255, 0, 0)  # Red
        elif not node.value.visited:
            return (128, 128, 128)  # Gray
        elif node.data:
            return (144, 238, 144)  # Light green, equivalent to '#90EE90'
        else:
            return (255, 255, 255)  # White


    def select_path(self, node, path):
        node.selected = True
        node.expanded = True

        # Find the child node with the matching last_move
        if len(path) <= 1:
            return
        move_to_match = path[1]
        matching_child = next((child for child in node.children if child.index == move_to_match), None)
        
        if matching_child:
            self.select_path(matching_child, path[1:])

    def deselect_all(self, node=None):
        if node is None:
            node = self.root_node
        node.selected = False
        for child in node.children:
            self.deselect_all(child)

    def on_select_list_item(self, selected_item):
        self.deselect_all()
        self.select_path(self.plotter.selected_node, selected_item["data"])
        self.plotter.update_view(None)




    def start(self):
        self.plotter.main_loop()


def generate_tree(max_depth, num_children):
    def create_node(level, path = []):
        # Base case: if the maximum depth is reached, return None
        if level > max_depth:
            return None            

        # Create a node with a value based on its level and index
        value = f"Level-{path[-1] if path else 0}\n{' '.join(map(str, path))}"
        node = TreeNode(value)

        if level > 5:
            node.set_visible(False)

        node.data =  [[random.randint(0, 1) for _ in range(max_depth - level + 1)]]
        # Recursively add children to the current node
        for i in range(num_children):
            child_node = create_node(level + 1, path + [i])
            if child_node:
                child_node.index = i
                node.add_child(child_node)

        return node

    return create_node(1)


def init_tree():
    root_node = generate_tree(8, 2)
    return root_node
    
# Usage
# root_node = init_tree()
# mcts_tree = MCTSTree(root_node)
# mcts_tree.start()
