import os
import tkinter as tk
from tkinter import ttk, filedialog
from handlers.base_data_handler import update_base_data
from handlers.base_name_handler import update_base_name
from handlers.base_type_handler import update_base_type
from handlers.tool_data_handler import update_tool_data
from handlers.tool_type_handler import update_tool_type
from handlers.tool_name_handler import update_tool_name
from handlers.load_data_handler import update_load_data
from handlers.e6axis_handler import update_e6axis
from utils.file_utils import prepare_target_file


class PurgeFileView:
    def __init__(self, parent):
        """
        Initialize the Purge File tab view.
        """
        self.parent = parent

        # Initialize advanced options variables
        self.update_base_data = tk.BooleanVar(value=True)
        self.update_base_name = tk.BooleanVar(value=True)
        self.update_base_type = tk.BooleanVar(value=True)
        self.update_tool_data = tk.BooleanVar(value=True)
        self.update_tool_type = tk.BooleanVar(value=True)
        self.update_tool_name = tk.BooleanVar(value=True)
        self.update_load_data = tk.BooleanVar(value=True)
        self.update_e6axis = tk.BooleanVar(value=True)

        self.create_view()

    def create_view(self):
        """
        Create the UI for the Purge File tab.
        """
        # Left frame for file selection and controls
        left_frame = tk.Frame(self.parent)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Right frame for log display
        right_frame = tk.Frame(self.parent)
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

        # Target file selection
        self.target_label = tk.Label(left_frame, text="Target File:")
        self.target_label.pack(pady=5)
        self.target_entry = tk.Entry(left_frame, width=50)
        self.target_entry.pack(pady=5)
        self.target_button = tk.Button(left_frame, text="Browse", command=self.select_target_file)
        self.target_button.pack(pady=5)

        # Progress bar
        self.progress = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, orient="horizontal", length=400, mode="determinate", variable=self.progress)
        self.progress_bar.pack(pady=10)

        # Checkbox for opening file after purge
        self.open_file_after_purge = tk.BooleanVar(value=False)
        self.open_file_checkbox = tk.Checkbutton(left_frame, text="Open file after purge", variable=self.open_file_after_purge)
        self.open_file_checkbox.pack(pady=5)

        # Checkbox for modifying the file directly
        self.modify_directly = tk.BooleanVar(value=True)
        self.modify_directly_checkbox = tk.Checkbutton(left_frame, text="Modify target file directly", variable=self.modify_directly)
        self.modify_directly_checkbox.pack(pady=5)

        # Button to open advanced options
        self.advanced_options_button = tk.Button(left_frame, text="Advanced Options", command=self.open_advanced_options)
        self.advanced_options_button.pack(pady=5)

        # Start button
        self.start_button = tk.Button(left_frame, text="Purge File", command=self.purge_file)
        self.start_button.pack(pady=10)

        # Logger display in the right frame
        self.log_display = tk.Text(right_frame, width=70, height=30, state="disabled", wrap="word")
        self.log_display.pack(fill="both", expand=True)

        # Footer with version and author
        footer_label = tk.Label(left_frame, text="Ver 0.2\nCreated By Kacper Borowiec", font=("Arial", 8), fg="gray")
        footer_label.pack(side="bottom", pady=10)

    def select_target_file(self):
        """
        Open a file dialog to select the target file.
        """
        file_path = filedialog.askopenfilename(title="Select Target File")
        if file_path:
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, file_path)

    def open_advanced_options(self):
        """
        Open a new window for advanced options.
        """
        advanced_window = tk.Toplevel(self.parent)
        advanced_window.title("Advanced Options")
        advanced_window.geometry("400x400")

        # Checkboxes for handlers
        checkboxes = [
            ("Purge BASE_DATA", self.update_base_data),
            ("Purge BASE_NAME", self.update_base_name),
            ("Purge BASE_TYPE", self.update_base_type),
            ("Purge TOOL_DATA", self.update_tool_data),
            ("Purge TOOL_TYPE", self.update_tool_type),
            ("Purge TOOL_NAME", self.update_tool_name),
            ("Purge LOAD_DATA", self.update_load_data),
            ("Purge E6AXIS", self.update_e6axis),
        ]

        for text, var in checkboxes:
            tk.Checkbutton(advanced_window, text=text, variable=var).pack(anchor="w", pady=2)

        # Button to uncheck all checkboxes
        def uncheck_all():
            for _, var in checkboxes:
                var.set(False)

        uncheck_button = tk.Button(advanced_window, text="Uncheck All", command=uncheck_all)
        uncheck_button.pack(pady=10)

        # Close button
        close_button = tk.Button(advanced_window, text="Close", command=advanced_window.destroy)
        close_button.pack(pady=10)

    def purge_file(self):
        """
        Purge the selected file by setting all values to 0.0.
        """
        target_file = self.target_entry.get()
        if not target_file:
            self.log_message("Please select a target file.", level="ERROR")
            return

        self.log_message(f"Purging file: {target_file}", level="INFO")

        try:
            # Prepare the target file
            target_file = prepare_target_file(target_file, self.modify_directly.get(), self.log_message)

            # Read the target file
            with open(target_file, 'r') as file:
                target_content = file.readlines()

            # Process each handler based on the selected options
            handlers = [
                (update_base_data, self.update_base_data.get()),
                (update_base_name, self.update_base_name.get()),
                (update_base_type, self.update_base_type.get()),
                (update_tool_data, self.update_tool_data.get()),
                (update_tool_type, self.update_tool_type.get()),
                (update_tool_name, self.update_tool_name.get()),
                (update_load_data, self.update_load_data.get()),
                (update_e6axis, self.update_e6axis.get())
            ]

            for handler, enabled in handlers:
                if enabled:
                    handler([], target_content, self.log_message, purge_mode=True)

            # Write the updated content back to the file
            with open(target_file, 'w') as file:
                file.writelines(target_content)

            self.log_message("Purge process completed successfully!", level="INFO")

            # Open the file if the option is selected
            if self.open_file_after_purge.get():
                os.startfile(target_file)

        except Exception as e:
            self.log_message(f"Error during purge: {e}", level="ERROR")

    def log_message(self, message, level="INFO"):
        """
        Log a message to the log display.
        """
        self.log_display.config(state="normal")
        self.log_display.insert(tk.END, f"[{level}] {message}\n")
        self.log_display.config(state="disabled")
        self.log_display.see(tk.END)

    def animate_lights(self):
        """
        Animate the lights (red, orange, green) in sequence.
        """
        # Reset all lights to gray
        self.lights_canvas.itemconfig(self.red_light, fill="gray")
        self.lights_canvas.itemconfig(self.orange_light, fill="gray")
        self.lights_canvas.itemconfig(self.green_light, fill="gray")

        # Turn on the current light
        if self.current_light == 0:
            self.lights_canvas.itemconfig(self.red_light, fill="red")
        elif self.current_light == 1:
            self.lights_canvas.itemconfig(self.orange_light, fill="orange")
        elif self.current_light == 2:
            self.lights_canvas.itemconfig(self.green_light, fill="green")

        # Move to the next light
        self.current_light = (self.current_light + 1) % 3

        # Schedule the next animation step
        self.parent.after(500, self.animate_lights)