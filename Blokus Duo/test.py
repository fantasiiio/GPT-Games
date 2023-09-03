# Here is the entire code, containing all the functions and classes developed so far.

from itertools import product
from collections import defaultdict
import copy

# Constants
GRID_SIZE = 5

sample_grid = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]
w_shape = [
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 1],
    [0, 0, 1]
]

# Define the Piece class
class Piece:
    def __init__(self, shape, shape_id, owner, orientation=0, mirror=False, position=None):
        self.shape = shape
        self.shape_id = shape_id
        self.owner = owner
        self.orientation = orientation
        self.mirror = mirror
        self.position = position

    def __eq__(self, other):
        if not isinstance(other, Piece):
            return False
        return self.shape_id == other.shape_id and self.owner == other.owner

    def transform(self):
        transformed_shape = [row.copy() for row in self.shape]
        if self.mirror:
            transformed_shape = [list(reversed(row)) for row in transformed_shape]
        for _ in range(self.orientation):
            transformed_shape = list(zip(*reversed(transformed_shape)))
        if self.orientation > 0:
            transformed_shape = [list(row) for row in transformed_shape]
        return transformed_shape

# Function to check for overlaps on the grid
def is_overlapping(grid, piece, row_from, col_from):
    transformed_piece = piece.transform()
    for i, row in enumerate(transformed_piece):
        for j, cell in enumerate(row):
            grid_x, grid_y = col_from + j, row_from + i
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if cell and grid[grid_y][grid_x] != 0:
                    return True
    return False

# Function to draw a grid with a specific piece placement
def draw_grid_with_placement(grid, piece, position):
    drawn_grid = [row.copy() for row in grid]
    transformed_piece = piece.transform()
    for i, row in enumerate(transformed_piece):
        for j, cell in enumerate(row):
            x, y = j + position[1], i + position[0]
            if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
                if cell:
                    drawn_grid[y][x] = "X"
    return drawn_grid

def is_within_grid(x, y, grid_width, grid_height):
    return 0 <= x < grid_width and 0 <= y < grid_height

def find_edge_touching_pieces(grid, shape, shape_x, shape_y, grid_x, grid_y):
    touching_pieces = set()
    
    grid_height, grid_width = len(grid), len(grid[0])
    shape_height, shape_width = len(shape), len(shape[0])
    
    # Offsets for checking adjacent cells
    adjacent_offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for i in range(shape_height):
        for j in range(shape_width):
            # If the cell in the shape is occupied
            if shape[i][j]:
                # Calculate the corresponding position on the grid
                grid_i, grid_j = grid_y + i - shape_y, grid_x + j - shape_x
                
                # Check adjacent cells in the grid
                for dx, dy in adjacent_offsets:
                    adj_x, adj_y = grid_j + dx, grid_i + dy
                    
                    # If the adjacent cell is within the grid boundaries
                    if is_within_grid(adj_x, adj_y, grid_width, grid_height):
                        # If the adjacent cell is occupied by a piece (not empty and not the same piece)
                        if grid[adj_y][adj_x] != 0:
                            touching_pieces.add(grid[adj_y][adj_x])
                            
    return list(touching_pieces)

def identify_corners_positions(grid, player_id, check_outer_edges=True):
    corner_positions = []
    rows = len(grid)
    cols = len(grid[0])

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == player_id:
                diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
                for dx, dy in diagonals:
                    if ((dx < 0 or dy < 0 or dx >= rows or dy >= cols)) or grid[dx][dy] == 0:
                        edge_touch = False
                        for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            new_dx, new_dy = dx + ddx, dy + ddy
                            if not((new_dx < 0 or new_dy < 0 or new_dx >= rows or new_dy >= cols)) and grid[new_dx][new_dy] == player_id:
                                edge_touch = True
                                break
                        if not edge_touch:
                            corner_positions.append((dx, dy))

    # remove position where x oy y is outsize of the grid
    new_list = []
    if not check_outer_edges:
        for i in range(len(corner_positions)):
            if corner_positions[i][0] >= 0 and corner_positions[i][1] >= 0 and corner_positions[i][0] < rows and corner_positions[i][1] < cols:
                new_list.append(corner_positions[i])
    else:
        new_list = corner_positions

    return list(set(new_list))  # Remove duplicates

# Function to check if a piece shape is symmetric
def get_symmetry_flags(shape):
    no_rotation = shape == list(zip(*reversed(shape)))  # Symmetric about the main diagonal
    no_mirror = shape == [list(reversed(row)) for row in shape]  # Symmetric about the vertical axis
    semi_symmetric = False  # Initialize as False

    # Check for semi-symmetry (180-degree rotational symmetry)
    rotated_180 = list(zip(*reversed(list(zip(*reversed(shape))))))
    if rotated_180 == shape:
        semi_symmetric = True

    return no_rotation, no_mirror, semi_symmetric

# Function to calculate the new position of a point after rotation and mirroring
def transform_point(point, rows, cols, orientation, mirror):
    x, y = point
    new_x, new_y = x, y
    for _ in range(orientation):
        new_x, new_y = y, rows - 1 - x
        x, y = new_x, new_y
    if mirror:
        new_x = cols - 1 - x
    return new_x, new_y

