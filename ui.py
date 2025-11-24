import os
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from background_tasks import start_transfer_in_thread
from utils.logger import setup_logger
from purge_file_view import PurgeFileView  # Import the PurgeFileView class

# Setup logger
logger = setup_logger("file_transfer.log")


class FileTransferApp:
    def __init__(self, root):
        self.root = root

        # Set the title of the program
        self.root.title("KUKA ACE (Automated Config Edit)")

        # Set a custom icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        else:
            print(f"Icon file not found: {icon_path}")

        self.root.geometry("800x600")  # Adjusted window size for layout

        # Create a Notebook widget for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Create the first tab: Copy/Paste Values
        self.copy_paste_frame = tk.Frame(self.notebook)
        self.notebook.add(self.copy_paste_frame, text="Copy/Paste Values")
        self.create_copy_paste_tab(self.copy_paste_frame)

        # Create the second tab: Purge File
        self.purge_file_frame = tk.Frame(self.notebook)
        self.notebook.add(self.purge_file_frame, text="Purge File")
        PurgeFileView(self.purge_file_frame)  # Use the PurgeFileView class

    def create_copy_paste_tab(self, parent):
        """
        Create the UI for the Copy/Paste Values tab.
        """
        # Left frame for file selection and controls
        left_frame = tk.Frame(parent)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right frame for log display
        right_frame = tk.Frame(parent)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Add animated lights in the top-right corner of the left frame
        self.lights_canvas = tk.Canvas(left_frame, width=60, height=20, bg="white", highlightthickness=0)
        self.lights_canvas.pack(anchor="ne", pady=5, padx=5)

        # Create three rectangles for the lights
        self.red_light = self.lights_canvas.create_rectangle(5, 5, 20, 20, fill="gray")
        self.orange_light = self.lights_canvas.create_rectangle(25, 5, 40, 20, fill="gray")
        self.green_light = self.lights_canvas.create_rectangle(45, 5, 60, 20, fill="gray")

        # Start the animation
        self.current_light = 0
        self.animate_lights()

        # Source file selection
        self.source_label = tk.Label(left_frame, text="Source File:")
        self.source_label.pack(pady=5)
        self.source_entry = tk.Entry(left_frame, width=50)
        self.source_entry.pack(pady=5)
        self.source_button = tk.Button(left_frame, text="Browse", command=self.select_source_file)
        self.source_button.pack(pady=5)

        # Target file selection
        self.target_label = tk.Label(left_frame, text="Target File:")
        self.target_label.pack(pady=5)
        self.target_entry = tk.Entry(left_frame, width=50)
        self.target_entry.pack(pady=5)
        self.target_button = tk.Button(left_frame, text="Browse", command=self.select_target_file)
        self.target_button.pack(pady=5)

        # Robot model comparison result
        self.robot_model_label = tk.Label(left_frame, text="Zgodność Modelu robota w plikach konfiguracyjnych:")
        self.robot_model_label.pack(pady=5)
        self.robot_model_canvas = tk.Canvas(left_frame, width=50, height=50)
        self.robot_model_canvas.pack(pady=5)

        # Display models in files
        self.models_info_label = tk.Label(left_frame, text="", justify="left", fg="blue", wraplength=300)
        self.models_info_label.pack(pady=5)

        # Checkbox for file modification behavior
        self.modify_directly = tk.BooleanVar(value=True)
        self.checkbox = tk.Checkbutton(left_frame, text="Modify target file directly", variable=self.modify_directly)
        self.checkbox.pack(pady=5)

        # Checkbox for opening file after process
        self.open_file_after_process = tk.BooleanVar(value=False)
        self.open_file_checkbox = tk.Checkbutton(left_frame, text="Open file as soon as the process finish", variable=self.open_file_after_process)
        self.open_file_checkbox.pack(pady=5)

        # Button to open advanced options
        self.advanced_options_button = tk.Button(left_frame, text="Opcje zaawansowane", command=self.open_advanced_options)
        self.advanced_options_button.pack(pady=5)

        # Start button
        self.start_button = tk.Button(left_frame, text="Start Transfer", command=self.start_transfer)
        self.start_button.pack(pady=10)

        # Progress bar
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=400, mode="determinate", variable=self.progress)
        self.progress_bar.pack(pady=10)

        # Logger display in the right frame
        self.log_display = scrolledtext.ScrolledText(right_frame, width=70, height=30, state="disabled", wrap="word")
        self.log_display.pack(fill="both", expand=True)
        
        # Initialize advanced options variables
        self.update_base_data = tk.BooleanVar(value=True)
        self.update_base_name = tk.BooleanVar(value=True)
        self.update_base_type = tk.BooleanVar(value=True)
        self.update_tool_data = tk.BooleanVar(value=True)
        self.update_tool_type = tk.BooleanVar(value=True)
        self.update_tool_name = tk.BooleanVar(value=True)
        self.update_load_data = tk.BooleanVar(value=True)
        self.update_e6axis = tk.BooleanVar(value=True)
        self.e6axis_names = tk.StringVar(value="xFFT_HOME")

        # Version and Created By labels in the same line
        footer_frame = tk.Frame(left_frame)
        footer_frame.pack(side="bottom", fill="x", pady=5)

        self.created_by_label = tk.Label(footer_frame, text="Created by Kacper Borowiec", fg="gray", anchor="w")
        self.created_by_label.pack(side="left", padx=5)

        self.version_label = tk.Label(footer_frame, text="Ver 0.2", fg="gray", anchor="e")
        self.version_label.pack(side="right", padx=5)

    def select_source_file(self):
        file_path = filedialog.askopenfilename(title="Select Source File")
        if file_path:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file_path)
            self.compare_robot_models()

    def select_target_file(self):
        file_path = filedialog.askopenfilename(title="Select Target File")
        if file_path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, file_path)
            self.compare_robot_models()

    def compare_robot_models(self):
        source_file = self.source_entry.get()
        target_file = self.target_entry.get()

        if not source_file or not target_file:
            return

        try:
            # Extract robot model from source file
            with open(source_file, 'r') as src:
                source_content = src.read()
            source_match = re.search(r'kr\s*\d+', source_content, re.IGNORECASE)  # Case-insensitive search
            source_model = source_match.group(0).replace(" ", "").upper() if source_match else None  # Convert to uppercase

            # Extract robot model from target file
            with open(target_file, 'r') as tgt:
                target_content = tgt.read()
            target_match = re.search(r'MACHINE_DEF\[\d+\]=\{NAME\[\]\s*"KR\s*\d+', target_content)
            target_model = target_match.group(0).split('"')[1].replace(" ", "").upper() if target_match else None  # Convert to uppercase

            # Compare models and update the canvas
            self.robot_model_canvas.delete("all")
            if source_model and target_model and source_model == target_model:
                self.robot_model_canvas.create_rectangle(0, 0, 50, 50, fill="green")
                self.log_message_with_color("Robot models match.", level="INFO")
            else:
                self.robot_model_canvas.create_rectangle(0, 0, 50, 50, fill="red")
                self.log_message_with_color("Robot models do not match.", level="WARNING")

            # Update models info label
            self.models_info_label.config(
                text=f"Source File Model: {source_model or 'Not Found'}\nTarget File Model: {target_model or 'Not Found'}"
            )
        except Exception as e:
            self.log_message_with_color(f"Error comparing robot models: {e}", level="ERROR")

    def open_advanced_options(self):
        """
        Open a new window for advanced options.
        """
        advanced_window = tk.Toplevel(self.root)
        advanced_window.title("Opcje zaawansowane")
        advanced_window.geometry("400x400")

        # Add checkboxes for BASE, TOOL, LOAD, and E6AXIS updates
        checkboxes = [
            ("Update BASE_DATA", self.update_base_data),
            ("Update BASE_NAME", self.update_base_name),
            ("Update BASE_TYPE", self.update_base_type),
            ("Update TOOL_DATA", self.update_tool_data),
            ("Update TOOL_TYPE", self.update_tool_type),
            ("Update TOOL_NAME", self.update_tool_name),
            ("Update LOAD_DATA", self.update_load_data),
            ("Update E6AXIS", self.update_e6axis),
        ]

        for text, var in checkboxes:
            tk.Checkbutton(advanced_window, text=text, variable=var).pack(anchor="w", pady=5)

        # Input field for E6AXIS names
        tk.Label(advanced_window, text="E6AXIS Names (comma-separated):").pack(anchor="w", pady=5)
        tk.Entry(advanced_window, textvariable=self.e6axis_names).pack(anchor="w", pady=5)

        # Add "Uncheck All" button
        def uncheck_all():
            for _, var in checkboxes:
                var.set(False)

        uncheck_button = tk.Button(advanced_window, text="Uncheck All", command=uncheck_all)
        uncheck_button.pack(pady=10)

        # Add "Wyjdź" button to close the window
        exit_button = tk.Button(advanced_window, text="Wyjdź", command=advanced_window.destroy)
        exit_button.pack(pady=10)

    def start_transfer(self):
        """
        Start the transfer process.
        """
        source_file = self.source_entry.get()
        target_file = self.target_entry.get()

        if not source_file or not target_file:
            self.log_message("Please select both source and target files.")
            return

        # Start the transfer in a separate thread
        start_transfer_in_thread(
            source_file, target_file,
            update_base_data_flag=self.update_base_data.get(),
            update_base_name_flag=self.update_base_name.get(),
            update_base_type_flag=self.update_base_type.get(),
            update_tool_data_flag=self.update_tool_data.get(),
            update_tool_type_flag=self.update_tool_type.get(),
            update_tool_name_flag=self.update_tool_name.get(),
            update_load_data_flag=self.update_load_data.get(),
            update_e6axis_flag=self.update_e6axis.get(),
            e6axis_names=[name.strip() for name in self.e6axis_names.get().split(",")],
            modify_directly=self.modify_directly.get(),
            log_message=self.log_message_with_color
        )

        # Open the file if the option is selected
        if self.open_file_after_process.get():
            try:
                os.startfile(target_file)
            except Exception as e:
                self.log_message_with_color(f"Error opening file: {e}", level="ERROR")

    def log_message_with_color(self, message, level="INFO", bold=False):
        """
        Log a message to the log display with a specific color and optional bold formatting.

        Args:
            message (str): The message to log.
            level (str): The log level ("INFO", "ERROR", "WARNING").
            bold (bool): Whether to make the text bold.
        """
        self.log_display.config(state="normal")

        # Map log levels to colors
        colors = {
            "INFO": "green",
            "ERROR": "red",
            "WARNING": "orange"
        }
        color = colors.get(level, "black")  # Default to black if level is unknown

        # Add the log level prefix to the message
        formatted_message = f"[{level}] {message}\n"

        # Insert the message with the appropriate color and bold formatting
        tag_name = f"{level}_bold" if bold else level
        self.log_display.insert(tk.END, formatted_message, tag_name)
        self.log_display.tag_config(tag_name, foreground=color, font=("TkDefaultFont", 10, "bold" if bold else "normal"))

        self.log_display.config(state="disabled")
        self.log_display.see(tk.END)

        # Log to the file using the logger
        if level == "INFO":
            logger.info(message)
        elif level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)

    def animate_lights(self):
        # Animation logic for the lights
        self.lights_canvas.itemconfig(self.red_light, fill="gray")
        self.lights_canvas.itemconfig(self.orange_light, fill="gray")
        self.lights_canvas.itemconfig(self.green_light, fill="gray")

        if self.current_light == 0:
            self.lights_canvas.itemconfig(self.red_light, fill="red")
        elif self.current_light == 1:
            self.lights_canvas.itemconfig(self.orange_light, fill="orange")
        elif self.current_light == 2:
            self.lights_canvas.itemconfig(self.green_light, fill="green")

        self.current_light = (self.current_light + 1) % 3
        self.root.after(500, self.animate_lights)  # Change light every 500 ms