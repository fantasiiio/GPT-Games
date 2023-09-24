
class Structure:
    def __init__(self, x, y, structure_type='farm'):
        self.screen_x = x
        self.screen_y = y
        self.structure_type = structure_type

    def produce(self):
        """Produce resources or units based on the structure type."""
        if self.structure_type == 'farm':
            return 'food', 10  # Produce 10 food per turn
        elif self.structure_type == 'barracks':
            # Produce a soldier unit (can be added to game logic later)
            return 'soldier', Unit(self.screen_x, self.screen_y)