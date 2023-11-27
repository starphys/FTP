from .FileTransferDialog import FileTransferDialog
import os
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
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

        # Local treeview context menus
        self.local_item_menu = tk.Menu(self, tearoff=0)
        self.local_item_menu.add_command(label="Rename", command=self.rename_local_item)
        self.local_item_menu.add_command(label="Delete", command=self.delete_local_item)
        
        self.local_empty_menu = tk.Menu(self, tearoff=0)
        self.local_empty_menu.add_command(label="Add Directory", command=self.add_local_directory)

        # Remote treeview context menus
        self.remote_item_menu = tk.Menu(self, tearoff=0)
        self.remote_item_menu.add_command(label="Rename", command=self.rename_remote_item)
        self.remote_item_menu.add_command(label="Delete", command=self.delete_remote_item)
        
        self.remote_empty_menu = tk.Menu(self, tearoff=0)
        self.remote_empty_menu.add_command(label="Add Directory", command=self.add_remote_directory)

        # Bind right-click event (cross platform)
        self.local_treeview.bind("<Button-3>", self.on_local_treeview_right_click)
        self.local_treeview.bind("<Button-2>", self.on_local_treeview_right_click)

        self.remote_treeview.bind("<Button-3>", self.on_remote_treeview_right_click)
        self.remote_treeview.bind("<Button-2>", self.on_remote_treeview_right_click)


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
            self.controller.set_local_directory(self.local_path)
        elif item_type == 'directory':
            self.local_path = os.path.join(self.local_path, name)
            self.controller.set_local_directory(self.local_path)
        else:
            self.upload_file(name)
        self.display_local_files()

    def on_remote_double_click(self, event):
        item = self.remote_treeview.selection()[0]
        name, item_type = self.remote_treeview.item(item, 'values')
        if item_type == 'directory':
            self.controller.set_remote_directory(name)
        else:
            self.download_file(name)

    def on_local_treeview_right_click(self, event):
        item_id = self.local_treeview.identify_row(event.y)
        if item_id:
            self.local_treeview.selection_set(item_id)
            item_name, item_type = self.local_treeview.item(item_id, 'values')
            if item_name == '..':
                return
            self.configure_menu(self.local_item_menu, item_type)
            self.local_item_menu.post(event.x_root, event.y_root)
        else:
            self.local_empty_menu.post(event.x_root, event.y_root)

    def on_remote_treeview_right_click(self, event):
        item_id = self.remote_treeview.identify_row(event.y)
        if item_id:
            self.remote_treeview.selection_set(item_id)
            item_name, item_type = self.remote_treeview.item(item_id, 'values')
            if item_name == '..':
                return
            self.configure_menu(self.remote_item_menu, item_type)
            self.remote_item_menu.post(event.x_root, event.y_root)
        else:
            self.remote_empty_menu.post(event.x_root, event.y_root)

    def delete_local_item(self):
        # Get the selected item
        selected_item = self.local_treeview.selection()

        # Check if an item is actually selected
        if selected_item:
            item_name = self.local_treeview.item(selected_item[0], 'values')[0]
            confirmation = tk.messagebox.askyesno("Delete", f"Are you sure you want to delete '{item_name}'?")
            if confirmation:
                self.controller.delete_local_item(self.local_path, item_name)

    def rename_local_item(self):
        selected_item = self.local_treeview.selection()
        if selected_item:
            old_name = self.local_treeview.item(selected_item[0], 'values')[0]
            new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
            if new_name and new_name != old_name:
                self.controller.rename_local_file(self.local_path, old_name, new_name)

    def add_local_directory(self):
        new_dir_name = simpledialog.askstring("New Directory", "Enter name for new directory:")
        if new_dir_name:
            self.controller.create_local_directory(self.local_path, new_dir_name)

    def delete_remote_item(self):
        # Get the selected item
        selected_item = self.remote_treeview.selection()

        # Check if an item is actually selected
        if selected_item:
            item_name, item_type = self.remote_treeview.item(selected_item[0], 'values')
            confirmation = tk.messagebox.askyesno("Delete", f"Are you sure you want to delete '{item_name}'?")
            if confirmation:
                if item_type == 'directory':
                    self.controller.delete_remote_directory(item_name)
                else:
                    self.controller.delete_remote_file(item_name)

    def rename_remote_item(self):
        selected_item = self.remote_treeview.selection()
        if selected_item:
            old_name = self.remote_treeview.item(selected_item[0], 'values')[0]
            new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
            if new_name and new_name != old_name:
                self.controller.rename_remote_file(old_name, new_name)

    def add_remote_directory(self):
        new_dir_name = simpledialog.askstring("New Directory", "Enter name for new directory:")
        if new_dir_name:
            self.controller.create_remote_directory(new_dir_name)

    def configure_menu(self, menu, item_type):
        if item_type == 'file':
            menu.entryconfig("Rename", state="normal")
        else:
            menu.entryconfig("Rename", state="disabled")

    def upload_file(self, file_name):
        file_path = os.path.join(self.local_path, file_name)
        dialog = FileTransferDialog(self, "Upload File", file_path, is_upload=True)
        action, destination_name = dialog.show()
        if action:
            destination_name = destination_name if destination_name != '' else file_name
            self.controller.upload_file(file_path, destination_name, action)

    def download_file(self, file_name):
        file_path = os.path.join(self.remote_path.strip(), file_name)
        dialog = FileTransferDialog(self, "Download File", file_path, is_upload=False)
        action, destination_name = dialog.show()
        if action:
            destination_name = destination_name if destination_name != '' else file_name
            self.controller.download_file(file_name, destination_name)

    def disconnect(self):
        self.on_disconnect()