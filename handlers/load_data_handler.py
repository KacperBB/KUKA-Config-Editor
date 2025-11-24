import re

def update_load_data(source_content, target_content, log_callback, purge_mode=False):
    """
    Update or purge LOAD_DATA values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        purge_mode (bool): If True, set all values to default.
    """
    log_callback("Processing LOAD_DATA...", level="INFO")

    # Domyślna struktura LOAD_DATA
    default_load_data = "M -1.00000,CM {X 0.0,Y 0.0,Z 0.0,A 0.0,B 0.0,C 0.0},J {X 0.0,Y 0.0,Z 0.0}"

    if purge_mode:
        # Purge mode: Set all LOAD_DATA values to default
        for i, line in enumerate(target_content):
            match = re.match(r'LOAD_DATA\[(\d+)\]=\{(.*)\}', line)
            if match:
                index = int(match.group(1))
                target_content[i] = f"LOAD_DATA[{index}]={{ {default_load_data} }}\n"
                log_callback(f"Purged LOAD_DATA[{index}] to default values.", level="INFO")
        return True

    # Normal update mode
    source_data = {}
    for line in source_content:
        match = re.match(r'LOAD_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            values = match.group(2).strip()
            source_data[index] = values

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    changes_made = False
    for i, line in enumerate(target_content):
        match = re.match(r'LOAD_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            if index in source_data:
                # Update the LOAD_DATA values
                updated_line = f"LOAD_DATA[{index}]={{ {source_data[index]} }}\n"
                target_content[i] = updated_line
                log_callback(f"Updated LOAD_DATA[{index}] with values from source file.", level="INFO")
                changes_made = True

    return changes_made