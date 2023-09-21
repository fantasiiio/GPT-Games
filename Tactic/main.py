#from SpriteLayer import SpriteLayers
from Helicopter import Helicopter
import random
import pygame
import pygame_gui
import sys
from grid import Grid 
from Player import Player 
from Soldier import Soldier
from Tank import Tank
import pygame.mixer
from config import screen, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY
from Inputs import Inputs
from MusicPlayer import MusicPlayer
from Boat import Boat
pygame.mixer.init()



# Initialize pygame
pygame.init()
# Set up the display
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption('Strategy Game')
manager = pygame_gui.UIManager((GRID_WIDTH, GRID_HEIGHT))

grid = Grid(pygame, screen, "assets\\maps\\terrain1.tmx")
players = {1: Player(1, True), 2: Player(2, False)}

music_folder = 'assets\\music'
music_player = MusicPlayer(music_folder)

def handle_mouse_click(pos):
    pass
            


def check_game_end():
    # Check if either player has no units left
    if not players[1].units:
        return "AI Wins!"
    elif not players[2].units:
        return "Human Wins!"
    return None

#SpriteLayers.add_layer("top")

def get_unit_index(unit):
    for i, u in enumerate(players[unit.player].units):
        if u == unit:
            return i
    return -1

def choosing_action_finished(unit):
    index = get_unit_index(unit)
    if index >= 0 and index < len(players[unit.player].units) - 1:
        players[unit.player].units[index + 1].current_action = "choosing_action"


player_initial_pos = {1: (2, 2), 2: (4, 2)}
players[1].add_unit(Soldier(grid.tiles[5][16], 1, grid, screen=screen, choosing_action_finished=choosing_action_finished))
players[1].add_unit(Soldier(grid.tiles[14][15], 1, grid, screen=screen, choosing_action_finished=choosing_action_finished))
players[1].add_unit(Tank(grid.tiles[6][16], 1, grid, screen=screen, choosing_action_finished=choosing_action_finished))
players[1].add_unit(Helicopter(grid.tiles[17][15], 1, grid, screen=screen, choosing_action_finished=choosing_action_finished))

#players[1].units[0].current_action = "choosing_action"

for i in range(1):
    x = i + 6
    y = 17
    if not grid.tiles[x][y].unit and not grid.tiles[x][y].structure:
        players[2].add_unit(Soldier(grid.tiles[x][y], 2, grid, screen=screen, choosing_action_finished=choosing_action_finished))

#boat_tile = grid.get_tiles_with_property("heli_start","True")
#if boat_tile:
players[2].add_unit(Boat(grid.tiles[8][17], 2, grid, screen=screen, choosing_action_finished=choosing_action_finished))

# players[2].add_unit(Soldier(grid.tiles[4][2], 2, grid, screen=screen))
# players[2].add_unit(Soldier(grid.tiles[5][2], 2, grid, screen=screen))

unit_info_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((10, 10), (200, 40)),
    text=f"Health: 100  Points: 0",
    manager=manager
)

end_turn_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((GRID_WIDTH - 110, 10), (100, 30)),
    text='End Turn',
    manager=manager
)

action_info_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((GRID_WIDTH - 310, 10), (200, 40)),
    text="Actions: Move (1), Attack (2)",
    manager=manager
)


def update_ui():
    """Update the UI elements."""
    if grid.selected_tile and grid.selected_tile.unit:
        unit = grid.selected_tile.unit
        unit_info_label.set_text(f"Health: 100  Points: {unit.action_points}")


inputs = Inputs()
# Main game loop
running = True

def game_loop():
    """Main game loop."""

    # Main game loop
    running = True
    mouse_pos = (0,0)
    while running:
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        inputs.update()

        for event in pygame.event.get():           
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    handle_mouse_click(event.pos)

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == end_turn_button:
                        pass
                        #unit.action_points = 10
                        #update_ui()

            manager.process_events(event)
            # for player in players.values(): 
            #     for unit in player.units:
            #         unit.process_events(event)

        manager.update(time_delta)

        grid.update(inputs)
        grid.draw_grid(inputs)
        for player in players.values():             
            for unit in player.units:
                if grid.selected_tile and unit == grid.selected_tile.unit:
                    continue
                unit.update(inputs)
                unit.draw()
            for structure in player.structures:
                structure.draw()

        
        if grid.selected_tile:
            unit = grid.selected_tile.unit
            if unit:
                unit.update(inputs)
                unit.draw()


        #SpriteLayers.draw(screen)

        manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()
 

if __name__ == "__main__":
    game_loop()

    
