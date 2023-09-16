import os
from PIL import Image

def read_grid_from_file(filename):
    grid = []
    with open(filename, 'r') as f:
        for line in f:
            grid.append([int(num) for num in line.strip().split()])
    return grid

def load_tile_image(folder, base_filename, tile_number):
    if tile_number == 0:
        return None
    image_filename = f"{folder}/{base_filename} ({tile_number}).png"
    return Image.open(image_filename)


def stitch_images(folder, base_filename, grid):
    tile_width, tile_height = load_tile_image(folder, base_filename, 1).size
    merged_width = tile_width * len(grid[0])
    merged_height = tile_height * len(grid)
    
    merged_image = Image.new('RGB', (merged_width, merged_height))

    for row_idx, row in enumerate(grid):
        for col_idx, tile_number in enumerate(row):
            tile = load_tile_image(folder, base_filename, tile_number)
            if tile:
                merged_image.paste(tile, (col_idx * tile_width, row_idx * tile_height))

    return merged_image


def save_merged_image(image, output_filename):
    image.save(output_filename)

def main():
    print(os.getcwd() )
    # Step 1: Read the grid from a file
    grid_filename = "assets\\maps\\tilesNumbers.txt"
    grid = read_grid_from_file(grid_filename)

    # Step 2: Stitch the images based on the grid
    tiles_folder = "C:\\Users\\Ryzen\\Downloads\\graphicriver-gCwi2QXV-topdown-game-tileset-1\\png\\separate\\64x64\\water"
    base_filename = "water"  # e.g., "water"
    merged_img = stitch_images(tiles_folder, base_filename, grid)

    # Step 3: Save the merged image
    output_filename = "assets\\maps\\water.png"
    save_merged_image(merged_img, output_filename)
    print(f"Merged image saved as {output_filename}!")

if __name__ == "__main__":
    main()
