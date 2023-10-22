import ast
import os

def extract(file_path):
    imports_list = []
    
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read())
            
            for node in ast.walk(tree):
                # Handle 'import x' style imports
                if isinstance(node, ast.Import):
                    for n in node.names:
                        imports_list.append(n.name.split('.')[0])
                
                # Handle 'from x import y' style imports
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module  # This captures the 'x' in 'from x import y'
                    imports_list.append(module_name.split('.')[0])
        except:
            pass
    return imports_list

def get_all_python_files_in_directory(directory='.'):
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                yield os.path.join(dirpath, filename)

all_imports = []
for python_file in get_all_python_files_in_directory():
    if python_file == "extract_imports.py":
        continue
    all_imports.extend(extract(python_file))

# Remove duplicates and sort
sorted_unique_imports = sorted(list(set(all_imports)))

# Write to a file with an additional line break after each import
with open('imports_list.txt', 'w', encoding='utf-8') as file:
    for imp in sorted_unique_imports:
        file.write(imp + '\n\n')

print(sorted_unique_imports)
