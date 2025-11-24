import re

def update_tool_data(source_content, target_content, log_callback, purge_mode=False):
    """
    Update or purge TOOL_DATA values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        purge_mode (bool): If True, set all values to 0.0.
    """
    log_callback("Processing TOOL_DATA...", level="INFO")

    if purge_mode:
        # Purge mode: Set all TOOL_DATA values to 0.0
        for i, line in enumerate(target_content):
            match = re.match(r'TOOL_DATA\[(\d+)\]=\{(.*)\}', line)
            if match:
                index = int(match.group(1))
                target_content[i] = f"TOOL_DATA[{index}]={{X 0.0, Y 0.0, Z 0.0, A 0.0, B 0.0, C 0.0}}\n"
                log_callback(f"Purged TOOL_DATA[{index}] to 0.0.", level="INFO")
        return True

    # Normal update mode
    source_data = {}
    for line in source_content:
        match = re.match(r'TOOL_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            values = match.group(2).split(',')
            source_data[index] = {}
            for value in values:
                value = value.strip()
                if re.match(r'[XYZABC] [\-\d.]+', value):  # Match values like "X 516.36"
                    key, val = value.split(' ', 1)
                    source_data[index][key.strip()] = val.strip()
                else:
                    log_callback(f"Skipping invalid value: {value}", level="WARNING")

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    changes_made = False
    for i, line in enumerate(target_content):
        match = re.match(r'TOOL_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            if index in source_data:
                # Parse the existing values in the target file
                target_values = {}
                values = match.group(2).split(',')
                for value in values:
                    value = value.strip()
                    if ' ' in value:
                        key, val = value.split(' ', 1)
                        target_values[key.strip()] = val.strip()

                # Update the target values with the source values
                for key in source_data[index]:
                    target_values[key] = source_data[index][key]

                # Reconstruct the line with updated values
                updated_values = ', '.join([f"{k} {v}" for k, v in target_values.items()])
                target_content[i] = f"TOOL_DATA[{index}]={{ {updated_values} }}\n"
                log_callback(f"Updated TOOL_DATA[{index}] with values from source file.", level="INFO", bold=True)
                changes_made = True

    return changes_made