import tkinter as tk


class CameraRectangle:
    def __init__(self, canvas, x, y, width, height, color="red"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.line_ids = [None, None, None, None]  # left, top, right, bottom
        self.update(self.x, self.y)

    def id_exists(self, id):
        return len(self.canvas.find_withtag(id)) > 0

    def get_corners(self):
        #self.update(self.x, self.y)
        line1_coords = self.canvas.coords(self.line_ids[0])
        line3_coords = self.canvas.coords(self.line_ids[2])
        
        # Upper-left corner
        upper_left_x = line1_coords[0]
        upper_left_y = line1_coords[1]
        
        # Lower-right corner
        lower_right_x = line3_coords[2]
        lower_right_y = line3_coords[3]
        
        return (upper_left_x, upper_left_y), (lower_right_x, lower_right_y)


    def update(self, x, y):
        self.x = x
        self.y = y
        x1, y1, x2, y2 = self.x + 50, self.y + 50, self.x + self.width - 50, self.y + self.height -50
        # Coordinates for the four lines
        lines = [
            (x1, y1, x1, y2),  # Left
            (x1, y1, x2, y1),  # Top
            (x2, y1, x2, y2),  # Right
            (x1, y2, x2, y2)   # Bottom
        ]

        for i in range(4):
            if self.line_ids[i] is None or not self.id_exists(self.line_ids[i]):
                self.line_ids[i] = self.canvas.create_line(*lines[i], fill=self.color, tags=("CameraRectangle","move"))
            else:
                self.canvas.coords(self.line_ids[i], *lines[i])

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

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
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_offset = {'x': 0, 'y': 0}
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
        self.node_height = 100
        self.vertical_spacing = 50
        self.horizontal_spacing = 20
        self.label_func = label_func if label_func is not None else (lambda node: str(node.value))

        self.selected_node = None
        self.tk_root = tk_root if tk_root is not None else tk.Tk()
        self.canvas = tk.Canvas(self.tk_root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.scale("move",0,0, 0.0001,0.0001)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Double-Button-1>", self.node_double_click)
        self.canvas.bind("<Button-1>", self.node_click)
        self.canvas.bind("<Button-2>", self.start_pan)
        self.canvas.bind("<ButtonPress-2>", self.start_pan) # Changed from ButtonPress-1
        self.canvas.bind("<B2-Motion>", self.pan) # Changed from B1-Motion

        self.camera_rect = CameraRectangle(self.canvas, color="red", x = -self.canvas_width / 2, y = -self.canvas_width /2, width=self.canvas_width, height=self.canvas_height)

        self.mouse_position_label = tk.Label(self.tk_root, anchor='e', relief='solid', borderwidth=1, padx=5)
        self.mouse_position_label.pack(side='bottom', fill='x', anchor='e', padx=5, pady=5)
        self.canvas.bind('<Motion>', self.update_info_bar)
        self.show_visible_var = tk.BooleanVar(value=False)

        self.show_visible_check = tk.Checkbutton(
        self.tk_root, text="Show Visible Nodes", variable=self.show_visible_var, command=self.toggle_visible_nodes)
        self.show_visible_check.pack(side='bottom', padx=5, pady=5)
        self.center_view(-self.canvas_width // 2, -self.canvas_height // 2)
    
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
        self.canvas.delete("delete")
        self.clear_canvas()
        self.draw_tree(self.root, 0, 0)    

        # Refresh the visuals
        self.set_font_size()            
        root_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(root_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        self.canvas.move("move", dx, dy)


    def refresh_tree(self, event=None):
        try:
            item_id = self.find_canvas_id(self.root)
            old_position = self.canvas.coords(item_id)         
        except:
            return

        self.canvas.delete("delete")
        self.clear_canvas()

        self.draw_tree(self.root, 0, 0)

        self.set_font_size()  

        item_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(item_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        delta = Vector2(dx, dy)

        dx = delta.x
        dy = delta.y
        # self.camera_rect.update(0,0)
        self.canvas.move("move", dx + self.pan_offset["x"], dy + self.pan_offset["y"])

        self.pan_offset['x'] -= dx
        self.pan_offset['y'] -= dy
        self.update_info_bar(event)
        # self.canvas.move("move", dx, dy)

    def recursive_toggle_visibility(self, node):
        if not node.initial_visibility:  # Only change nodes that were initially not visible
            node.visible = self.show_visible_var.get()
               
        for child in node.children:
            self.recursive_toggle_visibility(child)

    def clear_canvas(self):
        self.canvas.delete("delete")

        items_to_delete = []
        for item_id, node in self.canvas_nodes.items():
            tags = self.canvas.gettags(item_id)
            if "delete" in tags:
                self.canvas.delete(item_id)
                items_to_delete.append(item_id)

        for item_id in items_to_delete:
            del self.canvas_nodes[item_id]




    def toggle_visible_nodes(self):
        item_id = self.find_canvas_id(self.root)
        old_position = self.canvas.coords(item_id) 
    
        self.recursive_toggle_visibility(self.root)
        self.canvas.delete("delete")
        self.clear_canvas()
        self.draw_tree(self.root, 0, 0)

        self.set_font_size()            
        item_id = self.find_canvas_id(self.root)
        new_position = self.canvas.coords(item_id) 
        dx = old_position[0] - new_position[0]
        dy = old_position[1] - new_position[1]
        self.canvas.move("move", dx, dy)

    
    def screen_to_world(self, screen_x, screen_y):
        # Reverse the pan offset
        world_x = screen_x + self.pan_offset['x'] / self.zoom_level
        world_y = screen_y + self.pan_offset['y'] / self.zoom_level
        return world_x, world_y

    def world_to_screen(self, world_x, world_y):
        screen_x = world_x * self.zoom_level - self.pan_offset['x']
        screen_y = world_y * self.zoom_level - self.pan_offset['y']
        return screen_x, screen_y

    def update_info_bar(self, event):
        if not event:
            return
        world_x, world_y = self.screen_to_world(event.x, event.y)
        cam_world_x, cam_world_y = self.screen_to_world(self.canvas_width/2, self.canvas_height/2)
        cam_world_x2, cam_world_y2 = self.screen_to_world(self.canvas_width/2 + self.canvas_width, self.canvas_height/2 + self.canvas_height)
        root_id = self.find_canvas_id(self.root)
        old_position = self.canvas.coords(root_id)         
        # self.camera_rect.update(0, 0)
        (camera_x, camera_y), (camera_width, camera_height) = self.camera_rect.get_corners()        
        self.mouse_position_label.config(text=f"X: {int(event.x)}, Y: {int(event.x)}\nWORLD X: {int(world_x)}, WORLD Y: {int(world_y)}\nCAMERA X: {int(camera_x)}, CAMERA Y: {int(camera_y)}\nCAMERA WIDTH: {int(camera_width)}, CAMERA HEIGHT: {int(camera_height)}\n CAM WORLD X: {int(cam_world_x)}, CAM WORLD Y: {int(cam_world_y)}\n CAM WORLD X2: {int(cam_world_x2)}, CAM WORLD Y2: {int(cam_world_y2)}")


    def find_closest(self, x, y):
        closest_item_id = None
        canvas_x = self.canvas.canvasx(x)
        canvas_y = self.canvas.canvasy(y)

        for item_id in self.canvas_nodes.keys():
            bbox = self.canvas.bbox(item_id)
            if bbox is None or len(bbox) < 4:
                continue
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
                self.expand_all_children(clicked_node, not clicked_node.expanded)
                self.canvas.delete("delete")
                self.clear_canvas()
                self.draw_tree(self.root, 0, 0)
            else:
                self.toggle_expand(clicked_node)
            
            self.set_font_size()            
            # Find the new position of the clicked node
            for new_item_id, node in self.canvas_nodes.items():
                if node == clicked_node:
                    new_position = self.canvas.coords(new_item_id)
                    break
            if(new_position):
                dx = old_position[0] - new_position[0]
                dy = old_position[1] - new_position[1]
                self.canvas.move("move", dx, dy)
            
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


    def draw_node(self, node, x, y):
        # self.camera_rect.update(0, 0)  
        (camera_x, camera_y), (camera_x2, camera_y2) = self.camera_rect.get_corners()
        camera_x, camera_y = self.screen_to_world(camera_x, camera_y)
        camera_x2, camera_y2 = self.screen_to_world(camera_x2, camera_y2)

        no_render = False

        if (
            (x + self.node_width < camera_x or
            x - self.node_width > camera_x2 or
            y + self.node_height < camera_y or
            y - self.node_height > camera_y2) and
            not node == self.root
        ):
            no_render = False

        
        label = self.label_func(node)
        color = self.color_func(node)
        
        # Adjusting the starting and ending points to center the rectangle on (x, y)
        start_x = x - self.node_width // 2
        start_y = y - self.node_height // 2
        end_x = x + self.node_width // 2
        end_y = y + self.node_height // 2

        outline_width = 3 if node.selected else 1
        if not no_render:
            tag = ("move") if node == self.root else ("move","delete")
                
            rect = self.canvas.create_rectangle(start_x, start_y, end_x, end_y, fill=color, width=outline_width, tags=(tag,))
            text_id = self.canvas.create_text(x, y, text=label, tags=(tag,))  # Using the center x and y directly
        
            # Draw the up/down arrow for nodes with children
            if node.children:
                arrow_size = 20  # Adjust as needed
                if not node.expanded:
                    # Draw the up arrow
                    self.canvas.create_polygon(x, end_y - arrow_size,
                                            x - arrow_size / 2, end_y,
                                            x + arrow_size / 2, end_y,
                                            fill='black', tags=(tag,))
                else:
                    # Draw the down arrow
                    self.canvas.create_polygon(x, end_y,
                                            x - arrow_size / 2, end_y - arrow_size,
                                            x + arrow_size / 2, end_y - arrow_size,
                                            fill='black', tags=(tag,))

            self.canvas_nodes[rect] = node
            self.canvas_nodes[text_id] = node
        return x, y


    def toggle_expand(self, node):       
        # Toggle the node's visibility and redraw the tree
        node.expanded = not node.expanded
        self.refresh_tree()
    
        
    def get_children_width(self, node):
        total_width = 0
        
        # Check if the node has children
        if not node.children:
            return self.node_width  # Return the width of a single node if it has no children

        # Loop through all children to calculate their widths
        for child in node.children:
            if child.visible:  # Only count visible nodes
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
        visible_children_count = sum(1 for child in node.children if child.visible)
        total_width += self.horizontal_spacing * (max(visible_children_count - 1, 0))

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
                self.draw_line_culled(parent_center[0], parent_center[1] + self.node_height // 2,
                                        child_center[0], child_center[1] - self.node_height // 2)

        return parent_center

    def draw_line_culled(self, x1, y1, x2, y2):
        (camera_x, camera_y), (camera_x2, camera_y2) = self.camera_rect.get_corners()
        x_view_start, y_view_start = self.world_to_screen(camera_x, camera_y)
        x_view_end, y_view_end = self.world_to_screen(camera_x2, camera_y2)

        #if self.line_intersects_rect(Vector2(x1, y1), Vector2(x2, y2), Vector2(x_view_start, y_view_start), Vector2(x_view_end, y_view_end)):
        self.canvas.create_line(x1, y1, x2, y2, tags=("move",))



    def center_view(self, x, y):
        """Center the canvas view around the given canvas coordinates."""
        half_width = self.canvas.winfo_width() // 2
        half_height = self.canvas.winfo_height() // 2
        dx = half_width - x
        dy = half_height - y
        self.canvas.move("move", dx, dy)
        
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
        self.canvas.scale("move", mouseX, mouseY, zoom_factor, zoom_factor)
        self.canvas.scale("CameraRectangle", mouseX, mouseY, 1/zoom_factor, 1/zoom_factor)
        # Update the running font scale
        self.font_scale *= zoom_factor
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

    def line_intersects_rect(self, line_start, line_end, rect_top_left, rect_bottom_right):
        # Define the four edges of the rectangle as pairs of points
        top_edge = (rect_top_left, Vector2(rect_bottom_right.x, rect_top_left.y))
        bottom_edge = (Vector2(rect_top_left.x, rect_bottom_right.y), rect_bottom_right)
        left_edge = (rect_top_left, Vector2(rect_top_left.x, rect_bottom_right.y))
        right_edge = (Vector2(rect_bottom_right.x, rect_top_left.y), rect_bottom_right)

        rect_edges = [top_edge, bottom_edge, left_edge, right_edge]

        if rect_top_left.x <= line_start.x <= rect_bottom_right.x and \
        rect_top_left.y <= line_start.y <= rect_bottom_right.y and \
        rect_top_left.x <= line_end.x <= rect_bottom_right.x and \
        rect_top_left.y <= line_end.y <= rect_bottom_right.y:
            return True

        for edge_start, edge_end in rect_edges:
            # Calculate vectors
            A = line_end - line_start
            B = edge_end - edge_start
            C = edge_start - line_start

            # Calculate the determinant
            det = A.x * B.y - A.y * B.x
            if det == 0:
                continue  # Lines are parallel, no intersection

            # Calculate the lambda and gamma parameters for the intersection point
            lam = (B.y * C.x - B.x * C.y) / det
            gamma = (A.y * C.x - A.x * C.y) / det

            # Check if the intersection point is within both the line segment and the edge of the rectangle
            if 0 <= lam <= 1 and 0 <= gamma <= 1:
                return True

        return False


    def start_pan(self, event):
        self.last_x, self.last_y = event.x, event.y
    

    def pan(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.canvas.move("move", dx, dy)
        self.pan_offset['x'] += dx
        self.pan_offset['y'] += dy
        self.canvas.move("CameraRectangle", -dx, -dy)
        
        self.last_x, self.last_y = event.x, event.y

    def start(self):
        self.draw_tree(self.root, 0, 0)
        self.canvas.update()
        self.set_font_size()
        #self.center_view(0, 0)
        # self.canvas.move("move", 100, 100)
        self.tk_root.mainloop()




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

root_node = generate_tree(8,2)
mcts_tree = TreePlotter(root_node, canvas_width=1000, canvas_height=1000)
mcts_tree.start()