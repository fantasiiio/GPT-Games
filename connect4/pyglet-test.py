from direct.showbase.ShowBase import ShowBase
from panda3d.core import CardMaker, TextNode, TransparencyAttrib

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a rectangle using the CardMaker
        card_maker = CardMaker("rectangle")
        card_maker.setFrame(-0.5, 0.5, -0.25, 0.25) # left, right, bottom, top
        rectangle = self.render2d.attachNewNode(card_maker.generate())
        rectangle.setColor(0.5, 0.2, 0.8, 1) # Set the color (R, G, B, A)

        # Make sure the rectangle is rendered properly
        rectangle.setTransparency(TransparencyAttrib.MAlpha)

        # Create a text node to hold the text
        text_node = TextNode('text_node')
        text_node.setText("Hello, Panda3D!")
        text_node.setTextColor(1, 1, 1, 1) # Set the text color (R, G, B, A)

        # Attach the text node to a NodePath to display it
        text_node_path = self.aspect2d.attachNewNode(text_node)
        text_node_path.setScale(0.07) # Set the scale to make the text visible
        text_node_path.setPos(-0.3, 0, -0.1) # Set the position

app = MyApp()
app.run()
