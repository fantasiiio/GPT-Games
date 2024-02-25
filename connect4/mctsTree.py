import numpy as np
import random
import pygame
import pygame_gui
from tree3 import TreeNode, TreePlotter

testing = True

selection_list_clicked = pygame.USEREVENT + 1
testing = False

class MCTSTree:
    """
    MCTSTree class to visualize an MCTS tree using pygame.
    
    Attributes:
      - root_node: Root node of the tree 
      - show_hidden_nodes: Whether to show nodes marked as hidden
      - WIDTH, HEIGHT: Dimensions of the pygame screen
      - PANEL_WIDTH: Width of the side panel
      - screen: Pygame screen surface
      - clock: Pygame clock 
      - manager: Pygame GUI manager
      - list_box: List box UI element to show node data
      - toggle_button: Button to toggle showing hidden nodes
      - plotter: TreePlotter instance to handle rendering the tree
    
    Methods:
      - __init__: Initialize the pygame screen, GUI elements, and tree plotter
      - on_event: Handle pygame events
      - update_view: Redraw the screen
      - node_selected: Callback when a node is clicked, updates the list box
      - custom_label: Custom node label formatter 
      - custom_color: Custom node color formatter
      - draw_board: Draw a board visualization 
      - draw_legend: Draw the legend for node colors
      - select_path: Select a path in the tree
      - deselect_all: Deselect currently selected nodes
      - on_select_list_item: Callback when list box item is selected
      - start: Start the main loop
    
    """
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
        list_box_rect = pygame.Rect(self.WIDTH - self.PANEL_WIDTH, 0, self.PANEL_WIDTH , self.HEIGHT)
        self.list_box = pygame_gui.elements.UISelectionList(relative_rect=list_box_rect,
                                                            item_list=[],
                                                            manager=self.manager)

        # Create toggle button for showing/hiding nodes
        toggle_button_rect = pygame.Rect(self.WIDTH - self.PANEL_WIDTH + 30, self.HEIGHT - 50, 150, 20)
        self.toggle_button = pygame_gui.elements.UIButton(relative_rect=toggle_button_rect,
                                                        text='Show Hidden Nodes',
                                                        manager=self.manager)

        self.root_node = root_node
        self.plotter = TreePlotter(self.root_node, 0.5, canvas_width=self.WIDTH, canvas_height=self.HEIGHT, clip_rect=pygame.Rect(0,0,self.WIDTH - self.PANEL_WIDTH, self.HEIGHT)
,
                                   label_func=self.custom_label, color_func=self.custom_color, select_node_func=self.node_selected, update_view_func=self.update_view, on_event_func=self.on_event)
        
        self.plotter.screen = self.screen  # pass the screen object to your TreePlotter
        self.plotter.update_view(None)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            return
        
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
        if self.plotter.selected_node and hasattr(self.plotter.selected_node.value, 'int_to_board'):
            board = self.plotter.selected_node.value.int_to_board()
            self.draw_board(board)

        color_mapping = {
            'Terminal - Winner 1': (0, 0, 255),
            'Terminal - Winner 2': (255, 0, 0),
            'Terminal - Draw': (255, 0, 255),
            'Simulation': (128, 128, 128),
            'Has Path': (144, 238, 144),
        }
        self.draw_legend(color_mapping)                   
        pygame.display.update()


    def node_selected(self, node): 
        
        if node.data:
            # Update the list box with new items.
            self.list_box.set_item_list([str(item) for item in node.data])
            
            # Attach the node object as 'data' to each item.
            for i, item in enumerate(self.list_box.item_list):
                item['data'] = node.data[i]

        # Draw the board if the node has the 'int_to_board' method
        if hasattr(node.value, 'int_to_board'):
           board = node.value.int_to_board()
           self.draw_board(board)

    testing = False
    if testing:
        def custom_label(self, node):
            return f"{node.value}"

        def custom_color(self, node):
            return 'white'
    else:
        def custom_label(self, node):
            return f"c{node.value.last_move} W:{node.value.win_count[1]},{node.value.win_count[2]} t:{node.value.win_count[2]-node.value.win_count[1]} \nQ: {int(node.value.Q[1])},{int(node.value.Q[2])} N: {node.value.N[1]},{node.value.N[2]} U:{node.value.uct_value[1]:.1f},{node.value.uct_value[2]:.1f} \nD: {node.value.depth} P: {node.value.player}\nR: {node.value.reward[1]:.1f}, {node.value.reward[2]:.1f} RT: {node.value.total_reward[1]:.1f}, {node.value.total_reward[2]:.1f}"

        def custom_color(self, node):
            
            if node.value._is_terminal:
                if node.value.winner == 1:
                    return (0, 0, 255)  # Blue
                elif node.value.winner == 2:
                    return (255, 0, 0)  # Red
                else:
                    return (255, 0, 255)  # Magenta
            elif not node.value.visited:
                return (128, 128, 128)  # Gray
            elif node.data:
                return (144, 238, 144)  # Light green, equivalent to '#90EE90'
            else:
                return (255, 255, 255)  # White

    def draw_board(self, board):
            # rows, cols = 6, 7
            # board = np.zeros((rows, cols), dtype=np.int8)            
            # board[0, 0] = 1
            rows, cols = board.shape
            cell_size = 20  # Size for each cell in the board
            board_x = self.WIDTH - self.PANEL_WIDTH + 20  # Starting x-coordinate to draw the board
            board_y = 300  # Starting y-coordinate to draw the board

            for row in range(rows):
                for col in range(cols):
                    rect_x = board_x + col * cell_size
                    rect_y = board_y + row * cell_size
                    pygame.draw.rect(self.screen, (100,100,100), (rect_x, rect_y, cell_size, cell_size), 1)  # Draw cell border
                    
                    if board[row, col] == 1:
                        pygame.draw.circle(self.screen, (0, 0, 255), (rect_x + cell_size // 2, rect_y + cell_size // 2), cell_size // 3)  # Draw blue circle for player 1
                    elif board[row, col] == 2:
                        pygame.draw.circle(self.screen, (255, 0, 0), (rect_x + cell_size // 2, rect_y + cell_size // 2), cell_size // 3)  # Draw red circle for player 2

    def draw_legend(self, color_mapping):
        x, y = 20, self.HEIGHT - 20  # Start drawing the legend 20 pixels above the bottom left corner.
        font = pygame.font.SysFont('Arial', 14)
        offset = 0

        for color_name, color_value in reversed(color_mapping.items()):
            pygame.draw.rect(self.screen, color_value, (x, y - offset, 15, 15))
            label_surface = font.render(color_name, True, (0,0,0))
            self.screen.blit(label_surface, (x + 20, y - offset))
            offset += 25  # Move 25 pixels up for the next entry


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
    """
    Recursively generate a test tree up to a given depth.
    
    Arguments:
      - max_depth: Maximum depth of the tree
      - num_children: Number of children each node should have
    
    Returns the root node of the generated tree.
    
    """
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
    """
    Initialize a sample MCTS tree for testing.
    """
    root_node = generate_tree(8, 2)
    return root_node
    
# Usage
# root_node = init_tree()
# mcts_tree = MCTSTree(root_node)
# mcts_tree.start()
