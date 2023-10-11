from PIL import Image
import os
import math

def resize_to_nearest_64(folder_path, tile_path):
    # Get list of all files in the provided directory
    files = os.listdir(folder_path)
    
    # Load the 64x64 tile
    tile_image = Image.open(tile_path)

    for file in files:
        file_path = os.path.join(folder_path, file)
        
        # Check if it's an image file
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path).convert('RGBA')
            width, height = img.size
            
            # Calculate new dimensions (rounded up to the nearest multiple of 64)
            new_width = math.ceil(width/64) * 64
            new_height = math.ceil(height/64) * 64
            
            # Create a blank image filled with the tile
            blank_img = Image.new('RGBA', (new_width, new_height))
            for x in range(0, new_width, 64):
                for y in range(0, new_height, 64):
                    blank_img.paste(tile_image, (x, y))

            # Paste the original image onto the center of the blank image
            offset = ((new_width - width) // 2, (new_height - height) // 2)
            blank_img.paste(img, offset, img)  # The last parameter is the alpha mask for transparency
            
            # Save the combined image
            blank_img.save(file_path)

# Specify your directory path here
directory_path = f"{base_path}\\assets\\maps\\Riverwood Assets"
tile_path = "C:\\dev-fg\\GPT-Games\\Tactic\\assets\\maps\\water (13).png"
resize_to_nearest_64(directory_path, tile_path)
