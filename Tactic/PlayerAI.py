from Player import Player
from Helicopter import Helicopter
from Soldier import Soldier
from Tank import Tank
from Boat import Boat
import random

class PlayerAI(Player):
    def __init__(self, number):
        super().__init__(number, False)
        pass

    def place_units(self, grid, team, max_distance=3, screen=None, end_turn_clicked=None):
        first_unit_placed = False

        # self.register_observer(unit)
        # #unit.place_on_tiles(tile)
        # self.players[player].add_unit(unit)

        first_unit_tile = None
        for unit_type in team:
            if not first_unit_tile:
                tile_fount = False
                while not tile_fount:
                    tile = grid.get_random_tile()
                    tiles = grid.tiles_in_range_manhattan(tile.x, tile.y, max_distance)
                    free_tiles_count = 0
                    for t_x, t_y in tiles:
                        if grid.is_tile_free(t_x, t_y):
                            free_tiles_count+=1
                    tile_fount = free_tiles_count >= len(team)
                first_unit_tile = tile
            else:
                # Generate random offsets within the max_distance range
                dx = random.randint(-max_distance, max_distance)
                dy = random.randint(-max_distance, max_distance)
                
                # Calculate new coordinates within the board boundaries
                x = min(max(first_unit_tile.x + dx, 0), len(grid.tiles) - 1)
                y = min(max(first_unit_tile.y + dy, 0), len(grid.tiles[0]) - 1)
                
                tile = grid.tiles[x][y]

            if unit_type == "Soldier":
                unit = Soldier(tile, self.number, grid, screen=screen)
            elif unit_type == "Tank":
                unit = Tank(tile, self.number, grid, screen=screen)
            elif unit_type == "Helicopter":
                unit = Helicopter(tile, self.number, grid, screen=screen)
            elif unit_type == "Boat":
                unit = Boat(tile, self.number, grid, screen=screen)

            self.add_unit(unit)

        end_turn_clicked(None)
        