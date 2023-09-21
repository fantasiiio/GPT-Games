import os
import glob

def rename_files_in_folder(folder_path, index, prefix="Explosion"):
    # List all files in the folder
    file_paths = glob.glob(os.path.join(folder_path, '*'))
    
    # Sort the file paths alphabetically
    file_paths.sort()
    
    # Initialize a counter for numbering files
    counter = 1
    
    for file_path in file_paths:
        # Generate the new name for the file
        new_name = f"{prefix}_{index}_{str(counter).zfill(2)}.png"
        
        # Generate the full path for the new name
        new_path = os.path.join(folder_path, new_name)
        
        # Rename the file
        os.rename(file_path, new_path)
        
        # Increment the counter
        counter += 1

# Folder path where the files are located
#folder_path = "C:\\dev-fg\\GPT-Games\\Tactic\\assets\\images\\Effects\\Explosion"

# Call the function
#C:\dev-fg\GPT-Games\Tactic\assets\images\Effects
for i in range(1, 16):
    folder_path = f"C:\\dev-fg\\GPT-Games\\Tactic\\assets\\images\\Effects\\{i}"
    rename_files_in_folder(folder_path, i)
