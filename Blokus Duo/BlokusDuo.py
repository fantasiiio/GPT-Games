import random
import math
import numpy as np
from tqdm import tqdm
from itertools import product
from collections import defaultdict
import pygame
import sys
from bitGrid import BitGrid
from MCTS import MCTS 
import time

# Initialize Pygame
pygame.init()

piece_count = 0
duplication_count = 0

class Move:
    def __init__(self, piece, shape_id,orientation,mirror,Piece_pos,Grid_pos, player_move_left_count):
        self.piece = piece
        self.shape_id = shape_id
        self.orientation = orientation
        self.mirror = mirror
        self.Piece_pos = Piece_pos
        self.Grid_pos = Grid_pos
        self.player_move_left_count = player_move_left_count

class Piece:
    def __init__(self, shape, shape_id, owner, orientation = 0, mirror = False, position = None):
        self.shape = shape
        self.shape_id = shape_id
        self.owner = owner
        self.orientation = orientation
        self.mirror = mirror
        self.position = position



    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return (self.shape_id == other.shape_id and 
                self.owner == other.owner)

    # Function to check if a piece shape is symmetric
    def get_symmetry_flags(self):
        no_rotation = self.shape == list(zip(*reversed(self.shape)))  # Symmetric about the main diagonal
        no_mirror = self.shape == [list(reversed(row)) for row in self.shape]  # Symmetric about the vertical axis
        semi_symmetric = False  # Initialize as False

        # Check for semi-symmetry (180-degree rotational symmetry)
        rotated_180 = list(self.shape(*reversed(list(zip(*reversed(self.shape))))))
        if rotated_180 == shape:
            semi_symmetric = True

        return no_rotation, no_mirror, semi_symmetric

    def is_between(self, min, number, max):
        return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]

    def identify_shape_corners(self, shape, player_id):
        # Diagonal points and their respective adjacent points
        diagonal_and_adjacent = {
            (-1, -1): [(0, -1), (-1, 0)],
            (-1, 1): [(0, 1), (-1, 0)],
            (1, -1): [(0, -1), (1, 0)],
            (1, 1): [(0, 1), (1, 0)]
        }
        corners = []
        rows = len(shape)
        cols = len(shape[0])
        for y in range(rows):
            for x in range(cols): 
                if shape[y][x] == 0:
                    continue     
                for dx, dy in diagonal_and_adjacent.keys():
                    diag_x, diag_y = x + dx, y + dy
                    between = False
                    between = self.is_between((0, 0), (diag_x, diag_y), (cols, rows))
                    if between and shape[diag_y][diag_x] == 0 or not between:
                        # Check the adjacent points for the diagonal
                        adj1_x, adj1_y = x + diagonal_and_adjacent[(dx, dy)][0][0], y + diagonal_and_adjacent[(dx, dy)][0][1]
                        adj2_x, adj2_y = x + diagonal_and_adjacent[(dx, dy)][1][0], y + diagonal_and_adjacent[(dx, dy)][1][1]
                        between1 = self.is_between((0, 0), (adj1_x, adj1_y), (cols, rows))
                        between2 = self.is_between((0, 0), (adj2_x, adj2_y), (cols, rows))
                        if between1 and shape[adj1_y][adj1_x] != player_id or not between1:
                            if between2 and shape[adj2_y][adj2_x] != player_id or not between2:
                                if not (x, y) in corners:
                                    corners.append((x, y))

        list(set(corners))
        return corners

    def is_between(self, min, number, max):
        return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]


    def transform(self):
        # Copy the original shape
        transformed_shape = [row.copy() for row in self.shape]

        # Apply mirror transformation if needed
        if self.mirror:
            transformed_shape = [list(reversed(row)) for row in transformed_shape]

        # Apply rotation transformation based on the orientation
        for _ in range(self.orientation):
            transformed_shape = list(zip(*reversed(transformed_shape)))

        # Convert tuples back to lists if rotations were applied
        if self.orientation > 0:
            transformed_shape = [list(row) for row in transformed_shape]

        return transformed_shape    

    def precompute_transforms_and_corners(self):
        all_transforms_and_corners = {}
        unique_transforms = set()
        
        # Initialize dictionaries for each orientation and mirror state
        for mirror in [0, 1]:  # 0 for False, 1 for True
            for orientation in range(4):
                
                self.orientation = orientation
                self.mirror = bool(mirror)
                transformed_shape = self.transform()
                
                # Convert the 2D array to a tuple of tuples to make it hashable
                transformed_shape_tuple = tuple(tuple(row) for row in transformed_shape)
                global piece_count
                piece_count +=1
                # Check if this transformed shape is unique
                if transformed_shape_tuple not in unique_transforms:
                    unique_transforms.add(transformed_shape_tuple)
                    
                    piece = Piece(transformed_shape, self.shape_id, self.owner, orientation, mirror) 
                    corners = self.identify_shape_corners(transformed_shape, 1)

                    if self.shape_id not in all_transforms_and_corners:
                        all_transforms_and_corners[self.shape_id] = {}
                    if orientation not in all_transforms_and_corners[self.shape_id]:
                        all_transforms_and_corners[self.shape_id][orientation] = {}
                    
                    all_transforms_and_corners[self.shape_id][orientation][mirror] = {
                        'transformed_piece': piece,
                        'transformed_shape': transformed_shape,
                        'corners': corners
                    }
                else:
                    global duplication_count
                    duplication_count += 1

        return all_transforms_and_corners


    def compress(self):
        """
        shape_id: 0-20 (5 bits)
        player: 0-1 (1 bit)
        position: (0-13, 0-13) for both x and y (4 bits each, total 8 bits)
        orientation: 0-3 (2 bits)
        mirror: 0-1 (1 bit)
        
        Total = 5 + 1 + 8 + 2 + 1 = 17 bits
        """
        compressed_value = 0
        compressed_value |= self.shape_id
        compressed_value |= (self.owner << 5)
        # compressed_value |= (self.position[0] << 6)
        # compressed_value |= (self.position[1] << 10)
        compressed_value |= (self.orientation << 14)
        compressed_value |= (self.mirror << 16)
        
        return compressed_value

    def decompress(self, compressed_value):
        mirror = (compressed_value >> 16) & 1
        orientation = (compressed_value >> 14) & 3
        # position_y = (compressed_value >> 10) & 15
        # position_x = (compressed_value >> 6) & 15
        owner = (compressed_value >> 5) & 1
        shape_id = compressed_value & 31
        
        return shape_id, owner, orientation, mirror

