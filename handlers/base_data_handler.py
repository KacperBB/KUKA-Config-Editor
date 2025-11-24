import re

def update_base_data(source_content, target_content, log_callback, purge_mode=False):
    """
    Update or purge BASE_DATA values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        purge_mode (bool): If True, set all values to 0.0.
    """
    log_callback("Processing BASE_DATA...", level="INFO")

    if purge_mode:
        # Purge mode: Set all BASE_DATA values to 0.0
        for i, line in enumerate(target_content):
            match = re.match(r'BASE_DATA\[(\d+)\]=\{(.*)\}', line)
            if match:
                index = int(match.group(1))
                target_content[i] = f"BASE_DATA[{index}]={{X 0.0, Y 0.0, Z 0.0, A 0.0, B 0.0, C 0.0}}\n"
                log_callback(f"Purged BASE_DATA[{index}] to 0.0.", level="INFO")
        return True

    # Normal update mode: Parse source_content and update target_content
    source_data = {}
    for line in source_content:
        match = re.match(r'BASE_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            values = match.group(2).split(',')
            source_data[index] = {}
            for value in values:
                value = value.strip()
                if re.match(r'[XYZABC] [\-\d.]+', value):  # Match values like "X 335.22"
                    key, val = value.split(' ', 1)
                    source_data[index][key.strip()] = val.strip()
                else:
                    log_callback(f"Skipping invalid value: {value}", level="WARNING")

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    changes_made = False
    for i, line in enumerate(target_content):
        match = re.match(r'BASE_DATA\[(\d+)\]=\{(.*)\}', line)
        if match:
            index = int(match.group(1))
            if index in source_data:
                # Update the target values with the source values
                target_values = {k: "0.0" for k in source_data[index]}  # Default to 0.0
                for key in source_data[index]:
                    target_values[key] = source_data[index][key]

                # Reconstruct the line with updated values
                updated_values = ', '.join([f"{k} {v}" for k, v in target_values.items()])
                target_content[i] = f"BASE_DATA[{index}]={{ {updated_values} }}\n"
                log_callback(f"Updated BASE_DATA[{index}] with values from source file.", level="INFO", bold=True)
                changes_made = True

    return changes_made