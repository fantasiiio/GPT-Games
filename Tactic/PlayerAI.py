from Player import Player
from Helicopter import Helicopter
from Soldier import Soldier
from Tank import Tank
from Boat import Boat
from config import GameState
import random

class PlayerAI(Player):
    def __init__(self, number, grid, end_turn_clicked):
        super().__init__(number, False)
        self.end_turn_clicked = end_turn_clicked
        self.grid = grid
        self.players = {1: Player(1, False), 2: Player(2, False)}
        self.selected_team = {}  # Fill this with your teams
        self.screen = None  # Your screen object
        self.game_state = None  # Current game state

    def find_closest_enemy(self, ai_unit, enemy_units):
        ai_unit_position = (ai_unit.tile.x, ai_unit.tile.y)
        return min(enemy_units, key=lambda unit: self.grid.get_manathan_range(*ai_unit_position, unit.world_pos_x, unit.world_pos_y))

    def plan_movement(self, ai_unit, closest_enemy):
        ai_unit_position = (ai_unit.tile.x, ai_unit.tile.y)
        closest_enemy_position = (closest_enemy.tile.x, closest_enemy.tile.y)
        path = self.grid.find_path(ai_unit_position, closest_enemy_position)
        next_point_within_range = self.grid.get_farthest_walkable_point(path, ai_unit.max_move)

        if self.grid.get_manathan_range(*ai_unit_position, *next_point_within_range) <= ai_unit.fire_range:
            path = path[:path.index(next_point_within_range)]
        
        steps_to_take = min(len(path) - 1, ai_unit.max_move)
        return path[steps_to_take]

    def plan_attack_or_move(self, ai_unit, closest_enemy, next_position):
        enemy_range = self.grid.get_manathan_range(*next_position, closest_enemy.tile.x, closest_enemy.tile.y)
        if enemy_range <= ai_unit.fire_range:
            ai_unit.planned_actions.append(("Attack", self.grid.tiles[closest_enemy.tile.x][closest_enemy.tile.y]))
        else:
            ai_unit.planned_actions.append(("Move", self.grid.tiles[next_position[0]][next_position[1]]))

    def AI_planning(self):
        if self.ready:
            return
        enemy_units = self.enemy.units

        for ai_unit in self.get_units_can_do_action():
            closest_enemy = self.find_closest_enemy(ai_unit, enemy_units)
            next_position = self.plan_movement(ai_unit, closest_enemy)
            self.plan_attack_or_move(ai_unit, closest_enemy, next_position)
        
        self.end_turn_clicked(None)

    def play_AI(self, game_state):
        self.game_state = game_state
        if self.game_state == GameState.UNIT_PLACEMENT and not self.ready:
            self.ready = True
            self.place_units(self.selected_team.get(2, []), 6, self.screen)            
            self.end_turn_clicked(None)
        elif self.game_state == GameState.RANDOM_EVENT and not self.ready:
            self.ready = True
            self.end_turn_clicked(None)
        elif self.game_state == GameState.PLANNING:
            self.AI_planning()

    def place_units(self, team, max_distance=3, screen=None, end_turn_clicked=None):
        first_unit_placed = False

        # self.register_observer(unit)
        # #unit.place_on_tiles(tile)
        # self.players[player].add_unit(unit)

        first_unit_tile = None
        for unit_type in team:
            if not first_unit_tile:
                tile_fount = False
                while not tile_fount:
                    tile = self.grid.get_random_tile()
                    tiles = self.grid.tiles_in_range_manhattan(tile.x, tile.y, max_distance)
                    free_tiles_count = 0
                    for t_x, t_y in tiles:
                        tile = self.grid.tiles[t_x][t_y]
                        if self.grid.self.grid.can_place_unit(unit_type, tile, 2):
                            free_tiles_count+=1
                    tile_fount = free_tiles_count >= len(team)
                first_unit_tile = tile
            else:
                tile_fount = False                
                while not tile_fount:
                    dx = random.randint(-max_distance, max_distance)
                    dy = random.randint(-max_distance, max_distance)
                    # Calculate new coordinates within the board boundaries
                    x = min(max(first_unit_tile.x + dx, 0), len(self.grid.tiles) - 1)
                    y = min(max(first_unit_tile.y + dy, 0), len(self.grid.tiles[0]) - 1)

                    tile = self.grid.tiles[x][y]
                    if self.grid.can_place_unit(unit_type, tile, 2):
                            tile_fount = True
                # Generate random offsets within the max_distance range                
                
                tile = self.grid.tiles[x][y]

            if unit_type == "Soldier":
                unit = Soldier(tile, self.number, self.grid, screen=screen)
            elif unit_type == "Tank":
                unit = Tank(tile, self.number, self.grid, screen=screen)
            elif unit_type == "Helicopter":
                unit = Helicopter(tile, self.number, self.grid, screen=screen)
            elif unit_type == "Boat":
                unit = Boat(tile, self.number, self.grid, screen=screen)

            self.add_unit(unit)

        self.end_turn_clicked(None)
        