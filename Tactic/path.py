from collections import deque

def find_path(grid):
    rows, cols = len(grid), len(grid[0])
    
    # Helper function to check if a given cell is within grid boundaries and is accessible
    def is_valid(x, y, visited):
        return 0 <= x < rows and 0 <= y < cols and grid[x][y] != 'X' and (x, y) not in visited
    
    # Initialize starting and ending points
    start = end = None
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 'S':
                start = (i, j)
            elif grid[i][j] == 'E':
                end = (i, j)
    
    if start is None or end is None:
        return []
    
    visited = set()  # Set to keep track of visited cells
    queue = deque([(start, [start])])  # Queue for BFS. Each element is a tuple containing current cell coordinates and the path taken to reach there.
    
    while queue:
        (cur_x, cur_y), path = queue.popleft()
        
        # If we've reached the end, return the path
        if (cur_x, cur_y) == end:
            return path
        
        # Mark the current cell as visited
        visited.add((cur_x, cur_y))
        
        # Visit all valid neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x, new_y = cur_x + dx, cur_y + dy
            
            if is_valid(new_x, new_y, visited):
                queue.append(((new_x, new_y), path + [(new_x, new_y)]))
                visited.add((new_x, new_y))
                
    return []

def draw_grid(grid):
    """
    Visualize a 2D grid.

    Args:
        grid (list of lists): The 2D grid to be visualized.

    Returns:
        None
    """
    for row in grid:
        print(" ".join(map(str, row)))

# Example usage
grid = [
    ['S', 'O', 'O', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'O'],
    ['O', 'O', 'O', 'O', 'E']
]

result = find_path(grid)
for x, y in result:
    grid[x][y] = '*'
draw_grid(grid)
if isinstance(result, list):
    print("Path found:", result)
else:
    print(result)
