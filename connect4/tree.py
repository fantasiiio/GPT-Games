import tkinter as tk

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
    def __init__(self, root, tk_root = None, zoom_level=1.0, canvas_width=600, canvas_height=400, label_func=None, color_func=None, select_node_func=None):
        self.zoom_level = zoom_level
        self.initial_font_size = 10
        self.font_scale = zoom_level
        self.last_click_time = 0
        self.double_click_flag = False
        self.select_node_func = select_node_func
        self.color_func = color_func if color_func is not None else (lambda node: 'white')
        self.canvas_nodes = {}
        self.root = root
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.node_width = 100
        self.node_height = 70
        self.vertical_spacing = 50
        self.horizontal_spacing = 20
        self.label_func = label_func if label_func is not None else (lambda node: str(node.value))
        self.pan_offset = {'x': 0, 'y': 0}
        self.selected_node = None
        self.tk_root = tk_root if tk_root is not None else tk.Tk()
        self.canvas = tk.Canvas(self.tk_root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.scale("all",0,0, 0.0001,0.0001)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Double-Button-1>", self.node_double_click)
        self.canvas.bind("<Button-1>", self.node_click)
        self.canvas.bind("<Button-2>", self.start_pan)
        self.canvas.bind("<ButtonPress-2>", self.start_pan) # Changed from ButtonPress-1
        self.canvas.bind("<B2-Motion>", self.pan) # Changed from B1-Motion

        self.mouse_position_label = tk.Label(self.tk_root, anchor='e', relief='solid', borderwidth=1, padx=5)
        self.mouse_position_label.pack(side='bottom', fill='x', anchor='e', padx=5, pady=5)
        self.canvas.bind('<Motion>', self.update_mouse_position)
        self.show_visible_var = tk.BooleanVar(value=False)

        self.show_visible_check = tk.Checkbutton(
        self.tk_root, text="Show Visible Nodes", variable=self.show_visible_var, command=self.toggle_visible_nodes)
        self.show_visible_check.pack(side='bottom', padx=5, pady=5)
        #self.center_view(-self.canvas_width // 2, -self.canvas_height // 2)
    
    def node_click(self, event):
        current_time = event.time

        # Check if the last click was within 300 milliseconds (can adjust this value)
        if current_time - self.last_click_time < 400:
            self.double_click_flag = True
            return  # Do not process this click since it's part of a double-click

        # Reset the last click time
        self.last_click_time = current_time

        # Delay the processing of the single click to check for a subsequent click
        self.tk_root.after(400, self.process_single_click, event)


    def process_single_click(self, event):
        # If a double-click event has occurred, reset the flag and return
        if self.double_click_flag:
            self.double_click_flag = False
            return
        
        item_id = self.find_closest(event.x, event.y)
        root_id = self.find_canvas_id(self.root)
        old_position = self.canvas.coords(root_id) 
        if item_id is not None:
            clicked_node = self.canvas_nodes[item_id]
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
            

        self.recursive_toggle_visibility(self.root)
        self.canvas.delete("all")
        self.canvas_nodes.clear()
        self.draw_tree(self.root, 0, 0)    

        # Refresh the visuals
        self.restore_view_scale()            
        root_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(root_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        self.canvas.move("all", dx, dy)


    def refresh_tree(self):
        item_id = self.find_canvas_id(self.root)
        old_position = self.canvas.coords(item_id)         
        self.canvas.delete("all")
        self.canvas_nodes.clear()

        self.draw_tree(self.root, 0, 0)

        self.restore_view_scale()  
        item_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(item_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        self.canvas.move("all", dx, dy)

    def recursive_toggle_visibility(self, node):
        if not node.initial_visibility:  # Only change nodes that were initially not visible
            node.visible = self.show_visible_var.get()
               
        for child in node.children:
            self.recursive_toggle_visibility(child)
                
    def get_view_position(self):
        return self.canvas.canvasx(0), self.canvas.canvasy(0)

    def toggle_visible_nodes(self):
        item_id = self.find_canvas_id(self.root)
        old_position = self.canvas.coords(item_id) 
    
        self.recursive_toggle_visibility(self.root)
        self.canvas.delete("all")
        self.canvas_nodes.clear()
        self.draw_tree(self.root, 0, 0)

        self.restore_view_scale()            
        item_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(item_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        self.canvas.move("all", dx, dy)

    def update_mouse_position(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        self.mouse_position_label.config(text=f"X: {canvas_x}, Y: {canvas_y}")


    def find_closest(self, x, y):
        closest_item_id = None
        canvas_x = self.canvas.canvasx(x)
        canvas_y = self.canvas.canvasy(y)

        for item_id in self.canvas_nodes.keys():
            bbox = self.canvas.bbox(item_id)
            if bbox[0] <= canvas_x <= bbox[2] and bbox[1] <= canvas_y <= bbox[3]:
                closest_item_id = item_id
                break

        return closest_item_id

    def node_double_click(self, event):
        self.double_click_flag = True
        item_id = self.find_closest(event.x, event.y)
        if item_id is not None:
            clicked_node = self.canvas_nodes[item_id]
            old_position = self.canvas.coords(item_id)  # Capture the current position
            
            # Check if Shift key was pressed
            if event.state & 0x1: 
                x, y = self.pan_offset['x'], self.pan_offset['y']
                self.expand_all_children(clicked_node, not clicked_node.expanded)
                self.canvas.delete("all")
                self.canvas_nodes.clear()
                self.draw_tree(self.root, 0, 0)
            else:
                self.toggle_expand(clicked_node)
            
            self.restore_view_scale()            
            # Find the new position of the clicked node
            for new_item_id, node in self.canvas_nodes.items():
                if node == clicked_node:
                    new_position = self.canvas.coords(new_item_id)
                    break
            
            dx = old_position[0] - new_position[0]
            dy = old_position[1] - new_position[1]
            self.canvas.move("all", dx, dy)
            
    def find_canvas_id(self, target_node):
        for canvas_id, node in self.canvas_nodes.items():
            if node == target_node:
                return canvas_id
        return None


    def expand_all_children(self, node, expanded):
        if node.visible and node.children:
            node.expanded = expanded
        for child in node.children:
                child.expanded = expanded
                self.expand_all_children(child, expanded)

    def get_view_position(self):
        """Get the current horizontal and vertical scroll position."""
        return self.canvas.xview()[0], self.canvas.yview()[0]

    def set_view_position(self, x, y):
        """Set the horizontal and vertical scroll position."""
        self.canvas.xview_moveto(x)
        self.canvas.yview_moveto(y)


    def set_visibility(self, node, visibility):
        for child in node.children:
            child.expanded = visibility
            self.set_visibility(child, visibility)

    def draw_node(self, node, x, y):
        label = self.label_func(node)
        color = self.color_func(node)
        
        # Adjusting the starting and ending points to center the rectangle on (x, y)
        start_x = x - self.node_width // 2
        start_y = y - self.node_height // 2
        end_x = x + self.node_width // 2
        end_y = y + self.node_height // 2

        outline_width = 3 if node.selected else 1
        rect = self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill=color, width=outline_width)
        text_id = self.canvas.create_text(x, y, text=label)  # Using the center x and y directly
        
        # Draw the up/down arrow for nodes with children
        if node.children:
            arrow_size = 20  # Adjust as needed
            if not node.expanded:
                # Draw the up arrow
                self.canvas.create_polygon(x, end_y - arrow_size,
                                        x - arrow_size / 2, end_y,
                                        x + arrow_size / 2, end_y,
                                        fill='black')
            else:
                # Draw the down arrow
                self.canvas.create_polygon(x, end_y,
                                        x - arrow_size / 2, end_y - arrow_size,
                                        x + arrow_size / 2, end_y - arrow_size,
                                        fill='black')

        self.canvas_nodes[rect] = node
        self.canvas_nodes[text_id] = node
        return x, y



    def restore_view_scale(self):
        self.canvas.scale("all", 0, 0, self.zoom_level, self.zoom_level)
        self.set_font_size()

    def toggle_expand(self, node):       
        # Toggle the node's visibility and redraw the tree
        node.expanded = not node.expanded
        self.canvas.delete("all")
        self.canvas_nodes.clear()
        self.draw_tree(self.root, 0, 0)
    
        
    def get_children_width(self, node, width=0):
        # If the node has no children or if it's not expanded, count it as a leaf
        visible_children_count = sum(1 for child in node.children if child.visible)        
        if not node.expanded or not node.children or not node.visible or visible_children_count == 0:
            node.total_width =  self.node_width
            return self.node_width + self.horizontal_spacing

        total_width = 0
        for child in node.children:
            if child.visible:
                total_width += self.get_children_width(child, total_width) 
                node.total_width = total_width
        
        if total_width > 0 :
            total_width -= self.horizontal_spacing

        return total_width


                    
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




    def center_view(self, x, y):
        """Center the canvas view around the given canvas coordinates."""
        half_width = self.canvas.winfo_width() // 2
        half_height = self.canvas.winfo_height() // 2
        dx = half_width - x
        dy = half_height - y
        self.canvas.move("all", dx, dy)
        
        # Adjust the pan_offset to reflect the new position
        self.pan_offset['x'] -= dx
        self.pan_offset['y'] -= dy





    def zoom(self, event):
        scale_factor = 1.1
        zoom_factor = 1 / scale_factor if -event.delta > 0 else scale_factor
        self.zoom_level *= zoom_factor
        # Get the current canvas coordinates of the mouse pointer
        mouseX = self.canvas.canvasx(event.x)
        mouseY = self.canvas.canvasy(event.y)
        
        # Adjust the coordinates of all items on the canvas
        self.canvas.scale("all", mouseX, mouseY, zoom_factor, zoom_factor)
        
        # Update the running font scale
        self.font_scale *= zoom_factor

        # Adjust font size for all text items
        self.set_font_size()

    def set_font_size(self):
        for item_id, node in self.canvas_nodes.items():
            if self.canvas.type(item_id) == 'text':
                new_font_size = int(self.initial_font_size * self.font_scale)
                if new_font_size < 1:
                    new_font_size = 1
                current_font = self.canvas.itemcget(item_id, "font").split()
                font_name = current_font[0]
                self.canvas.itemconfig(item_id, font=(font_name, new_font_size))



    def start_pan(self, event):
        self.last_x, self.last_y = event.x, event.y
    

    def pan(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.canvas.move("all", dx, dy)
        self.pan_offset['x'] += dx
        self.pan_offset['y'] += dy
        self.last_x, self.last_y = event.x, event.y
  
    def start(self):
        self.draw_tree(self.root, 0, 0)
        self.canvas.update()
        self.restore_view_scale()
        self.center_view(0, 0)
        # self.canvas.move("all", 100, 100)
        self.tk_root.mainloop()

