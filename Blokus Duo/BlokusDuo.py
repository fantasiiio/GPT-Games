from itertools import product
from collections import defaultdict
import pygame
import sys
from bitGrid import BitGrid

# Initialize Pygame
pygame.init()

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

    def identify_shape_corners(self, grid):
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
                    between = self.is_between((0, 0), (diag_x, diag_y), (cols, rows))
                    if between and grid[diag_y][diag_x] == 0 or not between:
                        # Check the adjacent points for the diagonal
                        adj1_x, adj1_y = x + diagonal_and_adjacent[(dx, dy)][0][0], y + diagonal_and_adjacent[(dx, dy)][0][1]
                        adj2_x, adj2_y = x + diagonal_and_adjacent[(dx, dy)][1][0], y + diagonal_and_adjacent[(dx, dy)][1][1]
                        between1 = self.is_between((0, 0), (adj1_x, adj1_y), (cols, rows))
                        between2 = self.is_between((0, 0), (adj2_x, adj2_y), (cols, rows))
                        if between1 and grid[adj1_y][adj1_x] != self.owner or not between1:
                            if between2 and grid[adj2_y][adj2_x] != self.owner or not between2:
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
        
        # Initialize dictionaries for each orientation and mirror state
        for orientation in range(4):
            for mirror in [0, 1]:  # 0 for False, 1 for True
                if self.shape_id not in all_transforms_and_corners:
                    all_transforms_and_corners[self.shape_id] = {}
                if orientation not in all_transforms_and_corners[self.shape_id]:
                    all_transforms_and_corners[self.shape_id][orientation] = {}
                
                self.orientation = orientation
                self.mirror = bool(mirror)
                transformed_shape = self.transform()
                piece = Piece(transformed_shape, self.shape_id, self.owner, orientation, mirror) 
                #self.shape = transformed_shape
                corners = self.identify_shape_corners(transformed_shape)
                
                all_transforms_and_corners[self.shape_id][orientation][mirror] = {
                    'transformed_piece': piece,
                    'transformed_shape': transformed_shape,
                    'corners': corners
                }

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
        compressed_value |= (player << 5)
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
        player = (compressed_value >> 5) & 1
        shape_id = compressed_value & 31
        
        return shape_id, player, (position_x, position_y), orientation, mirror

max_piece_per_player = 12

