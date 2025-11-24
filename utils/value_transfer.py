import sys
import os
from shutil import copyfile
from datetime import datetime
import re
from handlers.base_data_handler import update_base_data
from handlers.base_name_handler import update_base_name
from handlers.base_type_handler import update_base_type  # Correct import
from handlers.tool_data_handler import update_tool_data
from handlers.tool_type_handler import update_tool_type
from handlers.tool_name_handler import update_tool_name
from handlers.load_data_handler import update_load_data
from handlers.e6axis_handler import update_e6axis


def transfer_values(
    source_file,
    target_file,
    log_callback,
    update_base_data_flag=True,
    update_base_name_flag=True,
    update_base_type_flag=True,
    update_tool_data_flag=True,
    update_tool_type_flag=True,
    update_tool_name_flag=True,
    update_load_data_flag=True,
    update_e6axis_flag=True,
    e6axis_names=["HOME"],  # New parameter for E6AXIS names
):
    try:
        log_callback("Starting value transfer...", level="INFO")

        # Read the source file
        with open(source_file, 'r') as src:
            source_content = src.readlines()
        log_callback(f"Source file content loaded successfully. Lines: {len(source_content)}", level="INFO")

        # Read the target file
        with open(target_file, 'r') as tgt:
            target_content = tgt.readlines()
        log_callback(f"Target file content loaded successfully. Lines: {len(target_content)}", level="INFO")

        # Check if target_content is empty
        if not target_content:
            log_callback("Warning: Target file is empty. No updates will be made.", level="WARNING")
            return

        # Update BASE, TOOL, LOAD, and E6AXIS data if the flags are enabled
        changes_made = False
        if update_base_data_flag:
            changes_made |= update_base_data(source_content, target_content, log_callback)
        if update_base_name_flag:
            changes_made |= update_base_name(source_content, target_content, log_callback)
        if update_base_type_flag:
            changes_made |= update_base_type(source_content, target_content, log_callback)  # Correct function call
        if update_tool_data_flag:
            changes_made |= update_tool_data(source_content, target_content, log_callback)
        if update_tool_type_flag:
            changes_made |= update_tool_type(source_content, target_content, log_callback)
        if update_tool_name_flag:
            changes_made |= update_tool_name(source_content, target_content, log_callback)
        if update_load_data_flag:
            changes_made |= update_load_data(source_content, target_content, log_callback)
        if update_e6axis_flag:
            # Pobierz nazwę wpisaną w GUI (np. HOME)
            base_source = e6axis_names[0].strip()
            # Bazowa nazwa targetu – tutaj zakładamy XHOME
            base_target = "XHOME"

            log_callback(f"Processing E6AXIS with source prefix: {base_source} -> target prefix: {base_target}", level="INFO")

            # Stwórz początkowe mapowanie: XHOME -> HOME
            name_mapping = {base_target: "HOME"}

            # Automatycznie utwórz mapowania indeksowane
            # Najpierw wyciągnij wszystkie pasujące klucze ze źródła
            indexed_keys = []
            for line in source_content:
                m = re.match(r'\s*E6AXIS\s+([A-Za-z0-9_]+)\s*=', line)
                if m:
                    key = m.group(1)
                    if key.startswith(base_source):
                        indexed_keys.append(key)

            # Posortuj, żeby kolejność była poprawna
            indexed_keys.sort()

            for key in indexed_keys:
                # Wyciągamy numer z końca (np. HOME3 -> "3")
                idx = key[len(base_source):]
                # Tworzymy target key, np. XHOME3
                target_key = f"{base_target}{idx}"
                name_mapping[target_key] = key

            log_callback(f"Generated name_mapping: {name_mapping}", level="DEBUG")

            updated_keys = update_e6axis(source_content, target_content, log_callback, name_mapping=name_mapping)
            log_callback(f"Updated E6AXIS keys: {updated_keys}", level="INFO")

            if updated_keys:
                changes_made = True
                log_callback(f"Successfully updated E6AXIS keys: {updated_keys}", level="INFO")
            else:
                log_callback("No E6AXIS keys were updated.", level="INFO")

        # Write the final updated content back to the target file
        if changes_made:
            with open(target_file, 'w') as tgt:
                tgt.writelines(target_content)
            log_callback(f"Final updated target file saved: {target_file}", level="INFO")
        else:
            log_callback("No changes were made to the target file.", level="INFO")

        log_callback("Transfer process completed.", level="INFO")
    except Exception as e:
        log_callback(f"Error during value transfer: {e}", level="ERROR")