import tkinter as tk
from ui import FileTransferApp

if __name__ == "__main__":
    root = tk.Tk()
    app = FileTransferApp(root)
    root.mainloop()