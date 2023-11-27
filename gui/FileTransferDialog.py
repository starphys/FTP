import tkinter as tk

class FileTransferDialog(tk.Toplevel):
    def __init__(self, parent, title, file_path, is_upload=True):
        super().__init__(parent)
        self.title(title)

        self.file_path = file_path
        self.is_upload = is_upload
        self.transfer_action = 'overwrite'

        tk.Label(self, text=f"Path: {self.file_path}").pack(padx=10, pady=5)

        self.destination_var = tk.StringVar()
        tk.Entry(self, textvariable=self.destination_var).pack(padx=10, pady=5)

        if is_upload:
            tk.Button(self, text="Append and Upload", command=lambda: self.set_action("append")).pack(side=tk.LEFT, padx=10, pady=10)
            tk.Button(self, text="Overwrite and Upload", command=lambda: self.set_action("overwrite")).pack(side=tk.RIGHT, padx=10, pady=10)
        else:
            tk.Button(self, text="Download", command=lambda: self.set_action("overwrite")).pack(side=tk.RIGHT, padx=10, pady=10)

        self.grab_set()

    def set_action(self, action):
        self.transfer_action = action
        self.destination_var.set(self.destination_var.get().strip())
        self.destroy()

    def show(self):
        self.wait_window()  # Wait for the user to close the dialog
        return self.transfer_action, self.destination_var.get()