def is_between(min, number, max):
    return min[0] <= number[0] < max[0] and min[1] <= number[1] < max[1]

# Reimplement the function to identify corners in a shape based on the criteria that corners must have >= 4 adjacent empty cells
def identify_shape_block_corners(grid, player_id):
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

# Define the W shape
W_shape = [
    [1, 1, 0, 0],
    [1, 1, 1, 1],
    [0, 0, 1, 0],
]


# Use the new function to identify corners in the W shape
print(identify_shape_block_corners(W_shape, 1))