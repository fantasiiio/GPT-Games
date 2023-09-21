class SpriteLayer():
    def __init__(layer_name, z_order = 0):
        self.name = layer_name
        self.z_order = z_order
        self.animations = []

    def draw():
        for animation in self.animations:
            animation.draw()

class SpriteLayerManager():
    layers = []

    @classmethod    
    def add_layer(layer_name):
        layers.append(SpriteLayer(layer_name))
    
    def add_animation(layer_name, animation):
        for layer in self.layers:
            if layer.name == layer_name:
                layer.animations.append(animation)
                return
        raise ValueError(f"Layer {layer_name} not found.")

    @classmethod
    def draw():
        sorted_layers = sorted(layers, key=lambda x: x.z_order)        
        for layer in self.layers:
            layer.draw()