class Board:
    def __init__(self, size, cell_size, bit_grid = None, player = 1, is_terminal = False, last_move=None, move_history=[], winner=None):
        self.uncompressed_grid = [[0 for _ in range(size)] for _ in range(size)]
        self.bit_grid = bit_grid if bit_grid is not None else BitGrid(2)
        self.bit_grid.compress_grid_x_bits(self.uncompressed_grid)
        self.player = player
        self.cell_size = cell_size        
        self.screen = pygame.display.set_mode((size * cell_size, size * cell_size))
        self.available_pieces = {1:[], 2:[]}
        self.selected_piece_index = {1:0, 2:0}
        self.placed_pieces = {1:[], 2:[]}
        self.move_history = move_history
        self.move_history.copy()

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

    def is_between(self, min, number, max):
        return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]

    def identify_grid_corners_positions(self):
        corner_positions = []
        rows = len(self.uncompressed_grid)
        cols = len(self.uncompressed_grid[0])

        for i in range(rows):
            for j in range(cols):
                if self.uncompressed_grid[i][j] == self.player:
                    diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
                    for dx, dy in diagonals:
                        if ((dx < 0 or dy < 0 or dx >= rows or dy >= cols)) or self.uncompressed_grid[dx][dy] == 0:
                            edge_touch = False
                            for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                new_dx, new_dy = dx + ddx, dy + ddy
                                if not((new_dx < 0 or new_dy < 0 or new_dx >= rows or new_dy >= cols)) and self.uncompressed_grid[new_dx][new_dy] == self.player:
                                    edge_touch = True
                                    break
                            if not edge_touch:
                                corner_positions.append((dx, dy))

        new_list = []
        for i in range(len(corner_positions)):
            if corner_positions[i][0] >= 0 and corner_positions[i][1] >= 0 and corner_positions[i][0] < rows and corner_positions[i][1] < cols:
                new_list.append(corner_positions[i])

        return list(set(new_list))  # Remove duplicates

    def draw_grid(self):
        for x in range(0, self.cell_size * len(self.uncompressed_grid), self.cell_size):
            pygame.draw.line(self.screen, WHITE, (x, 0), (x, self.cell_size * len(self.uncompressed_grid)))
        for y in range(0, self.cell_size * len(self.uncompressed_grid), self.cell_size):
            pygame.draw.line(self.screen, WHITE, (0, y), (self.cell_size * len(self.uncompressed_grid), y))
    
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
        # Plot each cell in the grid
        for i, row in enumerate(self.uncompressed_grid):
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
        self.available_pieces[self.player].remove(transformed_piece)
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
        

    # Function to identify corners of shapes
    def identify_corners_positions(self, grid, player_id):
        corner_positions = []
        rows = len(grid)
        cols = len(grid[0])
        
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == player_id:
                    diagonals = [(i-1, j-1), (i-1, j+1), (i+1, j-1), (i+1, j+1)]
                    for dx, dy in diagonals:
                        #if dx < 0 or dy < 0 or dx >= rows or dy >= cols:
                         #   continue  # Skip negative positions and positions out of grid
                        if dx < 0 or dy < 0 or dx >= rows or dy >= cols or grid[dx][dy] == 0:
                            edge_touch = False
                            # Check if the corner shares an edge with any of the player's pieces
                            for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                                new_dx, new_dy = dx + ddx, dy + ddy
                                #if 0 <= new_dx < rows and 0 <= new_dy < cols:
                                if not(new_dx < 0 or new_dy < 0 or new_dx >= rows or new_dy >= cols) and grid[new_dx][new_dy] == player_id:
                                    edge_touch = True
                                    break
                            if not edge_touch:
                                corner_positions.append((dx, dy))
                                
        return list(set(corner_positions))  # Remove duplicates

        


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
        return self.available_pieces[self.player][shape_index]

    def get_selected_piece(self):
        return self.available_pieces[self.player][self.selected_piece_index[self.player]]

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
    
    def is_within_grid(self, x, y):
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

    def is_shape_within_grid(self, grid, shape, x, y):
        shape_rows = len(shape)
        shape_cols = len(shape[0])
        grid_rows = len(grid)
        grid_cols = len(grid[0])
        
        # Check if the shape will fit within the grid at the specified (x, y) position
        if x + shape_cols <= grid_cols and y + shape_rows <= grid_rows:
            return True
        else:
            return False

    def find_edge_touching_pieces(self, grid, shape, shape_x, shape_y, grid_x, grid_y):
        shape_height, shape_width = len(shape), len(shape[0])
        adjacent_offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    grid_i, grid_j = grid_y + i - shape_y, grid_x + j - shape_x
                    for dx, dy in adjacent_offsets:
                        adj_x, adj_y = grid_j + dx, grid_i + dy
                        if self.is_within_grid(adj_x, adj_y):
                            if grid[adj_y][adj_x] != 0:
                                return True
                                
        return False
           
    def is_move_valid(self, grid, shape, shape_x, shape_y, grid_x, grid_y):

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

    def place_shape_on_grid(self, grid, shape, shape_x, shape_y, grid_x, grid_y):
        shape_height, shape_width = len(shape), len(shape[0])
        
        # Place the shape on the grid
        for i in range(shape_height):
            for j in range(shape_width):
                if shape[i][j]:
                    grid[grid_y + i - shape_y][grid_x + j - shape_x] = shape[i][j]
                    
        return True

    def place_piece_on_all_corners_debug(self, grid, available_corners, piece):
        move_index = 0
        possible_placements = []
        no_rotation, no_mirror, semi_symmetric = self.get_symmetry_flags(piece.shape)    
        for grid_corner in available_corners:
            for orientation, mirror in product(range(4), [False, True]):
                piece.orientation = orientation
                piece.mirror = mirror
                transformed_shape = piece.transform()
                piece_corners = self.identify_shape_corners(transformed_shape, 1)
                if (no_rotation and orientation > 0) or (no_mirror and mirror) or (semi_symmetric and orientation >= 2 and not mirror):
                    continue
                for piece_corner_idx, piece_corner in enumerate(piece_corners):
                    edge_touching = self.find_edge_touching_pieces(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[1], grid_corner[0])
                    move_valid = not edge_touching and self.is_move_valid(grid, transformed_shape, piece_corner[0], piece_corner[1], grid_corner[1], grid_corner[0])
                    if move_valid:
                        move_index += 1
                        print(move_index)
                        placement_info = {
                            'piece_corner_idx': piece_corner_idx,
                            'orientation': orientation,
                            'mirror': mirror,
                            'Grid pos': grid_corner,
                            'Piece pos': piece_corner,
                        }
                        possible_placements.append(placement_info)
        return possible_placements


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


