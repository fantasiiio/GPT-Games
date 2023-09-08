import random

class AI:
    def __init__(self, grid):
        self.grid = grid

    def ai_turn(self,ai_player):
        for unit in ai_player.units:
            # Randomly decide to move or attack
            action = random.choice(['move', 'attack'])

            if action == 'move':
                # Randomly choose a direction and move
                direction = random.choice(['up', 'down', 'left', 'right'])
                target_tile = self.grid.get_adjacent_tile(unit, direction)
                unit.move(target_tile)
            elif action == 'attack':
                # Check for adjacent player units and attack
                for direction in ['up', 'down', 'left', 'right']:
                    target_tile = self.grid.get_adjacent_tile(unit, direction)
                    if target_tile.unit and target_tile.unit.player != ai_player:
                        unit.attack(target_tile.unit)
                        break

