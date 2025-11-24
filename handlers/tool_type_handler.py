import re

def update_tool_type(source_content, target_content, log_callback, purge_mode=False):
    """
    Update or purge TOOL_TYPE values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        purge_mode (bool): If True, set all values to #NONE.
    """
    log_callback("Processing TOOL_TYPE...", level="INFO")

    if purge_mode:
        # Purge mode: Set all TOOL_TYPE values to #NONE
        for i, line in enumerate(target_content):
            match = re.match(r'TOOL_TYPE\[(\d+)\]=#(\w+)', line)
            if match:
                index = int(match.group(1))
                target_content[i] = f"TOOL_TYPE[{index}]=#NONE\n"
                log_callback(f"Purged TOOL_TYPE[{index}] to #NONE.", level="INFO")
        return True

    # Normal update mode
    source_data = {}
    for line in source_content:
        match = re.match(r'TOOL_TYPE\[(\d+)\]=#(\w+)', line)
        if match:
            index = int(match.group(1))
            value = f"#{match.group(2).strip()}"
            source_data[index] = value

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    changes_made = False
    for i, line in enumerate(target_content):
        match = re.match(r'TOOL_TYPE\[(\d+)\]=#(\w+)', line)
        if match:
            index = int(match.group(1))
            if index in source_data:
                # Update the TOOL_TYPE value
                new_value = source_data[index]
                target_content[i] = f"TOOL_TYPE[{index}]={new_value}\n"
                log_callback(f"Updated TOOL_TYPE[{index}] to {new_value}.", level="INFO", bold=True)
                changes_made = True

    return changes_made