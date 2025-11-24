def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def write_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(lines)

def find_value_definition(lines, definition):
    for line in lines:
        if definition in line:
            return line.strip()
    return None

def replace_value(lines, definition, new_value):
    for i, line in enumerate(lines):
        if definition in line:
            lines[i] = line.replace(find_value_definition(lines, definition), new_value)
            return True
    return False

def extract_values(value_line):
    values = value_line[value_line.index('{') + 1:value_line.index('}')].split(',')
    return [value.strip() for value in values]

def create_internal_arrays(before_values, after_values):
    before_array = {}
    after_array = {}
    
    for i, value in enumerate(before_values):
        key = value.split()[0]
        before_array[i + 1] = value
    
    for i, value in enumerate(after_values):
        key = value.split()[0]
        after_array[i + 1] = value
    
    return before_array, after_array

def display_changes(before_array, after_array):
    for key in before_array.keys():
        print(f"Changed {before_array[key]} to {after_array[key]}")