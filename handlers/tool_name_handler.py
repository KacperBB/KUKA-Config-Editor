import re

def update_tool_name(source_content, target_content, log_callback, purge_mode=False):
    """
    Update or purge TOOL_NAME values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        purge_mode (bool): If True, set all values to empty strings.
    """
    log_callback("Processing TOOL_NAME...", level="INFO")

    if purge_mode:
        # Purge mode: Set all TOOL_NAME values to empty strings
        for i, line in enumerate(target_content):
            match = re.match(r'TOOL_NAME\[(\d+),\]=["](.*)["]', line)
            if match:
                index = int(match.group(1))
                target_content[i] = f'TOOL_NAME[{index},]=" "\n'
                log_callback(f"Purged TOOL_NAME[{index}] to an empty string.", level="INFO")
        return True

    # Normal update mode
    source_data = {}
    for line in source_content:
        match = re.match(r'TOOL_NAME\[(\d+),\]=["](.*)["]', line)
        if match:
            index = int(match.group(1))
            value = match.group(2).strip()
            source_data[index] = value

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    changes_made = False
    for i, line in enumerate(target_content):
        match = re.match(r'TOOL_NAME\[(\d+),\]=["](.*)["]', line)
        if match:
            index = int(match.group(1))
            if index in source_data:
                # Update the TOOL_NAME value
                new_value = source_data[index]
                target_content[i] = f'TOOL_NAME[{index},]="{new_value}"\n'
                log_callback(f"Updated TOOL_NAME[{index}] to \"{new_value}\".", level="INFO", bold=True)
                changes_made = True

    return changes_made