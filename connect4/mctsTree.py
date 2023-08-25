import tkinter as tk
from tree import TreeNode, TreePlotter

class MCTSTree:
    def __init__(self, root_node=None):
        self.tk_root = tk.Tk()
        self.tk_root.panel_frame = tk.Frame(self.tk_root, bd=2, relief='ridge')
        self.tk_root.panel_frame.pack(side=tk.RIGHT, padx=10, pady=10, expand=False)
        self.listbox = tk.Listbox(self.tk_root.panel_frame, selectmode=tk.SINGLE, width=50)
        self.listbox.pack(fill=tk.BOTH, expand=False)    
        # self.listbox.config(height=10)
        #self.listbox.place(relx=0, rely=0, relwidth=1, height=200)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_list_item)

        self.root_node = root_node
        self.plotter = TreePlotter(self.root_node, self.tk_root, 0.5, canvas_width=1000, canvas_height=1000, 
                                   label_func=self.custom_label, color_func=self.custom_color, select_node_func=self.node_selected)

    # def custom_label(self, node):
    #     return f"{node.value}"

    # def custom_color(self, node):
    #     return 'white'

    def custom_label(self, node):
        return f"c{node.value.last_move} 1:{node.value.win_count[1]} 2:{node.value.win_count[2]} t:{node.value.win_count[2]-node.value.win_count[1]} \nQ: {node.value.Q:.2f} N: {node.value.N}\nD: {node.value.depth} P: {node.value.player}"


    def custom_color(self, node):
        
        if node.value._is_terminal:
            if node.value.winner == 1:
                return 'blue'
            elif node.value.winner == 2:
                return 'red'            
        elif not node.value.visited:
            return 'gray' 
        elif node.data:
            return '#90EE90' 
        else:            
            return 'white'  

    def select_path(self, node, path):
        node.selected = True
        node.expanded = True

        # Find the child node with the matching last_move
        if len(path) <= 1:
            return
        move_to_match = path[1]
        matching_child = next((child for child in node.children if child.value.last_move == move_to_match), None)
        
        if matching_child:
            self.select_path(matching_child, path[1:])

    def deselect_all(self, node=None):
        if node is None:
            node = self.root_node
        node.selected = False
        for child in node.children:
            self.deselect_all(child)

    def on_select_list_item(self, event):
        self.listbox = event.widget
        selected_item_key = self.listbox.get(self.listbox.curselection())
        selected_value = self.plotter.selected_node.data[selected_item_key]
        self.deselect_all()
        self.select_path(self.plotter.selected_node, selected_value)
        self.plotter.refresh_tree()

    def node_selected(self, node): 
        if not node.data:
            return
        self.listbox.delete(0, tk.END)

        for item_key in node.data.keys():
            self.listbox.insert(tk.END, item_key)



    def start(self):
        self.plotter.start()

# def init_tree():
#     root_node = TreeNode(1)
#     root_node.data = {
#         'Item 1': [1,2],
#         'Item 2': [1,3,3],
#         'Item 3': [0,0,0,0],
#         'Item 4': [1,2,1,1,1]
#     }
#     child1 = TreeNode(2)
#     child1.data = {
#         'Item 1': [1],
#         'Item 2': [0,0],
#     }
#     child2 = TreeNode(3)
#     child3 = TreeNode(4)
#     child4 = TreeNode(5)
#     for i in range(10, 20):
#         tree_node = TreeNode(i)
#         tree_node.set_visible(False)
#         child1.add_child(tree_node) 
#     for i in range(20, 30):
#         tree_node = TreeNode(i)
#         tree_node.set_visible(True)
#         child2.add_child(tree_node) 
#     for i in range(30, 40):
#         child3.add_child(TreeNode(i))
#     for i in range(40, 50):
#         tree_node = TreeNode(i)
#         if i == 40:
#             tree_node.set_visible(True)
#         else:
#             tree_node.set_visible(False)
#         child1.children[0].add_child(tree_node)    

#     root_node.add_child(child1)
#     root_node.add_child(child2)
#     root_node.add_child(child3)
#     root_node.add_child(child4)
#     return root_node
    
# # Usage
# root_node = init_tree()
# mcts_tree = MCTSTree(root_node)
# mcts_tree.start()