def place_shape_on_grid(grid, shape, row_from, col_from):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            grid_x, grid_y = col_from + j, row_from + i
            # Check if the position is within the grid boundaries
            if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                if cell:
                    grid[grid_y][grid_x] = 9  # Using 9 for visualization

def print_grid_with_piece(grid, shape, row_from, col_from):
    piece_shape = shape
    for i, row in enumerate(grid):
        row_str = ""
        for j, cell in enumerate(row):
            
            if 0 <= i - row_from < len(piece_shape) and 0 <= j - col_from < len(piece_shape[0]):
                cell = piece_shape[i - row_from][j - col_from]
                if cell != 0:
                    if cell == 1:
                        row_str += 'X '
                    elif cell == 3:
                        row_str += '+ '                    
                else:
                    # if cell != 0:
                    row_str += f"{cell} "
            else:
                #if cell != 0:
                row_str += f"{cell} "                    
        print(row_str)

def find_diagonal_neighbor(position, shape, player_id):
    rows = len(shape)
    cols = len(shape[0])
    i, j = position
    diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
    
    for dx, dy in diagonals:
        if 0 <= dx < rows and 0 <= dy < cols and shape[dx][dy] == player_id:
            return (dx, dy)
    return None

def is_shape_outside_grid(grid, shape, row_from, col_from):
    grid_rows = len(grid)
    grid_cols = len(grid[0])
    shape_rows = len(shape)
    shape_cols = len(shape[0])

    # Calculate the maximum row and column index for the shape on the grid
    max_row = row_from + shape_rows - 1
    max_col = col_from + shape_cols - 1
    
    # Check if any corner of the shape's bounding box is outside the grid
    if row_from < 0 or max_row >= grid_rows or col_from < 0 or max_col >= grid_cols:
        return True

    return False


def is_between(min, number, max):
    return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]

def identify_shape_corners(grid, player_id):
    empty_count = 0
    # Diagonal points and their respective adjacent points
    diagonal_and_adjacent = {
        (-1, -1): [(0, -1), (-1, 0)],
        (-1, 1): [(0, 1), (-1, 0)],
        (1, -1): [(0, -1), (1, 0)],
        (1, 1): [(0, 1), (1, 0)]
    }
    corners = []
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols): 
            if grid[y][x] == 0:
                continue     
            for dx, dy in diagonal_and_adjacent.keys():
                diag_x, diag_y = x + dx, y + dy
                between = False
                between = is_between((0, 0), (diag_x, diag_y), (cols, rows))
                if between and grid[diag_y][diag_x] == 0 or not between:
                    # Check the adjacent points for the diagonal
                    adj1_x, adj1_y = x + diagonal_and_adjacent[(dx, dy)][0][0], y + diagonal_and_adjacent[(dx, dy)][0][1]
                    adj2_x, adj2_y = x + diagonal_and_adjacent[(dx, dy)][1][0], y + diagonal_and_adjacent[(dx, dy)][1][1]
                    between1 = is_between((0, 0), (adj1_x, adj1_y), (cols, rows))
                    between2 = is_between((0, 0), (adj2_x, adj2_y), (cols, rows))
                    if between1 and grid[adj1_y][adj1_x] != player_id or not between1:
                        if between2 and grid[adj2_y][adj2_x] != player_id or not between2:
                            if not (x, y) in corners:
                                corners.append((x, y))

    list(set(corners))
    return corners

def identify_shape_corners(grid, player_id):
    empty_count = 0
    # Diagonal points and their respective adjacent points
    diagonal_and_adjacent = {
        (-1, -1): [(0, -1), (-1, 0)],
        (-1, 1): [(0, 1), (-1, 0)],
        (1, -1): [(0, -1), (1, 0)],
        (1, 1): [(0, 1), (1, 0)]
    }
    corners = []
    rows = len(grid)
    cols = len(grid[0])
    for y in range(rows):
        for x in range(cols): 
            if grid[y][x] == 0:
                continue     
            for dx, dy in diagonal_and_adjacent.keys():
                diag_x, diag_y = x + dx, y + dy
                between = False
                between = is_between((0, 0), (diag_x, diag_y), (cols, rows))
                if between and grid[diag_y][diag_x] == 0 or not between:
                    # Check the adjacent points for the diagonal
                    adj1_x, adj1_y = x + diagonal_and_adjacent[(dx, dy)][0][0], y + diagonal_and_adjacent[(dx, dy)][0][1]
                    adj2_x, adj2_y = x + diagonal_and_adjacent[(dx, dy)][1][0], y + diagonal_and_adjacent[(dx, dy)][1][1]
                    between1 = is_between((0, 0), (adj1_x, adj1_y), (cols, rows))
                    between2 = is_between((0, 0), (adj2_x, adj2_y), (cols, rows))
                    if between1 and grid[adj1_y][adj1_x] != player_id or not between1:
                        if between2 and grid[adj2_y][adj2_x] != player_id or not between2:
                            if not (x, y) in corners:
                                corners.append((x, y))

    list(set(corners))
    return corners

