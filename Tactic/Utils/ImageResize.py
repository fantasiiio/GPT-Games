import os
from wand.image import Image

def convert_svg_to_png(svg_path, png_path):
    with Image(filename=svg_path) as img:
        img.format = 'png'
        img.save(filename=png_path)

def resize_image(image_path, output_path, new_width):
    if not os.path.exists(image_path):
        print(f"File {image_path} does not exist.")
        return
    with Image(filename=image_path) as img:
        aspect_ratio = img.height / img.width
        new_height = int(new_width * aspect_ratio)
        img.resize(new_width, new_height)
        img.save(filename=output_path)

def resize_images(input_folder, output_folder, new_width):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    files = os.listdir(input_folder)

    for file in files:
        if file.endswith('.svg'):
            filename_without_extension = os.path.splitext(file)[0]
            png_file_path = os.path.join(output_folder, f"{filename_without_extension}.png")
            svg_file_path = os.path.join(input_folder, file)
            convert_svg_to_png(svg_file_path, png_file_path)
            file = f"{filename_without_extension}.png"

        if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)
            resize_image(output_path, output_path, new_width)

if __name__ == "__main__":
    input_folder = "C:\\dev-fg\\GPT-Games\\Tactic\\data\\flags"
    output_folder = "C:\\dev-fg\\GPT-Games\\Tactic\\data\\flags\\small"
    new_width = 50  # Change this to your desired width

    resize_images(input_folder, output_folder, new_width)
