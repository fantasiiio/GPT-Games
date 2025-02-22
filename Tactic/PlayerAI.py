from Player import Player
from Helicopter import Helicopter
from Soldier import Soldier
from Tank import Tank
from Boat import Boat
from config import *
import random

class PlayerAI(Player):
    def __init__(self, number, grid, end_turn_clicked, selected_team=None, screen=None):
        super().__init__(number, False)
        self.end_turn_clicked = end_turn_clicked
        self.grid = grid
        self.players = {1: Player(1, False), 2: Player(2, False)}
        self.selected_team = selected_team  # Fill this with your teams
        self.screen = screen  # Your screen object
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
        elif self.game_state == GameState.EXECUTION:
            self.ready = True
            self.end_turn_clicked(None)

    def build_team_with_support(budget=2000, buy_unit_func=None):
        team = []
        remaining_budget = budget
        
        # List of unit types for easier random selection
        unit_types = list(unitSettings.keys())
        id = 0
        # Initially add a couple of medics and mechanics if possible
        for support_type in ["Soldier-Medic", "Soldier-Mecano"]:
            unit_id = f"{support_type}-{id}"
            new_unit = {unit_id: unit_id}
            setting = unitSettings[support_type]
            cost = setting["Purchase Cost"]            
            if cost * 2 <= remaining_budget:  # Checking if we can add two of them
                support_unit = buy_unit_func(new_unit)
                team.add_unit(support_unit)
                team.add_unit(support_unit)
                remaining_budget -= 2 * cost
            id += 1
        
        while remaining_budget > 0:
            affordable_units = [ut for ut in unit_types if unitSettings[ut]['Purchase Cost'] <= remaining_budget]
            
            # Exit loop if no more affordable units
            if not affordable_units:
                break
            
            # Randomly select an affordable unit type
            selected_unit_type = choice(affordable_units)
            
            # Create the unit
            new_unit = create_unit(selected_unit_type, unit_data_json)
            
            # Add the unit to the team
            team.add_unit(new_unit)
            
            # Update the remaining budget
            remaining_budget -= new_unit.purchase_cost
            
            # If the new unit is a vehicle, make sure there are at least 2 soldiers in the team for it to operate
            if isinstance(new_unit, Vehicle) and not any(isinstance(unit, Soldier) for unit in team.units):
                # Add two random soldier types to the team to accompany the vehicle
                for _ in range(2):
                    soldier_type = choice([u for u in unit_types if u.startswith("Soldier")])
                    soldier_unit = create_unit(soldier_type, unit_data_json)
                    
                    # Make sure adding the soldier doesn't exceed the budget
                    if soldier_unit.purchase_cost <= remaining_budget:
                        team.add_unit(soldier_unit)
                        remaining_budget -= soldier_unit.purchase_cost
                    else:
                        print(f"Could not add {soldier_type} due to budget constraints.")
                            
        return team

    def play_AI_TeamBuilder(self, game_state):
        self.game_state = game_state
        if not self.ready:
            self.ready = True
            self.place_units(self.selected_team, 6, self.screen)            
            self.end_turn_clicked(None)


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
                    first_unit_tile = self.grid.get_random_tile()
                    tiles = self.grid.tiles_in_range_manhattan(first_unit_tile.x, first_unit_tile.y, max_distance)
                    free_tiles_count = 0
                    for t_x, t_y in tiles:
                        tile = self.grid.tiles[t_x][t_y]
                        if self.grid.can_place_unit(unit_type, tile, 2):
                            free_tiles_count+=1
                    tile_fount = free_tiles_count >= len(team)
                tile = first_unit_tile
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

            unit.current_player = self.number
            self.add_unit(unit)

        self.end_turn_clicked(None)
        