def place_shape_on_grid(grid, shape, shape_x, shape_y, grid_x, grid_y):
    # Get the dimensions of the shape and the grid
    shape_height, shape_width = len(shape), len(shape[0])
    grid_height, grid_width = len(grid), len(grid[0])
    
    # Check if the shape can be placed at the specified position
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i][j]:
                if (grid_y + i - shape_y < 0 or grid_y + i - shape_y >= grid_height or
                    grid_x + j - shape_x < 0 or grid_x + j - shape_x >= grid_width or
                    grid[grid_y + i - shape_y][grid_x + j - shape_x]):
                    return False
    
    # Place the shape on the grid
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i][j]:
                grid[grid_y + i - shape_y][grid_x + j - shape_x] = shape[i][j]
                
    return True

def print_grid(grid):
    for i, row in enumerate(grid):
        row_str = ""
        for j, cell in enumerate(row):
            cell = grid[i][j]
            if cell == 1:
                row_str += 'X '
            elif cell == 3:
                row_str += '+ '                    
            else:
                row_str += f"{cell} "
        print(row_str)

def is_move_valid(grid, shape, shape_x, shape_y, grid_x, grid_y):

    shape_height, shape_width = len(shape), len(shape[0])
    grid_height, grid_width = len(grid), len(grid[0])
    
    # Check if the shape can be placed at the specified position
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i][j]:
                if (grid_y + i - shape_y < 0 or grid_y + i - shape_y >= grid_height or
                    grid_x + j - shape_x < 0 or grid_x + j - shape_x >= grid_width or
                    grid[grid_y + i - shape_y][grid_x + j - shape_x]):
                    return False
    return True

def place_piece_on_all_corners_debug(grid, available_corners, piece):
    move_index = 0
    possible_placements = []
    no_rotation, no_mirror, semi_symmetric = get_symmetry_flags(piece.shape)
    print(f"Symmetry Flags - No Rotation: {no_rotation}, No Mirror: {no_mirror}, Semi Symmetric: {semi_symmetric}")
    

    
    for grid_corner in available_corners:
        print(f"\n\nChecking available corner: {grid_corner}")
        
        for orientation, mirror in product(range(4), [False, True]):
            piece.orientation = orientation
            piece.mirror = mirror
            transformed_shape = piece.transform()
            piece_corners = identify_shape_corners(transformed_shape, 1)
            print(f"Piece Corners: {piece_corners}")

            if (no_rotation and orientation > 0) or (no_mirror and mirror) or (semi_symmetric and orientation >= 2 and not mirror):
                print(f"Skipping due to symmetry flags - Orientation: {orientation}, Mirror: {mirror}")
                continue
            
            
            for piece_corner_idx, piece_corner in enumerate(piece_corners):
                move_index += 1
                print(move_index)
                print(f"\nChecking piece corner index: {piece_corner_idx}, piece corner: {piece_corner}")

                #is_outside = is_shape_outside_grid(grid, transformed_shape, grid_corner[0], grid_corner[1])
                edge_touching = find_edge_touching_pieces(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[1], grid_corner[0])
                #if not is_overlapping(grid, piece, piece_corner[0], piece_corner[1]) and not is_outside and not edge_touching:
                print(f"Valid placement found: Position: {piece_corner}, Orientation: {orientation}, Mirror: {mirror}, Piece Corner Index: {piece_corner_idx}")
                move_valid = not edge_touching and is_move_valid(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[1], grid_corner[0])
                if move_valid:
                    placement_info = {
                        'piece_corner_idx': piece_corner_idx,
                        'orientation': orientation,
                        'mirror': mirror,
                        'Grid pos': grid_corner,
                        'Piece pos': piece_corner,
                    }
                    print(placement_info)
                    possible_placements.append(placement_info)
                    temp_grid = copy.deepcopy(grid)
                    place_shape_on_grid(temp_grid, transformed_shape, piece_corner[0],piece_corner[1],  grid_corner[1], grid_corner[0])
                    temp_grid[grid_corner[0]][grid_corner[1]] = 3
                    print()
                    print("Grid after placing the piece:")
                    print_grid(temp_grid)#
                    print()
        
    possible_placements.sort(key=lambda x: (x['piece_corner_idx'], x['orientation'], x['mirror']))
    return possible_placements




# Initialize an empty 5x5 grid for the example
grid = [[0 for _ in range(10)] for _ in range(5)]
grid[3][0] = 1
grid[3][1] = 1
grid[4][0] = 1
grid[4][1] = 1
grid[4][2] = 1
grid[3][2] = 1

# Create a piece of shape "W"
w_shape = [
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 1],
]


piece = Piece(w_shape, 2, 2)
print_grid(grid)

# Identify available corners
available_corners = identify_corners_positions(grid, 1, False)
print(f"Available corners: {available_corners}")
possible_placements = place_piece_on_all_corners_debug(grid, available_corners, piece)
print(f"Possible placements: {len(possible_placements)}")