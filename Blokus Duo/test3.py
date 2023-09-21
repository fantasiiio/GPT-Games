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

def print_grid_with_piece(grid, shape, row_from = 0, col_from = 0):
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
            # if cell != 0:
                row_str += f"{cell} "
        print(row_str)

# Example usage:
grid = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
]

shape = [
    [0, 1, 1],
    [0, 1, 0],
    [1, 1, 0]
]

shape_x, shape_y = 0, 0  # The corner (x, y) of the shape
piece = Piece(shape, 1, 1, orientation= 1)
transformed_shape = piece.transform()
grid_x, grid_y = 3,2    # The position (x, y) on the grid where you want to place the shape's corner

result = place_shape_on_grid(grid, transformed_shape, shape_x, shape_y, grid_x, grid_y)
print_grid(grid)
