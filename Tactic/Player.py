class Player:
    def __init__(self, number, is_human=True):
        self.number = number
        self.is_human = is_human
        self.units = []  # List to store all units owned by the player
        self.enemy = None  # Reference to the enemy player#
        self.name = f"Player {number}"

    def add_unit(self, unit):
        """Add a unit to the player's list of units."""
        self.units.append(unit)

    def remove_unit(self, unit):
        """Remove a unit from the player's list of units."""
        self.units.remove(unit)


    def end_turn(self):
        """Handle end of turn for the player."""
        self.gather_resources()
        # Reset action points for all units
        for unit in self.units:
            unit.action_points = unit.max_action_points


    def apply_event(self, event_func, restore_func):
        if self.current_event:
            return False 

        event_func(self.units, self.enemy.units)  # Apply the event
        self.current_event = {
            'event': event_func,
            'restore': restore_func
        }
        return True

    def restore_event(self):
        if not self.current_event:
            return False  # or handle it some other way

        self.current_event['restore'](self.units, self.enemy.units)  # Restore the unit's state
        self.current_event = None  # Clear the current event
        return True