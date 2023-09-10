import random
import pygame
import pygame_gui
import sys
from grid import Grid 
from Player import Player 
from Soldier import Soldier
from BTR import BTR
import pygame.mixer
from config import screen, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, TILES_X, TILES_Y, GRAY

pygame.mixer.init()



# Initialize pygame
pygame.init()
# Set up the display
screen = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT))
pygame.display.set_caption('Strategy Game')
manager = pygame_gui.UIManager((GRID_WIDTH, GRID_HEIGHT))

grid = Grid(pygame, screen, "C:\\dev-fg\\tiled-test\\terrain1.tmx")
players = {1: Player(1, True), 2: Player(2, False)}

def handle_mouse_click(pos):
    selected_tile = grid.selected_tile
    x, y = pos
    clicked_tile = grid.get_tile_from_coords(x, y)
    
    if clicked_tile != selected_tile:
        # If the clicked tile has a unit and he is doing an action, don't change the selected tile
        if not (grid.selected_tile and grid.selected_tile.unit and grid.selected_tile.unit.current_action != None):
            grid.selected_tile = clicked_tile
    else:
        if not (grid.selected_tile and grid.selected_tile.unit):
            grid.selected_tile = None  # Deselect if the same tile is clicked again

def handle_right_click(pos):
    selected_tile = grid.selected_tile
    if selected_tile and selected_tile.unit:
        x, y = pos
        target_tile = grid.get_tile_from_coords(x, y)
        # if target_tile.unit and selected_tile.unit.can_attack(target_tile):
        #     selected_tile.unit.attack(target_tile.unit)
        # elif not target_tile.unit and not target_tile.structure:
        #     # Assume the player wants to build a farm for now
        #     grid.selected_tile = target_tile
        #     selected_tile.unit.move(target_tile)
        # elif target_tile.unit:
        #     if selected_tile.unit.player != target_tile.unit.player:
        #         selected_tile.unit.fire(target_tile)
            


def check_game_end():
    # Check if either player has no units left
    if not players[1].units:
        return "AI Wins!"
    elif not players[2].units:
        return "Human Wins!"
    return None

player_initial_pos = {1: (2, 2), 2: (4, 2)}
players[1].add_unit(Soldier(grid.tiles[player_initial_pos[1][0]][player_initial_pos[1][1]], 1, grid, screen=screen, gun_sound_file="assets\\sounds\\pistol.wav"))
players[1].add_unit(BTR(grid.tiles[6][6], 1, grid, screen=screen, gun_sound_file="assets\\sounds\\machinegun.wav"))

players[2].add_unit(Soldier(grid.tiles[player_initial_pos[2][0]][player_initial_pos[2][1]], 2, grid, screen=screen, gun_sound_file="assets\\sounds\\pistol.wav"))

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


def mouse_move(event):
    grid.mouse_over_tile = grid.get_tile_from_coords(event.pos[0], event.pos[1])

# Main game loop
running = True

def game_loop():
    """Main game loop."""

    # Main game loop
    running = True
    mouse_pos = (0,0)
    while running:
        time_delta = pygame.time.Clock().tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    handle_mouse_click(event.pos)
                elif event.button == 3:  # Right click
                    handle_right_click(event.pos)

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == end_turn_button:
                        unit.action_points = 10
                        update_ui()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                mouse_move(event)

            manager.process_events(event)
            for player in players.values(): 
                for unit in player.units:
                    unit.process_events(event)

        manager.update(time_delta)

        grid.draw_grid()
        for player in players.values(): 
            for unit in player.units:
                unit.update(mouse_pos)
                unit.draw()
            for structure in player.structures:
                structure.draw()
        manager.draw_ui(screen)

        pygame.display.flip()

    pygame.quit()
 

if __name__ == "__main__":
    game_loop()

    
