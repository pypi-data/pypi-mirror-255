from tkinter import *
import os
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class Automation:
    def __init__(self, root):
        self.root = root
        self.root.title("AIUTGen")
        self.root.geometry("1020x500")

        self.filetreeview = ttk.Treeview(self.root, show='tree')
        self.filetreeview.place(x=7, y=180, width=180)
        self.filetreeview.bind("<ButtonRelease-1>", self.on_treeview_select) 
        self.filetreeview.bind("<Button-3>", self.show_context_menu)  # Bind right-click event

        btnload = ttk.Button(self.root, command=self.open_file_dialog, text="Select Source", width=20, compound=tk.LEFT)
        btnload.place(x=40, y=120)

        global lblFunction
        lblFunction = ttk.Label(self.root, text="Source Code", foreground="blue")
        lblFunction.place(x=200, y=190)

        self.function = Text(self.root, font=("MS Sans Serif", 10), width=55, height=15)
        self.function.place(x=200, y=210)

        self.image_dict = {
            ".java": "java.png",
            ".cs": "cs.png",
            ".py": "py.png",
            ".dir": "folder_icon.png",
            # Add more file extensions and corresponding image paths as needed
        }
        self.load_images()

    def load_images(self):
        self.image_dict = {ext: Image.open(path).resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC) for ext, path in self.image_dict.items()}
        self.image_dict = {ext: ImageTk.PhotoImage(image) for ext, image in self.image_dict.items()}

        # Load folder icon separately
        folder_icon_path = "folder_icon.png"
        self.dir_image = Image.open(folder_icon_path).resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        self.dir_image = ImageTk.PhotoImage(self.dir_image)
    def new_folder(self, parent_path, directory_entries, parent_iid, d_image):
        for name in directory_entries:
            item_path = os.path.join(parent_path, name)
            if os.path.isdir(item_path):
                subdir_iid = self.filetreeview.insert(parent=parent_iid, index='end',
                                         text=name,
                                         image=d_image)
                try:
                    subdir_entries = os.listdir(item_path)
                    self.new_folder(parent_path=item_path,
                           directory_entries=subdir_entries,
                           parent_iid=subdir_iid,
                           d_image=d_image)
                except PermissionError:
                    pass
            else:
                file_extension = os.path.splitext(name)[1].lower()
                file_image = self.get_file_image(file_extension)
                self.filetreeview.insert(parent=parent_iid,
                            index='end',
                            text=name,
                            image=file_image)

    def get_file_image(self, file_extension):
        # Helper method to get the image based on the file extension
        return self.image_dict.get(file_extension, self.dir_image)

    def on_treeview_select(self, event):
        print("inside on_treeview_select")
        item = self.filetreeview.selection()[0]
        item_text = self.filetreeview.item(item, "text")
        item_path = os.path.join(self.get_folder_path(item), item_text)
        print(item_path)
        if os.path.isfile(item_path):
            with open(item_path, 'r') as file:
                content = file.read()
                self.function.delete("1.0", "end")
                self.function.insert("end", content)

    def get_folder_path(self, item):
        # Helper method to get the folder path of an item in the treeview
        print("inside get_folder_path")
        parent = self.filetreeview.parent(item)
        if parent == '':
            return ""
        else:
            return os.path.join(self.get_folder_path(parent), self.filetreeview.item(parent, "text"))


    def open_file_dialog(self):
        src_folder_path = filedialog.askdirectory(title="Select the Source Code Location")
        start_path = os.path.expanduser(src_folder_path)
        start_path = os.path.expanduser(src_folder_path)
        start_dir_entries = os.listdir(start_path)
        parent_iid = self.filetreeview.insert(parent='',
                             index='0',
                             text=src_folder_path,
                             open=True,
                             image=self.dir_image)
        self.new_folder(parent_path=start_path,
           directory_entries=start_dir_entries,
           parent_iid=parent_iid,
           d_image=self.dir_image)

    def show_context_menu(self, event):
        # Display context menu when right-clicking on an item in the treeview
        item = self.filetreeview.selection()[0]
        item_text = self.filetreeview.item(item, "text")
        item_path = os.path.join(self.get_folder_path(item), item_text)

        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="Generate Test Case", command=lambda: self.generate_test_case_handler(item_path))
        menu.post(event.x_root, event.y_root)

    def generate_test_case_handler(self, file_path):
        # Placeholder for the actual test case generation code
        print(f"Generate Test Case for: {file_path}")

if __name__ == "__main__":
    root = Tk()
    obj = Automation(root)
    root.mainloop()
