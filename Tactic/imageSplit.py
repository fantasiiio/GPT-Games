from PIL import Image
import os

def split_image(image_path, grid_subdivision, output_directory):
    """
    Split an image into smaller images based on a grid subdivision.

    :param image_path: Path to the source image.
    :param grid_subdivision: Tuple indicating grid subdivision, e.g., (5, 5).
    :param output_directory: Directory to save the split images.
    """
    # Open the image
    img = Image.open(image_path)
    
    # Calculate the width and height of each subdivision
    width, height = img.size
    step_x = width // grid_subdivision[0]
    step_y = height // grid_subdivision[1]

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Split the image and save the small images
    for i in range(grid_subdivision[0]):
        for j in range(grid_subdivision[1]):
            left = i * step_x
            upper = j * step_y
            right = left + step_x
            lower = upper + step_y
            small_img = img.crop((left, upper, right, lower))
            
            # Create a filename for each small image
            output_path = os.path.join(output_directory, f"split_{i}_{j}.png")
            small_img.save(output_path)
            print(f"Saved: {output_path}")

# Example Usage
image_path = "C:\\Users\Ryzen\Downloads\\tds-modern-pixel-game-kit\\tds-modern-tilesets-environment\\PNG\\Tiles\\_0002_SandTiles.png"
output_directory = "."
grid_subdivision = (5, 5)

split_image(image_path, grid_subdivision, output_directory)
