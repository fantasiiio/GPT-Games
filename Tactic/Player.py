class Player:
    def __init__(self, number, is_human=True):
        self.number = number
        self.is_human = is_human
        self.resources = {
            'gold': 100,
            'wood': 100,
            'stone': 100,
            'food': 100
        }
        self.units = []  # List to store all units owned by the player
        self.structures = []  # List to store all structures owned by the player

    def add_unit(self, unit):
        """Add a unit to the player's list of units."""
        self.units.append(unit)

    def remove_unit(self, unit):
        """Remove a unit from the player's list of units."""
        self.units.remove(unit)

    def add_structure(self, structure):
        """Add a structure to the player's list of structures."""
        self.structures.append(structure)

    def gather_resources(self):
        """Gather resources from all structures owned by the player."""
        for structure in self.structures:
            resource, amount = structure.produce()
            self.resources[resource] += amount

    def can_afford(self, cost):
        """Check if the player can afford a certain cost."""
        for resource, amount in cost.items():
            if self.resources.get(resource, 0) < amount:
                return False
        return True

    def pay(self, cost):
        """Deduct the cost from the player's resources."""
        for resource, amount in cost.items():
            self.resources[resource] -= amount

    def end_turn(self):
        """Handle end of turn for the player."""
        self.gather_resources()
        # Reset action points for all units
        for unit in self.units:
            unit.action_points = unit.max_action_points
