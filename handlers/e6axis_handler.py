import re

def update_e6axis(source_content, target_content, log_callback, name_mapping={"HOME": "XHOME"}, purge_mode=False):
    """
    Update or purge E6AXIS values in the target content.

    Args:
        source_content (list): The source file content.
        target_content (list): The target file content to be updated.
        log_callback (function): Function to log messages.
        name_mapping (dict): Mapping of source names to target names (e.g., {"HOME": "XHOME"}).
        purge_mode (bool): If True, set all values to 0.0.

    Returns:
        dict: A dictionary of updated keys and their new values.
    """
    log_callback("Processing E6AXIS...", level="INFO")

    if purge_mode:
        # Purge mode: Set all E6AXIS values to 0.0
        for i, line in enumerate(target_content):
            match = re.match(r'E6AXIS\s+(\w+)=\{(.*)\}', line)
            if match:
                target_key = match.group(1).strip()
                target_content[i] = f"E6AXIS {target_key}={{ A1 0.0, A2 0.0, A3 0.0, A4 0.0, A5 0.0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0 }}\n"
                log_callback(f"Purged E6AXIS {target_key} to 0.0.", level="INFO")
        return {}

    # Parse source content to extract E6AXIS data
    source_data = {}
    for line in source_content:
        match = re.match(r'E6AXIS\s+(\w+)=\{(.*)\}', line)
        if match:
            key = match.group(1).strip()
            values = match.group(2).strip()
            args = {arg.split()[0]: arg.split()[1] for arg in values.split(",")}
            source_data[key] = args

    log_callback(f"Parsed source_data: {source_data}", level="INFO")

    # Validate and map all keys in name_mapping to source_data
    updated_keys = {}
    for source_key in list(name_mapping.keys()):
        if source_key not in source_data:
            # Check for indexed names (e.g., xFFT_HOME1, xFFT_HOME2)
            indexed_keys = [key for key in source_data.keys() if key.startswith(source_key)]
            if not indexed_keys:
                log_callback(f"Error: Source key '{source_key}' not found in source file.", level="ERROR")
                continue
            else:
                log_callback(f"Found indexed keys for '{source_key}': {indexed_keys}", level="INFO")
                for idx, indexed_key in enumerate(indexed_keys, start=1):
                    name_mapping[f"{source_key}{idx}"] = indexed_key

    # Update target content
    changes_made = False
    for i, line in enumerate(target_content):
        match = re.search(r'E6AXIS\s+([A-Za-z0-9_]+)\s*=\s*\{(.*)\}', line)
        if match:
            target_key = match.group(1).strip()
            source_key = name_mapping.get(target_key, target_key)

            if source_key in source_data:
                # Update the target values with the source values
                target_values = {arg.split()[0]: arg.split()[1] for arg in match.group(2).split(",")}
                for key, value in source_data[source_key].items():
                    target_values[key] = value
                updated_values = ", ".join([f"{k} {v}" for k, v in target_values.items()])
                target_content[i] = f"E6AXIS {target_key}={{ {updated_values} }}\n"
                log_callback(f"Updated E6AXIS {target_key} with values from source key {source_key}.", level="INFO")
                updated_keys[target_key] = target_values
                changes_made = True

    return updated_keys