max_piece_per_player = 12

class Board:
    def __init__(self, bit_grid , player = 1, is_terminal = 666, last_move=None, move_history=[], winner=None, all_possible_moves = None):
        self.all_possible_moves = all_possible_moves
        self.player_move_left_count  = {1:-1, 2:-1}
        self.bit_grid = bit_grid #if bit_grid is not None else BitGrid(2)
        self.reward = {1:0, 2:0}
        self.player = player
        self.cell_size = CELL_SIZE        
        self.screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
        self.available_pieces = {1:[], 2:[]}
        self.selected_piece_index = {1:0, 2:0}
        self.placed_pieces = {1:[], 2:[]}
        self.move_history = move_history
        self.unexplored_moves = []
        self.is_terminal = is_terminal
        self.last_move = last_move
        self.children = []
        self.winner = winner
        self.visited = False
        self.N = {1: 0, 2:0}
        self.win_count = {1: 0, 2: 0}
        self.uct_value = {1: 0, 2: 0}
        self.depth = -1
        self.simulation_paths = []
        self.simulated = False
        self.hash = hash(tuple(self.bit_grid.compressed_grid))
        self.move_index = 0
        self.count = 0
    
    def is_between(self, min, number, max):
        return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]

    def is_board_empty(self):
        for bits in self.bit_grid.compressed_grid:
            if bits != 0:
                    return False
        return True

    def identify_grid_corners_positions(self, player_id, check_outer_edges=True):
        corner_positions = []
        rows = GRID_SIZE
        cols = GRID_SIZE

        if len(self.available_pieces[player_id]) == 21 :
            corner_cells = [(0, 0), (0, rows-1), (cols-1, 0), (cols-1, rows-1)]
            for x, y in corner_cells:
                if self.bit_grid.read(x,y) == 0:
                    corner_positions.append((x, y))
            return corner_positions


        for i in range(rows):
            for j in range(cols):
                if self.bit_grid.read(i,j) == player_id:
                    diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
                    for dx, dy in diagonals:
                        if ((dx < 0 or dy < 0 or dx >= rows or dy >= cols)) or self.bit_grid.read(dx,dy) == 0:
                            edge_touch = False
                            for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                new_dx, new_dy = dx + ddx, dy + ddy
                                if not((new_dx < 0 or new_dy < 0 or new_dx >= rows or new_dy >= cols)) and self.bit_grid.read(new_dx,new_dy) == player_id:
                                    edge_touch = True
                                    break
                            if not edge_touch:
                                corner_positions.append((dx, dy))

        # remove position where x oy y is outsize of the grid
        new_list = []
        if not check_outer_edges:
            for i in range(len(corner_positions)):
                if corner_positions[i][0] >= 0 and corner_positions[i][1] >= 0 and corner_positions[i][0] < cols and corner_positions[i][1] < rows:
                    new_list.append(corner_positions[i])
        else:
            new_list = corner_positions

        return list(set(new_list))  # Remove duplicates

    def draw_grid(self):
        uncompressed_grid = self.bit_grid.decompress_grid_x_bits()
        for x in range(0, self.cell_size * len(uncompressed_grid), self.cell_size):
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, self.cell_size * len(uncompressed_grid)))
        for y in range(0, self.cell_size * len(uncompressed_grid), self.cell_size):
            pygame.draw.line(self.screen, WHITE, (0, y), (self.cell_size * len(uncompressed_grid), y))
    
    def draw_piece(self, transormed_piece, x, y, color):
        # transormed_piece = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
        if not color:
            color = (100,100,100) if piece.owner == 2 else (200,200,200)
        for i, row in enumerate(transormed_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, color, 
                                     ((x + j) * self.cell_size, (y + i) * self.cell_size, self.cell_size, self.cell_size))

    def draw_board(self):
        uncompressed_grid = self.bit_grid.decompress_grid_x_bits()

        # Plot each cell in the grid
        for i, row in enumerate(uncompressed_grid):
            for j, cell in enumerate(row):
                if cell:
                    color = (100,100,100) if cell == 2 else (200,200,200) if cell == 1 else (0,0,0)                   
                    pygame.draw.rect(self.screen, color, 
                                     (j * self.cell_size,i * self.cell_size, self.cell_size, self.cell_size))


    def highlight_available_corners(self, transformed_piece, x, y):
        # Get the available corners for the given player
        #piece = self.get_selected_piece()
        available_corners = piece_cache[transformed_piece.shape_id][transformed_piece.orientation][transformed_piece.mirror]['corners']

        # Highlight the available corners with a special value (using -1 for demonstration)
        for col, row in available_corners:
            pygame.draw.rect(self.screen, (144,238,144), 
                                     ((col + x) * self.cell_size, (row + y) * self.cell_size, self.cell_size, self.cell_size))            


        # available_corners = self.identify_grid_corners_positions()
        
        # # Highlight the available corners with a special value (using -1 for demonstration)
        # for row, col in available_corners:
        #     pygame.draw.rect(self.screen, (144,238,144), 
        #                              ((col) * self.cell_size, (row) * self.cell_size, self.cell_size, self.cell_size))            

    def place_piece(self, transformed_piece, x, y):
        self.placed_pieces[self.player].append(transformed_piece)
        self.available_pieces[self.player].remove(transformed_piece.shape_id)
        self.selected_piece_index[self.player] = 0   
        self.move_history.append(transformed_piece.compress())    
        # Loop through each cell in the shape template
        # transformed_piece = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
            
        for i, row in enumerate(transformed_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.bit_grid.write(y + i,x + j, transformed_piece.owner)
    
    def switch_player(self):
        self.player = 1 if self.player == 2 else 2
              


    def load_piece_data_from_file(self, file_path):
        # Initialize an empty list to store the pieces
        pieces = []
        
        # Read the file and split it into pieces
        with open(file_path, 'r') as f:
            piece_data_str = f.read()
            pieces_str = piece_data_str.strip().split("---")
        
        # Loop through each piece string to convert it into a 2D array
        for piece_str in pieces_str:
            piece_rows_str = piece_str.strip().split("\n")
            piece = [[int(cell) for cell in row.split()] for row in piece_rows_str]
            pieces.append(piece)
        
        return pieces
    
    def select_next_available_piece(self, direction):
        global shape_index
        self.selected_piece_index[self.player] += direction
        if self.selected_piece_index[self.player] < 0:
            self.selected_piece_index[self.player] = len(self.available_pieces[self.player]) - 1
        self.selected_piece_index[self.player] %= len(self.available_pieces[self.player])
        shape_index = self.selected_piece_index[self.player]
        return piece_cache[shape_index][0][0]['transformed_piece']

    def get_selected_piece(self):
        shape_index = self.available_pieces[self.player][self.selected_piece_index[self.player]]
        piece = piece_cache[shape_index][0][0]['transformed_piece']
        return piece

    def is_overlapping(self, transformed_piece, col_from, row_from):
        # transformed_piece = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
        for i, row in enumerate(transformed_piece.shape):
            for j, cell in enumerate(row):
                grid_x, grid_y = col_from + j, row_from + i
                # Check if the position is within the grid boundaries
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    if cell and self.bit_grid.read(grid_y, grid_x):
                        return True  # Overlap detected
        return False

    def draw_piece_perimeter(self, transformed_piece, x, y, color):
        line_width = 5
        #transformed_shape = piece_cache[piece.shape_id][piece.orientation][piece.mirror]['transformed_shape']
        
        # Draw perimeter line for the transformed shape
        for i, row in enumerate(transformed_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        neighbor_x, neighbor_y = j + dx, i + dy
                        
                        # Check if the neighboring cell is outside the piece
                        if 0 <= neighbor_x < len(row) and 0 <= neighbor_y < len(transformed_piece.shape):
                            is_empty_inside = transformed_piece.shape[neighbor_y][neighbor_x] == 0
                        else:
                            is_empty_inside = True  # Treat cells outside the shape boundary as empty
                        
                        if is_empty_inside:
                            if dx == -1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)
                            elif dx == 1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j + 1) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)
                            elif dy == -1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i) * self.cell_size],
                                                line_width)
                            elif dy == 1:
                                pygame.draw.line(self.screen, color,
                                                [(x + j) * self.cell_size, (y + i + 1) * self.cell_size],
                                                [(x + j + 1) * self.cell_size, (y + i + 1) * self.cell_size],
                                                line_width)




    def find_corner_touching_pieces(self, piece, row, col):
        corners = []
        piece_rows = len(piece.shape)
        piece_cols = len(piece.shape[0])
        for i in range(piece_rows):
            for j in range(piece_cols):
                if piece.shape[i][j] == 1:
                    grid_row = row + i
                    grid_col = col + j
                    corner_count = 0
                    # Check the corners of the piece cell
                    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                        corner_row = grid_row + dx
                        corner_col = grid_col + dy
                        if 0 <= corner_row < GRID_SIZE and 0 <= corner_col < GRID_SIZE:
                            corner_cell = self.bit_grid.read(corner_row, corner_col)
                            if corner_cell == piece.owner:
                                corner_count += 1

                    if corner_count >= 1:
                        corners.append((grid_row, grid_col))

        return corners
    
    def is_within_grid(self, x, y, grid_width, grid_height):
        return 0 <= x < grid_width and 0 <= y < grid_height

    def is_shape_within_grid(self, shape, x, y):
        shape_rows = len(shape)
        shape_cols = len(shape[0])
        grid_rows = GRID_SIZE
        grid_cols = GRID_SIZE
        
        # Check if the shape will fit within the grid at the specified (x, y) position
        if x + shape_cols <= grid_cols and y + shape_rows <= grid_rows:
            return True
        else:
            return False

    def find_edge_touching_pieces(self, shape, shape_x, shape_y, grid_x, grid_y):
        touching_pieces = set()
        
        grid_height, grid_width = GRID_SIZE, GRID_SIZE
        shape_height, shape_width = len(shape), len(shape[0])
        adjacent_offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    grid_i, grid_j = grid_y + i - shape_y, grid_x + j - shape_x
                    for dx, dy in adjacent_offsets:
                        adj_x, adj_y = grid_j + dx, grid_i + dy
                        if self.is_within_grid(adj_x, adj_y, grid_width, grid_height):
                            if self.bit_grid.read(adj_y,adj_x) != 0:
                                return True
                                
        return False
            
    def is_move_valid(self, shape, shape_x, shape_y, grid_x, grid_y):

        shape_height, shape_width = len(shape), len(shape[0])
        grid_height, grid_width = GRID_SIZE, GRID_SIZE
        
        # Check if the shape can be placed at the specified position
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    if (grid_y + i - shape_y < 0 or grid_y + i - shape_y >= grid_height or
                        grid_x + j - shape_x < 0 or grid_x + j - shape_x >= grid_width or
                        self.bit_grid.read(grid_x + j - shape_x, grid_y + i - shape_y) != 0):
                        return False
        return True

    def place_piece_on_grid(self, piece, shape_x, shape_y, grid_x, grid_y):
        self.placed_pieces[self.player].append(piece)
        self.available_pieces[self.player].remove(piece.shape_id)
        self.selected_piece_index[self.player] = 0   
        board_move = Move(piece, piece.shape_id, piece.orientation, piece.mirror, (shape_x, shape_y), (grid_x, grid_y), self.player_move_left_count)
        self.move_history.append(board_move)  
        shape = piece.shape
        shape_height, shape_width = len(shape), len(shape[0])
        
        # Place the shape on the grid
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    self.bit_grid.write(grid_x + j - shape_x, grid_y + i - shape_y, piece.owner)
                    
        return True

    def get_all_possible_moves(self):
        move_index = 0
        possible_placements = {1:[], 2:[]}
        
        for player in [1, 2]:
            available_corners = self.identify_grid_corners_positions(player, False)
            for grid_corner in available_corners:
                for shape_id in self.available_pieces[player]:
                    rotation_count = len(piece_cache[shape_id])                    
                    for orientation in range(rotation_count):
                        mirror_count = len(piece_cache[shape_id][orientation])
                        for mirror in range(mirror_count):
                            transformed_shape = piece_cache[shape_id][orientation][mirror]['transformed_shape']
                            piece_corners = piece_cache[shape_id][orientation][mirror]['corners']

                            for piece_corner_idx, piece_corner in enumerate(piece_corners):
                                edge_touching = self.find_edge_touching_pieces(transformed_shape, piece_corner[0], piece_corner[1], grid_corner[0], grid_corner[1])
                                move_valid = not edge_touching and self.is_move_valid(transformed_shape, piece_corner[0], piece_corner[1], grid_corner[0], grid_corner[1])
                                if move_valid:
                                    move_index += 1

                                    placement_info = {
                                        'shape_id': shape_id,
                                        'piece_corner_idx': piece_corner_idx,
                                        'orientation': orientation,
                                        'mirror': mirror,
                                        'Grid_pos': grid_corner,
                                        'Piece_pos': piece_corner,
                                    }
                                    possible_placements[player].append(placement_info)
                                    
        return possible_placements 


    def get_board_score(self):                  
        self.player_score = self.count_filled_cells()
        return self.player_score

    def piece_overlaps_corners(self, piece, base_x, base_y):
        # Define the four corners and their adjacent positions
        corners = [
            (0, 0),
            (0, GRID_SIZE-1), 
            (GRID_SIZE-1, 0), 
            (GRID_SIZE-1, GRID_SIZE-1)
        ]
        
        piece_rows = len(piece.shape)
        piece_cols = len(piece.shape[0])
        for i in range(piece_rows):
            for j in range(piece_cols):
                pos_x = base_x + j
                pos_y = base_y + i
                if piece.shape[i][j] == 1 and (pos_x, pos_y) in corners:
                    return True
        return False

    def update_win_count(self, winner):
        if winner in self.win_count:
            self.win_count[winner] += 1
            
    def print_grid(self):
        grid = self.bit_grid.decompress_grid_x_bits()
        print("-" * 30)
        for i, row in enumerate(grid):
            row_str = ""
            for j, cell in enumerate(row):
                cell = grid[i][j]
                if cell == 1:
                    row_str += '+ '
                elif cell == 2:
                    row_str += 'x '                    
                else:
                    row_str += f"  "
            print(row_str)
        print()



    def create_children(self, children_index):        
        opponent = 3 - self.player

        new_bit_grid = self.bit_grid.copy()
        new_history = self.move_history[:]
        move = self.all_possible_moves[opponent][children_index]
        piece = piece_cache[move["shape_id"]][move['orientation']][move['mirror']]["transformed_piece"]
        board_move = Move(piece, move["shape_id"], move['orientation'], move['mirror'], move['Piece_pos'], move['Grid_pos'], self.player_move_left_count)
        new_history.append(board_move)
        new_board = Board(bit_grid=new_bit_grid, player=opponent, last_move=board_move, move_history=new_history)
        
        piece.owner = opponent
        new_board.available_pieces[1] = self.available_pieces[1][:]
        new_board.available_pieces[2] = self.available_pieces[2][:]
        
        new_board.all_possible_moves = new_board.get_all_possible_moves()
        new_board.player_move_left_count[1] = len(new_board.all_possible_moves[1])
        new_board.player_move_left_count[2] = len(new_board.all_possible_moves[2])
        new_board.is_terminal = new_board.calc_final_score()
        new_board.reward = new_board.get_board_score()
        new_board.place_piece_on_grid(new_board.last_move.piece, new_board.last_move.Piece_pos[0], new_board.last_move.Piece_pos[1], new_board.last_move.Grid_pos[0], new_board.last_move.Grid_pos[1])
            #piece, piece_corner[0], piece_corner[1], grid_pos[0], grid_pos[1])
        if new_board.is_terminal[0]:
            new_board.winner = new_board.player            
            new_board.update_win_count(new_board.winner)          
        # new_board.all_possible_moves = new_board.get_all_possible_moves()
        self.children.append(new_board)
        self.move_index += 1
 
        return new_board

    def count_filled_cells(self):
        count = {1:0, 2:0}
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell_value = self.bit_grid.read(x, y)
                if cell_value != 0:
                    count[cell_value] += 1
        return count
    
    def calc_final_score(self):
        # Check if no more valid moves exist for both players
        no_moves_player1 = self.player_move_left_count[1] == 0
        no_moves_player2 = self.player_move_left_count[2] == 0

        # If both players have no more valid moves
        if no_moves_player1 and no_moves_player2:
            

            # Determine the winner
            if self.player_score[1] > self.player_score[2]:
                return (True, 1)  # Player 1 wins
            elif self.player_score[1] < self.player_score[2]:
                return (True, 2)  # Player 2 wins
            else:
                return (True, 0)  # Draw

        # If the game is not over yet
        return (False, None)        

    def get_mcts_move_single(self):
        mcts = MCTS()
        for _ in tqdm(range(10), desc="Running MCTS"):
            mcts.do_rollout(self)

        # mcts.propagate_win_count_root()
        # mcts.draw_tree(self.node)

        return mcts.choose(self)

    def update_board_state(self, piece, move):
        self.get_all_possible_moves()
    
    def find_random_child(self):
        if self.is_terminal[0]:
            return None
        
        if not self.children:
            move_count = len(self.all_possible_moves[3-self.player])
            best_child_index = np.random.choice(move_count)
            self.unexplored_moves = list(range(0, move_count))
            #best_child = self.create_children(best_child_index)
        else:
            best_child_index = self._uct_select(self.children)

        if self.unexplored_moves.index(best_child_index) != -1:
            self.unexplored_moves.remove(best_child_index)
            best_child = self.create_children(best_child_index)

          
        return best_child


    def _uct_select(self, nodeList):
        total_simulations = self.N[1] + self.N[2]
        total_simulations = 1 if total_simulations == 0 else total_simulations
        log_N = math.log(total_simulations)
        
        C = 2

        def uct(n):
            N = n.N[n.player]+1
            if N == 0:
                return float("inf")

            exploitation_value = n.win_count[n.player] / (N)
            if total_simulations > 0:
                exploration_value = C * math.sqrt(log_N / (N))
            else:
                exploration_value = 0
            return exploitation_value + exploration_value

        best_value = 0
        best_child = None
        for child in self.children:
            value = uct(child)
            if value > best_value:
                best_value = value
                best_child = child 

        unexplored_child_uct_value = C * math.sqrt(log_N)
        if unexplored_child_uct_value > best_value:
            return random.choice(self.unexplored_moves)
        
        index_of_best_child = nodeList.index(best_child)
        return index_of_best_child

    def run_game(self):
        turn = 1
        clock = pygame.time.Clock()
        selected_piece = piece_cache[0][0][0]['transformed_piece']
        game_over = False
        while not game_over:
            if turn == 2:
                self = self.get_mcts_move_single()
                turn = 3 - turn
                terminal = self.node.check_terminal()
                if terminal[0]:
                    self.end_game(self.node.player)
                    game_over = True
            else:   
            # turn = 3 - turn     
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        x, y = event.pos
                        grid_x, grid_y = x // CELL_SIZE, y // CELL_SIZE
                        
                        # Left click
                        if event.button == 1:
                            if selected_piece is not None:
                                if move_is_valid:
                                    self.place_piece(selected_piece, grid_x, grid_y)
                                    selected_piece = None
                                    turn = 3 - turn

                            else:
                                selected_piece = self.get_selected_piece()
                                selected_piece.owner = self.player
            

                        # Right click for rotation
                        elif event.button == 3:
                            if selected_piece is not None:
                                orientation = (selected_piece.orientation + 1) % len(piece_cache[selected_piece.shape_id])
                                selected_piece = piece_cache[selected_piece.shape_id][orientation][selected_piece.mirror]['transformed_piece']
                                selected_piece.owner = self.player


                        # Middle click for mirror
                        elif event.button == 2:
                            if selected_piece is not None:
                                mirror = (selected_piece.mirror + 1) % len(piece_cache[selected_piece.shape_id][selected_piece.orientation])
                                selected_piece = piece_cache[selected_piece.shape_id][selected_piece.orientation][mirror]['transformed_piece']
                                selected_piece.owner = self.player

                        # Mouse wheel scroll
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 4:  # Scroll up
                                selected_piece = self.select_next_available_piece(1)                       
                            elif event.button == 5:  # Scroll down
                                selected_piece = self.select_next_available_piece(-1)
                            selected_piece.orientation = 0
                            selected_piece.mirror = False
                                                                                    
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_board()

            if selected_piece is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = mouse_x // CELL_SIZE , mouse_y // CELL_SIZE
                overlapping = self.is_overlapping(selected_piece, grid_x, grid_y)
                corner_touching = self.find_corner_touching_pieces(selected_piece, grid_y, grid_x)
                edge_touching = self.find_edge_touching_pieces(selected_piece.shape, 0,0,grid_x, grid_y)
                touching = not edge_touching and corner_touching
                is_within = self.is_shape_within_grid(selected_piece.shape, grid_x, grid_y)

                first_move = len(self.placed_pieces[self.player]) == 0
                if first_move:
                    move_is_valid = self.piece_overlaps_corners(selected_piece, grid_x, grid_y) and is_within
                else:
                    move_is_valid = touching and is_within and not overlapping            

                border_color = (255,0,0) if not move_is_valid else (0,255,0) 
                if move_is_valid:
                    move_is_valid = True
                    color = (0,255,0)
                    border_color = (0,255,0)


                if self.is_overlapping(selected_piece, grid_x, grid_y):
                    color = (100,0,0) 
                else:
                    color = (100,100,100) if self.player == 2 else (200,200,200)

                self.draw_piece(selected_piece, grid_x, grid_y, color)
                self.draw_piece_perimeter(selected_piece, grid_x, grid_y, border_color)
                # self.highlight_available_corners(selected_piece, grid_x, grid_y)

                pygame.display.update()
                clock.tick(30)

move_is_valid = False

# Constants
GRID_SIZE = 14
CELL_SIZE = 40
SCREEN_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

game_board = None
piece_cache = {}

def init_game():
    global piece_cache
    global game_board
    # Initialize board
    def create_2d_array(rows, cols):
        return [[0 for _ in range(cols)] for _ in range(rows)]

    board = create_2d_array(GRID_SIZE, GRID_SIZE)
    game_board = Board(BitGrid(2, board))

    shapes = game_board.load_piece_data_from_file("blokus_duo_tiles.txt")

    for shape_id, shape in enumerate(shapes):
        piece = Piece(shape, shape_id, 1)
        info = piece.precompute_transforms_and_corners()
        piece_cache[shape_id] = info[shape_id]

    for player in range(1, 3):
        piece_id_counter = 0
        for shape in shapes:
            game_board.available_pieces[player].append(piece_id_counter)
            piece_id_counter += 1

    game_board.all_possible_moves = game_board.get_all_possible_moves()
    game_board.is_terminal = game_board.calc_final_score()

    pygame.display.set_caption('blokus duo Game')

init_game()
game_board.run_game()
