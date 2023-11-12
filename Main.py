import tkinter as tk
from tkinter import filedialog
from Login import Login
class FTPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Transfer Protocol")
        root.geometry("600x500")
 
 
        # Disconnect Button
        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect)
        self.disconnect_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

        # Left Panel
        self.left_frame = tk.Frame(root, padx=10, pady=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.upload_label = tk.Label(self.left_frame, text="Please choose the file to upload")
        self.upload_label.pack(pady=10)

        self.upload_scrollbar = tk.Scrollbar(self.left_frame, orient=tk.VERTICAL)
        self.upload_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.upload_listbox = tk.Listbox(self.left_frame, selectmode=tk.SINGLE, yscrollcommand=self.upload_scrollbar.set)
        self.upload_listbox.pack(expand=True, fill=tk.BOTH)

        self.upload_scrollbar.config(command=self.upload_listbox.yview)

        self.upload_button = tk.Button(self.left_frame, text="Upload", command=self.upload_file)
        self.upload_button.pack(pady=10)

        # Right Panel
        self.right_frame = tk.Frame(root, padx=10, pady=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.download_label = tk.Label(self.right_frame, text="Please select the file to download")
        self.download_label.pack(pady=10)

        self.download_scrollbar = tk.Scrollbar(self.right_frame, orient=tk.VERTICAL)
        self.download_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.download_listbox = tk.Listbox(self.right_frame, selectmode=tk.SINGLE, yscrollcommand=self.download_scrollbar.set)
        self.download_listbox.pack(expand=True, fill=tk.BOTH)

        self.download_scrollbar.config(command=self.download_listbox.yview)

        self.download_button = tk.Button(self.right_frame, text="Download", command=self.download_file)
        self.download_button.pack(pady=10)

    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_listbox.insert(tk.END, file_path)

    def download_file(self):
        selected_index = self.download_listbox.curselection()
        if selected_index:
            selected_file = self.download_listbox.get(selected_index)
            # Add your download logic here using the selected_file path

    def disconnect(self):
        
        self.root.destroy()
        new_root = tk.Tk()
        new_app = Login(new_root)
        new_root.mainloop()



if __name__ == "__main__":
    root = tk.Tk()
    app = FTPApp(root)
    root.mainloop()
