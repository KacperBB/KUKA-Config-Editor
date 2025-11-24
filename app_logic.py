import re
from tkinter import filedialog
from utils.logger import log_info, log_error
#System do dopracowania

class AppLogic:
    def __init__(self, ui):
        self.ui = ui

    def select_source_file(self):
        file_path = filedialog.askopenfilename(title="Select Source File")
        if file_path:
            self.ui.source_entry.delete(0, "end")
            self.ui.source_entry.insert(0, file_path)
            self.compare_robot_models()

    def select_target_file(self):
        file_path = filedialog.askopenfilename(title="Select Target File")
        if file_path:
            self.ui.target_entry.delete(0, "end")
            self.ui.target_entry.insert(0, file_path)
            self.compare_robot_models()

    def compare_robot_models(self):
        source_file = self.ui.source_entry.get()
        target_file = self.ui.target_entry.get()

        if not source_file or not target_file:
            return

        try:
            with open(source_file, 'r') as src:
                source_content = src.read()
            source_match = re.search(r'KR\s*\d+', source_content)
            source_model = source_match.group(0).replace(" ", "") if source_match else None

            with open(target_file, 'r') as tgt:
                target_content = tgt.read()
            target_match = re.search(r'MACHINE_DEF\[\d+\]=\{NAME\[\]\s*"KR\s*\d+', target_content)
            target_model = target_match.group(0).split('"')[1].replace(" ", "") if target_match else None

            self.ui.log_display.config(state="normal")
            if source_model == target_model:
                self.ui.log_display.insert("end", f"Models match: {source_model}\n")
            else:
                self.ui.log_display.insert("end", f"Models do not match: {source_model} vs {target_model}\n")
            self.ui.log_display.config(state="disabled")
        except Exception as e:
            log_error(f"Error comparing models: {e}")