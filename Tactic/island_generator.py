import noise
import numpy as np
import matplotlib.pyplot as plt

def generate_island(width, height, octaves=6, persistence=0.5, lacunarity=2.0):
    world = np.zeros((height, width))
    
    for i in range(height):
        for j in range(width):
            world[i][j] = noise.pnoise2(j, 
                                        i, 
                                        octaves=octaves, 
                                        persistence=persistence, 
                                        lacunarity=lacunarity, 
                                        repeatx=1024, 
                                        repeaty=1024, 
                                        base=42)
    
    # Apply radial gradient to get island shape
    max_dist = np.linalg.norm([width//2, height//2])
    for i in range(height):
        for j in range(width):
            dist = np.linalg.norm([j - width//2, i - height//2])
            world[i][j] *= (max_dist - dist) / max_dist
    
    return world


def draw_map(island_map):
    for x in range(island_map.shape[0]):
        line = ""
        for y in range(island_map.shape[1]):
            line += f"{island_map[x][y]},"
        print(line)

width, height = 30, 30
world = generate_island(width, height)
draw_map(world)
