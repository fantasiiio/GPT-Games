import os
import re

def extract_imports(file_content):
    # Extract import lines
    import_lines = re.findall(r'^\s*(from .+? import .+?|import .+?)$', file_content, re.MULTILINE)
    return import_lines, re.sub(r'^\s*(from .+? import .+?|import .+?)\n', '', file_content, flags=re.MULTILINE)

def combine_files(directory, output_filename="combined.py"):
    all_imports = set()
    all_content = ""

    # Iterating over each file in the directory
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Only process .py files (exclude the output file if it already exists)
        if filepath.endswith(".py") and filepath != os.path.join(directory, output_filename):
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()

                # Extracting imports and cleaned content
                imports, cleaned_content = extract_imports(content)
                all_imports.update(imports)
                all_content += f"# Content from {filename}\n{cleaned_content}\n\n"

    # Writing to the output file
    with open(os.path.join(directory, output_filename), 'w', encoding='utf-8') as output_file:
        # Writing unique imports to the top of the file
        for imp in sorted(all_imports):
            output_file.write(imp + "\n")
        
        # Writing combined content
        output_file.write("\n" + all_content)

if __name__ == "__main__":
    folder_path = input("Enter the path of the folder containing the python files: ")
    combine_files(folder_path)
    print("Files combined successfully!")
