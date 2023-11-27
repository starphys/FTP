import os
import tkinter as tk
from tkinter import filedialog, ttk
class MainView(tk.Frame):
    def __init__(self, parent, controller, on_disconnect):
        super().__init__(parent)
        self.controller = controller
        self.on_disconnect = on_disconnect
        self.local_path = os.path.expanduser('~')
        self.remote_path = '.'

        self.folder_icon = tk.PhotoImage(file='./icons/directory.png')
        self.file_icon = tk.PhotoImage(file='./icons/file.png')

        # Disconnect Button
        self.disconnect_button = tk.Button(self, text='Disconnect', command=self.disconnect)
        self.disconnect_button.pack(side=tk.TOP, anchor=tk.NE, padx=10, pady=10)

        # Left Panel for Local File System
        self.local_frame = tk.Frame(self, padx=10, pady=10)
        self.local_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.local_treeview = self.setup_treeview(self.local_frame, 'Local Files')
        self.local_treeview.bind('<Double-1>', self.on_local_double_click)

        self.display_local_files()

        # Right Panel for Remote File System
        self.remote_frame = tk.Frame(self, padx=10, pady=10)
        self.remote_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.remote_treeview = self.setup_treeview(self.remote_frame, 'Remote Files')
        self.remote_treeview.bind('<Double-1>', self.on_remote_double_click)

    def setup_treeview(self, parent, label_text):
        label = tk.Label(parent, text=label_text)
        label.pack(pady=10)

        treeview = ttk.Treeview(parent)
        treeview.pack(expand=True, fill=tk.BOTH)

        # Define columns
        treeview['columns'] = ('Name',)
        treeview.column('#0', width=50, stretch=tk.NO)
        treeview.column('Name', anchor=tk.W)

        treeview.heading('#0', text='', anchor=tk.W)
        treeview.heading('Name', text='Name', anchor=tk.W)

        return treeview
    
    def display_local_files(self):
        # Clear existing entries in the local file list
        self.local_treeview.delete(*self.local_treeview.get_children())
        
        # Add the '..' folder for navigation
        self.local_treeview.insert('', 'end', text='', values=('..','directory'), image=self.folder_icon)

        # Lists for storing directories and files
        directories = []
        files = []

        # Iterate over items in the directory
        for entry in os.listdir(self.local_path):
            full_path = os.path.join(self.local_path, entry)
            if os.path.isdir(full_path):
                directories.append(entry)
            else:
                files.append(entry)

        # Sort directories and files
        directories.sort()
        files.sort()

        # Insert sorted directories and files into the treeview
        for directory in directories:
            self.local_treeview.insert('', 'end', text='', values=(directory,'directory'), image=self.folder_icon)

        for file in files:
            self.local_treeview.insert('', 'end', text='', values=(file,'file'), image=self.file_icon)

    def update_remote_files(self, remote_data):
        # Clear existing entries in the remote file list
        self.remote_treeview.delete(*self.remote_treeview.get_children())

        directories = []
        files = []

        # Process response line by line
        lines = remote_data.split('\n')
        print(lines)
        for line in lines:
            parts = line.strip().split()
            # Skip improper lines
            if len(parts) < 9:
                continue
            
            name = ' '.join(parts[8:])
            if name == '.':
                continue
            if parts[0].startswith('d'):
                directories.append(name)
            else:
                files.append(name)

        # Sort directories and files
        directories.sort()
        files.sort()

        # Insert sorted directories and files into the treeview
        for directory in directories:
            self.remote_treeview.insert('', 'end', text='', values=(directory,'directory'), image=self.folder_icon)

        for file in files:
            self.remote_treeview.insert('', 'end', text='', values=(file,'file'), image=self.file_icon)
    
    def on_local_double_click(self, event):
        item = self.local_treeview.selection()[0]
        name, item_type = self.local_treeview.item(item, 'values')
        if name == "..":
            self.local_path = os.path.dirname(self.local_path)
        elif item_type == 'directory':
            self.local_path = os.path.join(self.local_path, name)
        else:
            # TODO: File double click, most likely upload
            pass
        self.display_local_files()

    def on_remote_double_click(self, event):
        item = self.remote_treeview.selection()[0]
        name, item_type = self.remote_treeview.item(item, 'values')
        print(name, item_type)
        if item_type == 'directory':
            self.controller.set_remote_directory(name)
        else:
            # TODO: File double click, most likely download
            pass


    def upload_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.upload_listbox.insert(tk.END, file_path)

    def download_file(self):
        selected_index = self.download_listbox.curselection()
        if selected_index:
            selected_file = self.download_listbox.get(selected_index)

    def disconnect(self):
        self.on_disconnect()