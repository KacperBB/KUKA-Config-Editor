import os
import threading
from value_transfer import transfer_values
from utils.logger import log_info, log_error
from utils.file_utils import prepare_target_file


def run_transfer(
    source_file, target_file, update_base_data_flag, update_base_name_flag, update_base_type_flag,
    update_tool_data_flag, update_tool_type_flag, update_tool_name_flag, update_load_data_flag,
    update_e6axis_flag, e6axis_names, modify_directly, log_message
):
    """
    Wykonuje transfer danych między plikami.
    """
    try:
        log_message("Starting transfer...", level="INFO")
        log_info("Transfer thread started.")

        # Przygotowanie pliku docelowego
        new_target_file = prepare_target_file(target_file, modify_directly, log_message)
        if not new_target_file:
            return  # Wyjdź, jeśli wystąpił błąd podczas przygotowania pliku

        # Wywołanie funkcji transfer_values z odpowiednimi parametrami
        transfer_values(
            source_file, new_target_file, log_message,
            update_base_data_flag, update_base_name_flag, update_base_type_flag,
            update_tool_data_flag, update_tool_type_flag, update_tool_name_flag,
            update_load_data_flag, update_e6axis_flag, e6axis_names
        )

        log_message("Transfer completed successfully!", level="INFO")

        # Otwórz nowo utworzony plik, jeśli zaznaczono odpowiednią opcję
        if not modify_directly:
            os.startfile(new_target_file)

    except Exception as e:
        log_message(f"Error during transfer: {e}", level="ERROR")


def start_transfer_in_thread(
    source_file, target_file, update_base_data_flag, update_base_name_flag, update_base_type_flag,
    update_tool_data_flag, update_tool_type_flag, update_tool_name_flag, update_load_data_flag,
    update_e6axis_flag, e6axis_names, modify_directly, log_message
):
    """
    Uruchamia transfer w osobnym wątku.
    """
    threading.Thread(
        target=run_transfer,
        args=(
            source_file, target_file, update_base_data_flag, update_base_name_flag, update_base_type_flag,
            update_tool_data_flag, update_tool_type_flag, update_tool_name_flag, update_load_data_flag,
            update_e6axis_flag, e6axis_names, modify_directly, log_message
        )
    ).start()