# Initialize board
game_board = Board(GRID_SIZE, CELL_SIZE)

shapes = game_board.load_piece_data_from_file("blokus_duo_tiles.txt")

piece_cache = {}
for shape_id, shape in enumerate(shapes):
    piece = Piece(shape, shape_id, 1)
    info = piece.precompute_transforms_and_corners()
    piece_cache[shape_id] = info[shape_id]

for player in range(1, 3):
    piece_id_counter = 0
    for shape in shapes:
        game_board.available_pieces[player].append(Piece(shape, piece_id_counter, player))
        piece_id_counter += 1
# Initialize self.screen

pygame.display.set_caption('blokus duo Game')


new_piece = None


move_is_valid = False
def main():
    clock = pygame.time.Clock()
    selected_piece = game_board.get_selected_piece()

    while True:
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
                            game_board.place_piece(selected_piece, grid_x, grid_y)
                            game_board.uncompressed_grid = game_board.bit_grid.decompress_grid_x_bits()
                            game_board.switch_player()

                            selected_piece = None
                    else:
                        selected_piece = game_board.get_selected_piece()
                        selected_piece.owner = game_board.player
     

                # Right click for rotation
                elif event.button == 3:
                    if selected_piece is not None:
                        orientation = (selected_piece.orientation + 1) % 4
                        selected_piece = piece_cache[selected_piece.shape_id][orientation][selected_piece.mirror]['transformed_piece']
                        selected_piece.owner = game_board.player


                # Middle click for mirror
                elif event.button == 2:
                    if selected_piece is not None:
                        mirror = not selected_piece.mirror
                        selected_piece = piece_cache[selected_piece.shape_id][selected_piece.orientation][mirror]['transformed_piece']
                        selected_piece.owner = game_board.player

                # Mouse wheel scroll
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        selected_piece = game_board.select_next_available_piece(1)                       
                    elif event.button == 5:  # Scroll down
                        selected_piece = game_board.select_next_available_piece(-1)
                    selected_piece.orientation = 0
                    selected_piece.mirror = False
                                                                                
   
        game_board.screen.fill(BLACK)
        game_board.draw_grid()
        game_board.draw_board()

        if selected_piece is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // CELL_SIZE , mouse_y // CELL_SIZE
            overlapping = game_board.is_overlapping(selected_piece, grid_x, grid_y)
            corner_touching = game_board.find_corner_touching_pieces(selected_piece, grid_y, grid_x)
            edge_touching = game_board.find_edge_touching_pieces(game_board.uncompressed_grid, selected_piece.shape, 0,0,grid_x, grid_y)
            touching = not edge_touching and corner_touching
            is_within = game_board.is_shape_within_grid(game_board.uncompressed_grid, selected_piece.shape, grid_x, grid_y)
            move_is_valid = touching and is_within and not overlapping
            border_color = (255,0,0) if not move_is_valid else (0,255,0) 
            if move_is_valid or len(game_board.placed_pieces[game_board.player]) == 0:
                move_is_valid = True
                color = (0,255,0)
                border_color = (0,255,0)
            if game_board.is_overlapping(selected_piece, grid_x, grid_y):
                color = (100,0,0) 
            else:
                color = (100,100,100) if game_board.player == 2 else (200,200,200)

            game_board.draw_piece(selected_piece, grid_x, grid_y, color)
            game_board.draw_piece_perimeter(selected_piece, grid_x, grid_y, border_color)
            game_board.highlight_available_corners(selected_piece, grid_x, grid_y)

        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()