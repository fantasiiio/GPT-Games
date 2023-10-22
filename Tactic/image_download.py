import os
import requests
from tqdm import tqdm
from config import *

# Define the folder where you want to save your images
folder_name = 'data\\images\\flags'

# Create folder if not exists
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


# Loop through each image data and download the image
for entry in tqdm(countries, desc="Downloading images", unit="file"):
    image_url = "https:" + entry['file_url']
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Create the full path where the image will be saved
        image_path = os.path.join(folder_name, f"{entry['name']}.svg")

        # Save the image
        with open(image_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {entry['name']}")

print("Download completed.")
