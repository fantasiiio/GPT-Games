from itertools import product
import copy

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

def is_within_grid(x, y, grid_width, grid_height):
    return 0 <= x < grid_width and 0 <= y < grid_height

def find_edge_touching_pieces(grid, shape, shape_x, shape_y, grid_x, grid_y):
    touching_pieces = set()
    
    grid_height, grid_width = len(grid), len(grid[0])
    shape_height, shape_width = len(shape), len(shape[0])
    adjacent_offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    # Instead of iterating through the entire shape, just loop through its edges
    for i in [0, shape_height - 1]:
        for j in range(shape_width):
            if shape[i][j]:
                for dx, dy in adjacent_offsets:
                    adj_x, adj_y = grid_x + j - shape_x + dx, grid_y + i - shape_y + dy
                    if is_within_grid(adj_x, adj_y, grid_width, grid_height):
                        if grid[adj_y][adj_x] != 0:
                            touching_pieces.add(grid[adj_y][adj_x])
    for j in [0, shape_width - 1]:
        for i in range(1, shape_height - 1):
            if shape[i][j]:
                for dx, dy in adjacent_offsets:
                    adj_x, adj_y = grid_x + j - shape_x + dx, grid_y + i - shape_y + dy
                    if is_within_grid(adj_x, adj_y, grid_width, grid_height):
                        if grid[adj_y][adj_x] != 0:
                            touching_pieces.add(grid[adj_y][adj_x])
                            
    return list(touching_pieces)

def is_move_valid(grid, shape, shape_x, shape_y, grid_x, grid_y):
    shape_height, shape_width = len(shape), len(shape[0])
    grid_height, grid_width = len(grid), len(grid[0])
    
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i][j]:
                grid_i, grid_j = grid_y + i - shape_y, grid_x + j - shape_x
                if not is_within_grid(grid_j, grid_i, grid_width, grid_height) or grid[grid_i][grid_j]:
                    return False
    return True

def place_shape_on_grid(grid, shape, shape_x, shape_y, grid_x, grid_y):
    shape_height, shape_width = len(shape), len(shape[0])
    grid_height, grid_width = len(grid), len(grid[0])
    
    for i in range(shape_height):
        for j in range(shape_width):
            if shape[i][j]:
                grid_i, grid_j = grid_y + i - shape_y, grid_x + j - shape_x
                if is_within_grid(grid_j, grid_i, grid_width, grid_height) and not grid[grid_i][grid_j]:
                    grid[grid_i][grid_j] = shape[i][j]
                else:
                    return False
    return True

def place_piece_on_all_corners_optimized(grid, available_corners, piece):
    possible_placements = []
    no_rotation, no_mirror, semi_symmetric = get_symmetry_flags(piece.shape) 

    for grid_corner in available_corners:
        for orientation, mirror in product(range(4), [False, True]):
            piece.orientation = orientation
            piece.mirror = mirror
            transformed_shape = piece.transform()
            piece_corners = identify_shape_corners(transformed_shape, 1)
            if (no_rotation and orientation > 0) or (no_mirror and mirror) or (semi_symmetric and orientation >= 2 and not mirror):
                continue
            for piece_corner in piece_corners:
                edge_touching = find_edge_touching_pieces(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[0], grid_corner[1])
                move_valid = not edge_touching and is_move_valid(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[0], grid_corner[1])
                if move_valid:
                    temp_grid = copy.deepcopy(grid)
                    if place_shape_on_grid(temp_grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[0], grid_corner[1]):
                        placement_info = {
                            'orientation': orientation,
                            'mirror': mirror,
                            'Grid pos': grid_corner,
                            'Piece pos': piece_corner,
                        }
                        possible_placements.append(placement_info)
        
    return possible_placements

def identify_grid_corners_positions(grid, player_id, check_outer_edges=True):
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
                            corner_positions.append((dy, dx))

    new_list = []
    if not check_outer_edges:
        for i in range(len(corner_positions)):
            if corner_positions[i][0] >= 0 and corner_positions[i][1] >= 0 and corner_positions[i][0] < cols and corner_positions[i][1] < rows:
                new_list.append(corner_positions[i])
    else:
        new_list = corner_positions

    return list(set(new_list))  # Remove duplicates

def get_symmetry_flags(shape):
    no_rotation = shape == list(zip(*reversed(shape)))  # Symmetric about the main diagonal
    no_mirror = shape == [list(reversed(row)) for row in shape]  # Symmetric about the vertical axis
    semi_symmetric = False  # Initialize as False

    # Check for semi-symmetry (180-degree rotational symmetry)
    rotated_180 = list(zip(*reversed(list(zip(*reversed(shape))))))
    if rotated_180 == shape:
        semi_symmetric = True

    return no_rotation, no_mirror, semi_symmetric

def is_between(min, number, max):
    return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]


def identify_shape_corners(grid, player_id):
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
                between = is_between((0, 0), (diag_x, diag_y), (cols, rows))
                if between and grid[diag_y][diag_x] == 0 or not between:
                    adj1_x, adj1_y = x + diagonal_and_adjacent[(dx, dy)][0][0], y + diagonal_and_adjacent[(dx, dy)][0][1]
                    adj2_x, adj2_y = x + diagonal_and_adjacent[(dx, dy)][1][0], y + diagonal_and_adjacent[(dx, dy)][1][1]
                    between1 = is_between((0, 0), (adj1_x, adj1_y), (cols, rows))
                    between2 = is_between((0, 0), (adj2_x, adj2_y), (cols, rows))
                    if between1 and grid[adj1_y][adj1_x] != player_id or not between1:
                        if between2 and grid[adj2_y][adj2_x] != player_id or not between2:
                            if not (x, y) in corners:
                                corners.append((x, y))

    return list(set(corners))

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
    [1, 1, 1],
    [0, 0, 1],
]


piece = Piece(w_shape, 2, 2)

# Now run 
# 
# the optimized function again
import time

start_time = time.time()
for i in range(1000):
    grid_available_corners = identify_grid_corners_positions(grid, 1, False)
    possible_placements_optimized = place_piece_on_all_corners_optimized(grid, grid_available_corners, piece)
    #print(len(possible_placements_optimized))

end_time = time.time()

elapsed_time = end_time - start_time
print(f"Function took {elapsed_time} seconds to run.")