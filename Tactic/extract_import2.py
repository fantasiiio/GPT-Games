# from stdlib_list import stdlib_list

# libraries = stdlib_list("3.11")


# def load_imports_from_file(filename):
#     with open(filename, 'r', encoding='utf-8') as file:
#         imports = [line.strip() for line in file if line.strip()]  # Read non-empty lines
#     return imports

# # Usage
# file_path = 'imports_list.txt'  # Replace with your file's path if different
# extracted_imports = load_imports_from_file(file_path)


# external_imports = [imp for imp in extracted_imports if imp not in libraries]
# print(external_imports)

# # Write to a file with an additional line break after each import
# with open('imports_list2.txt', 'w', encoding='utf-8') as file:
#     for imp in external_imports:
#         file.write(imp + '\n\n')

import os

def load_imports_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        imports = [line.strip() for line in file if line.strip()]  # Read non-empty lines
    return imports

def filter_out_filenames(imports_list, directory='.'):
    # Extract filenames without extensions from the directory
    filenames = [os.path.splitext(file)[0] for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file)) and file.endswith('.py')]
    
    # Filter out any import that matches a filename
    filtered_imports = [imp for imp in imports_list if imp not in filenames]
    
    return filtered_imports

# Load imports from file
file_path = 'imports_list2.txt'
extracted_imports = load_imports_from_file(file_path)

# Filter out filenames from the list of imports
filtered_imports = filter_out_filenames(extracted_imports)

print(filtered_imports)
# Write to a file with an additional line break after each import
with open('imports_list2.txt', 'w', encoding='utf-8') as file:
    for imp in filtered_imports:
        file.write(imp + '\n')
