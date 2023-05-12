import os

def get_js_files(directory):
    js_files = []
    for file in os.listdir(directory):
        if file.endswith('.js'):
            js_files.append(file)
    return js_files

def extract_classes(file):
    with open(file, 'r') as f:
        contents = f.read()
        classes = contents.split('class ')
        class_codes = []
        for i in range(1, len(classes)):
            class_name = classes[i].split()[0]
            class_code = f'class {classes[i]}'
            class_codes.append(class_code)
            # Create "classes" folder if it does not exist
            if not os.path.exists('./classes'):
                os.mkdir('./classes')
            with open(f'./classes/{class_name}.js', 'w') as class_file:
                class_file.write(class_code)
    
    # Remove the extracted class code from the original files
    remaining_content = contents
    for class_code in class_codes:
        remaining_content = remaining_content.replace(class_code, '')
    
    with open(file, 'w') as f:
        f.write(remaining_content.strip())

js_files = get_js_files('./')
for file in js_files:
    extract_classes(file)
