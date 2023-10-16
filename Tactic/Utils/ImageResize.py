import os
from PIL import Image

def resize_images(input_folder, output_folder, percentage):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    files = os.listdir(input_folder)

    for file in files:
        if file.endswith(('.jpg', '.jpeg', '.png', '.gif')):
            input_path = os.path.join(input_folder, file)
            output_path = os.path.join(output_folder, file)

            # Open the image using Pillow (PIL)
            img = Image.open(input_path)

            # Calculate the new size based on the percentage
            width, height = img.size
            new_width = int(width * (percentage / 100))
            new_height = int(height * (percentage / 100))

            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.ANTIALIAS)

            # Save the resized image to the output folder
            resized_img.save(output_path)

if __name__ == "__main__":
    input_folder = "C:\\dev-fg\\GPT-Games\\Tactic\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Icons"
    output_folder = "C:\\dev-fg\\GPT-Games\\Tactic\\assets\\UI-v2\\Buttons\\Framed\\Square\\Green\\Icons"
    resize_percentage = 50  # Change this to your desired percentage

    resize_images(input_folder, output_folder, resize_percentage)
