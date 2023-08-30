import panda3d.core as p3d

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

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    

class TreePlotter:
    def __init__(self, root, label_func = None, color_func = None, zoom_level = 1):
        self.zoom_level = zoom_level
        self.initial_font_size = 10
        self.font_scale = zoom_level
        self.last_click_time = 0
        self.double_click_flag = False
        self.color_func = color_func if color_func is not None else (lambda node: 'white')
        self.canvas_nodes = {}
        self.root = root
        self.node_width = 100
        self.node_height = 70
        self.vertical_spacing = 50
        self.horizontal_spacing = 20
        self.label_func = label_func if label_func is not None else (lambda node: str(node.value))
        self.pan_offset = {'x': 0, 'y': 0}
        self.selected_node = None

    def draw_node(self, node, x, y):

        label = self.label_func(node)
        color = self.color_func(node)
        
        # Create a TextNode for the label
        text = p3d.TextNode(label)
        text.setAlign(p3d.TextNode.ACenter) 
        textnp = self.render.attachNewNode(text)
        textnp.setPos(x, 0, y)
        
        # Create a rectangle for the node
        outline_width = 3 if node.selected else 1
        hw = self.node_width / 2.0
        hh = self.node_height / 2.0
        rectangle = p3d.CardMaker("node")
        rectangle.setFrame(x-hw, y-hh, x+hw, y+hh)
        nodepath = self.render.attachNewNode(rectangle.generate())
        nodepath.setColor(color)
        nodepath.setTransparency(p3d.TransparencyAttrib.MAlpha)
        nodepath.setBin("fixed", 0)
        
        # Store nodepath and textnp with the node
        self.panda_nodes[node] = nodepath
        self.panda_texts[node] = textnp
        
        # Draw arrows if needed
        if node.children:
            arrow_size = 20 
            if not node.expanded:
                arrow = self.drawArrow(x, y-hh-arrow_size, arrow_size)
            else:
                arrow = self.drawArrow(x, y-arrow_size, arrow_size)
            arrow.reparentTo(nodepath)
            
        return x, y

    def drawArrow(self, x, y, size):
        vertexes = [(x, y), 
                    (x-size/2, y-size),
                    (x+size/2, y-size)]
        arrow = p3d.GeomVertexData('arrow', p3d.GeomVertexFormat.getV3(), p3d.Geom.UHStatic) 
        arrow_vertices = arrow.modifyArray(0)
        for vert in vertexes:
            arrow_vertices.addData3f(vert[0], 0, vert[1])
        arrow_triangles = p3d.GeomTristrips(p3d.Geom.UHStatic)
        arrow_triangles.addNextVertices(0, 1, 2)
        arrow_triangles.closePrimitive()
        arrow_geom = p3d.Geom(arrow)
        arrow_geom.addPrimitive(arrow_triangles)
        node = p3d.NodePath(p3d.GeomNode('arrow'))
        node.addGeom(arrow_geom)
        return node

node = TreeNode("Root")
tree = TreePlotter(node)
tree.draw_node(node, 100, 100)